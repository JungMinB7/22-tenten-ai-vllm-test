import requests
import os, time
from dotenv import load_dotenv
from utils.logger import log_inference_to_langfuse

from openai import OpenAI
from abc import ABC, abstractmethod

class BaseModelLoader(ABC):
    @abstractmethod
    def get_response(self, messages, trace, start_time=None, prompt=None, name="vllm-inference"):
        pass

class ColabModelLoader(BaseModelLoader):
    def __init__(self, model_path, temperature, top_p, max_tokens, stop, headers):
        self.model_path = model_path
        self.headers = headers
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.stop = stop
        self.data = {
            "model": self.model_path,
            "messages": [],
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "stop": self.stop
        }

    def get_response(self, messages, trace, start_time=None, prompt=None, name="colab-inference"):
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


class GCPModelLoader(BaseModelLoader):
    def __init__(self, model_path, temperature, top_p, max_tokens, stop, tensor_parallel_size, max_model_len, gpu_memory_utilization, max_num_seqs, max_num_batched_tokens):
        from vllm import LLM, SamplingParams
        from transformers import AutoTokenizer

        self.model_path = model_path
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.stop = stop

        self.model_vllm = LLM(
            model=self.model_path,
            dtype="half",
            trust_remote_code=True,
            tensor_parallel_size=tensor_parallel_size,
            max_model_len=max_model_len,
            gpu_memory_utilization=gpu_memory_utilization,
            max_num_seqs=max_num_seqs,
            max_num_batched_tokens=max_num_batched_tokens
        )

        self.sampling_params = SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            stop=self.stop
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

    def get_response(self, messages, trace, start_time=None, prompt=None, name="vllm-inference"):
        prompt = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False
        )

        start_time = time.time()

        try:
            outputs = self.model_vllm.generate(prompt, self.sampling_params)
            content = outputs[0].outputs[0].text

            output_token_ids = outputs[0].outputs[0].token_ids
            output_tokens = len(output_token_ids)
            input_tokens = len(self.tokenizer(prompt)["input_ids"])

            end_time = time.time()
            inference_time = end_time - start_time

            log_model_parameters = {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "stop": self.stop,
                "dtype": "half",
                "tensor_parallel_size": self.model_vllm.tensor_parallel_size,
                "max_model_len": self.model_vllm.max_model_len,
                "gpu_memory_utilization": self.model_vllm.gpu_memory_utilization,
                "max_num_seqs": self.model_vllm.max_num_seqs,
                "max_num_batched_tokens": self.model_vllm.max_num_batched_tokens,
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
                    "tensor_parallel_size": self.model_vllm.tensor_parallel_size,
                    "max_model_len": self.model_vllm.max_model_len,
                    "gpu_memory_utilization": self.model_vllm.gpu_memory_utilization,
                    "max_num_seqs": self.model_vllm.max_num_seqs,
                    "max_num_batched_tokens": self.model_vllm.max_num_batched_tokens,
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


class GeminiAPILoader(BaseModelLoader):
    def __init__(self, mode, model_path, temperature, top_p, max_tokens, stop, base_url):
        self.mode = mode
        self.model_path = model_path
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.stop = stop

        if self.mode == "api-prod":
            load_dotenv(dotenv_path='/secrets/env')
        else:
            load_dotenv(override=True)

        self.client = OpenAI(
            api_key= os.getenv("GEMINI_API_KEY"),
            base_url=base_url
        )

    def get_response(self, messages, trace, start_time=None, prompt=None, name="api-inference"):
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_path,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=self.stop
            )

            print(f"DEBUG: response: {response}")

            content = response.choices[0].message.content

            print(f"DEBUG: content: {content}")

            input_tokens = output_tokens = None

            end_time = time.time()
            inference_time = end_time - start_time

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
                "url": "local_api",
                "error": str(e)
            }

        print(f"response time : {inference_time:.3f} sec")

        return {
            "status_code": 200,
            "url": "local_api",
            "content": content
        }


class ModelLoader:
    def __init__(self, mode="colab"):
        self.mode = mode
        self.loader = None
        if mode == "colab":
            self.loader = ColabModelLoader(
                model_path="allganize/Llama-3-Alpha-Ko-8B-Instruct",
                temperature=0.5,
                top_p=0.5,
                max_tokens=256,
                stop=["\n\n", "</s>"],
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer dummy-key"
                }
            )
        elif mode == "gcp":
            self.loader = GCPModelLoader(
                model_path="allganize/Llama-3-Alpha-Ko-8B-Instruct",
                temperature=0.5,
                top_p=0.5,
                max_tokens=256,
                stop=["\n\n", "</s>"],
                tensor_parallel_size=1,
                max_model_len=8192,
                gpu_memory_utilization=0.9,
                max_num_seqs=5,
                max_num_batched_tokens=2048
            )
        elif mode == "api-dev" or mode == "api-prod":
            print("ModelLoader init")
            self.loader = GeminiAPILoader(
                mode=mode,
                model_path="models/gemini-2.0-flash",
                temperature=0.5,
                top_p=0.5,
                max_tokens=256,
                stop=["\n"],
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def get_response(self, messages, trace, start_time=None, prompt=None, name="inference"):
        if self.loader:
            return self.loader.get_response(messages, trace, start_time, prompt, name)
        else:
            raise RuntimeError("Model loader not initialized.")