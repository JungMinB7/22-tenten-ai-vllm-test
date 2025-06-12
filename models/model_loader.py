import requests
import os, time
from dotenv import load_dotenv
import logging
from utils.logger import log_inference_to_langfuse

from openai import OpenAI

class ModelLoader:
    def __init__(self, mode="colab"):
        self.mode = mode

        if self.mode == "gcp" or self.mode == "colab":
            self.model_path = "allganize/Llama-3-Alpha-Ko-8B-Instruct"
        elif self.mode == "api-dev" or self.mode == "api-prod":
            self.model_path = "models/gemini-2.0-flash"

        # colab/ngrok API 요청에 필요한 헤더 및 데이터
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy-key"  
        }
        
        self.temperature = 0.5
        self.top_p = 0.5
        self.max_tokens = 256
        self.stop = ["\n\n", "</s>"]

        if self.mode == "colab":
            self.data = {
                "model": self.model_path ,
                "messages": [],
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "stop": self.stop
            }
        # GCP(vllm) 모드일 때만 vllm 엔진 초기화
        if self.mode == "gcp":
            from vllm import LLM, SamplingParams

            self.model_vllm = LLM(
                model=self.model_path ,
                dtype="half", # 또는 torch.bfloat16, torch.float16 등. torch.bfloat16은 최신 GPU(Ampere 이상)에서만 지원됨.
                trust_remote_code=True,
                tensor_parallel_size=1,
                max_model_len=8192,
                gpu_memory_utilization=0.9,
                max_num_seqs=5,
                max_num_batched_tokens=2048
            )

            self.sampling_params = SamplingParams(
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                stop=self.stop 
            )
        if self.mode == "api-dev" or self.mode == "api-prod":
            if self.mode == "api-prod":
                load_dotenv(dotenv_path='/secrets/env')
            else:
                load_dotenv(override=True)

            self.client = OpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            

    def get_response(self, messages, trace, start_time=None, prompt=None, name="vllm-inference"):
        if self.mode == "colab":
            # Ngrok(Colab) API로 요청
            load_dotenv(override=True)
            base_url = os.getenv('MODEL_NGROK_URL')

            self.data["messages"] = messages
            url = f"{base_url}/v1/chat/completions"

            start_time = time.time()
            response = requests.post(url, headers=self.headers, json=self.data)
            end_time = time.time()
            print(f"response time : {(end_time - start_time):.3f}")

            if response.status_code != 200:
                try:
                    error_body = response.json()
                except ValueError:
                    error_body = response.text
                return {
                    "status_code": response.status_code,
                    "url": response.url,
                    "headers": dict(response.headers),
                    "error": error_body
                }
            body = response.json()
            return {
                "status_code": response.status_code,
                "url": response.url,
                "content": body["choices"][0]["message"]["content"]
            }
        else:
            '''
            vllm 엔진을 통한 직접 추론
            '''
            if self.mode == "gcp":
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained(self.model_path)

                # messages -> 텍스트로 변환
                prompt = tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,  # 마지막에 assistant 응답 위치를 표시해줌
                    tokenize=False               # string 그대로 받기
                )

            start_time = time.time()

            try:
                if self.mode == "gcp":
                    outputs = self.model_vllm.generate(prompt, self.sampling_params)
                    content = outputs[0].outputs[0].text

                    output_token_ids = outputs[0].outputs[0].token_ids
                    output_tokens = len(output_token_ids)
                    input_tokens = len(tokenizer(prompt)["input_ids"])

                elif self.mode == "api-dev" or self.mode == "api-prod":
                    response = self.client.chat.completions.create(
                        model=self.model_path, 
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        stop=self.stop
                    )

                    content = response.choices[0].message.content

                    input_tokens = output_tokens = None

                end_time = time.time()
                inference_time = end_time - start_time

                log_model_parameters= {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "max_tokens": self.max_tokens,
                        "stop": self.stop,
                        "dtype": "half",
                        "tensor_parallel_size": 1,
                        "max_model_len": 8192,
                        "gpu_memory_utilization": 0.9,
                        "max_num_seqs": 5,
                        "max_num_batched_tokens": 2048,
                    }
                if self.mode == "api-dev" or self.mode == "api-prod":
                    log_model_parameters = {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "max_tokens": self.max_tokens,
                        "stop": self.stop,
                        }

                log_inference_to_langfuse(
                    trace=trace,
                    name=name,
                    prompt=prompt,
                    messages=messages,
                    content=content,
                    model_name=self.model_path,
                    model_parameters=log_model_parameters,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    inference_time=inference_time,
                    start_time=start_time,
                    end_time=end_time,
                    error=None
                )
            except Exception as e:
                import traceback
                error_info = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                from datetime import datetime
                gen_end = datetime.now()
                log_inference_to_langfuse(
                    trace=trace,
                    name=name,
                    prompt=prompt,
                    messages=messages,
                    content=None,
                    model_name=self.model_path,
                    model_parameters={
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "max_tokens": self.max_tokens,
                        "stop": self.stop,
                        "dtype": "half",
                        "tensor_parallel_size": 1,
                        "max_model_len": 8192,
                        "gpu_memory_utilization": 0.9,
                        "max_num_seqs": 5,
                        "max_num_batched_tokens": 2048,
                    },
                    input_tokens=0,
                    output_tokens=0,
                    inference_time=0.0,
                    start_time=start_time,
                    end_time=gen_end,
                    error=error_info
                )
                print(f"ChatCompletion error: {e}")
                return {
                    "status_code": 500,
                    "url": "local_vllm",
                    "error": str(e)
                }

            print(f"response time : {inference_time:.3f} sec")

            return {
                "status_code": 200,
                "url": "local_vllm",
                "content": content
            }