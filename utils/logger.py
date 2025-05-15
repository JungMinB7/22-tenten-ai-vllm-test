import os
from langfuse import Langfuse
from datetime import datetime, timezone

# Langfuse 인스턴스 싱글턴 생성 (환경변수에서 키/호스트 자동 로드)
langfuse = Langfuse()

def log_inference_to_langfuse(
    trace=None,
    name="vllm-inference",
    prompt=None,
    messages=None,
    text_prompt=None,
    content=None,
    model_name=None,
    model_parameters=None,
    input_tokens=None,
    output_tokens=None,
    inference_time=None,
    start_time=None,
    end_time=None,
    error=None
):
    """
    LLM 인퍼런스 결과(성공/에러 포함)를 Langfuse에 기록
    """
    now = datetime.now(timezone.utc)
    safe_start_time = start_time or now
    safe_end_time = end_time or now
    safe_prompt = prompt or ""
    safe_name = name or "vllm-inference"
    safe_input = {"messages": messages, "text_prompt": text_prompt}
    safe_output = {"content": content} if content is not None else None
    safe_usage = None
    if input_tokens is not None and output_tokens is not None:
        safe_usage = {
            "promptTokens": input_tokens,
            "completionTokens": output_tokens,
            "totalTokens": input_tokens + output_tokens,
        }
    safe_metadata = {"inference_time": inference_time} if inference_time is not None else {}

    try:
        if trace:
            trace.generation(
                name=safe_name,
                prompt=safe_prompt,
                input=safe_input,
                output=safe_output,
                model=model_name,
                model_parameters=model_parameters,
                usage=safe_usage,
                metadata=safe_metadata,
                start_time=safe_start_time,
                end_time=safe_end_time,
                error=error
            )
        else:
            langfuse.generation(
                name=safe_name,
                prompt=safe_prompt,
                input=safe_input,
                output=safe_output,
                model=model_name,
                model_parameters=model_parameters,
                usage=safe_usage,
                metadata=safe_metadata,
                start_time=safe_start_time,
                end_time=safe_end_time,
                error=error
            )
    except Exception as gen_err:
        print(f"[Langfuse logging error] {gen_err}")
        import traceback
        print(traceback.format_exc())
