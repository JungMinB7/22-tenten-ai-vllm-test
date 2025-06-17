from dotenv import load_dotenv
import os
from langfuse import Langfuse

class YoutubeSummaryPrompt:
    def __init__(self, mode:str):
        """
        Args:
            mode : colab(default) / gcp
        """

        if os.environ.get("LLM_MODE") == "api-prod":
            load_dotenv(dotenv_path='/secrets/env')
        else:
            load_dotenv(override=True)

        # Langfuse 초기화
        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST')
        )

        # 프롬프트 가져오기
        if mode == "gcp":
            label="production"
        else : 
            label="latest"

        # 청크별 요약용
        self.chunk_prompt = self.langfuse.get_prompt(
            name="posts_youtube_chunk_summary",
            label=label,
            type="chat"
        )
        # 최종 통합 요약용
        self.final_prompt = self.langfuse.get_prompt(
            name="posts_youtube_final_summary",
            label=label,
            type="chat"
        )

    def create_chunk_messages(self, chunk, position, prev_summary=None):
        vars = {"text_chunk": chunk, "position": position, "prev_summary": prev_summary}
        return self.chunk_prompt, self.chunk_prompt.compile(**vars)

    def create_final_messages(self, chunk_summaries: list):
        joined = "\n".join(f"청크 {i+1} 요약:\n{s}\n" for i, s in enumerate(chunk_summaries))
        vars = {"chunk_summaries": joined}
        return self.final_prompt, self.final_prompt.compile(**vars)