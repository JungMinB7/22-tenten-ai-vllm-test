class YoutubeSummaryPrompt:
    def create_user_prompt(self, youtube_transcript: str) -> str:
        return f"""아래 텍스트를 읽고, 가장 중요한 핵심 내용을 3가지로 요약해 주세요.
- 각 요약은 한 문장으로 간결하게 작성해 주세요.
- 불필요한 설명 없이 요약만 반환해 주세요.
- 각 요약 앞에 1., 2., 3. 번호를 붙여 주세요.

[텍스트]
{youtube_transcript}

[요약 예시]
1. 첫 번째 핵심 요약
2. 두 번째 핵심 요약
3. 세 번째 핵심 요약
"""

    def create_messages(self, chunk: str, position: str, prev_summary: str = None) -> list:
        system_msg = f"너는 아주 친절한 AI 어시스턴트야. 아래 텍스트는 {position}에 해당하는 부분이야. 이 부분을 한국어로 3개의 핵심 포인트로 요약해줘. 각 요약은 한 문장으로 간결하게 작성하고, 반드시 요약만 반환해."
        if prev_summary:
            system_msg += f" 반드시 이전 청크의 요약도 참고해서 문맥을 반영해 요약을 생성해야 해. 이전 청크의 요약은 다음과 같아: {prev_summary}"
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": self.create_user_prompt(chunk)}
        ]
