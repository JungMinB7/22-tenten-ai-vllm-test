class YoutubeSummaryPrompt:
    def create_user_prompt(self, youtube_transcript: str) -> str:
        return f"""아래 텍스트를 한국어로 3개의 핵심 포인트로 요약해주세요.
                            각 포인트는 '•' 기호로 시작하고, 한 문장으로 작성해주세요.

                            텍스트:
                            {youtube_transcript}

                            요약 형식:
                            • [첫 번째 핵심 포인트]
                            • [두 번째 핵심 포인트]
                            • [세 번째 핵심 포인트]"""

    def create_messages(self, youtube_transcript: str) -> list:
        return [
            {"role": "system", "content": "너는 아주 친절한 AI 어시스턴트야. 너의 목표는 주어진 텍스트를 한국어로 3개의 핵심 포인트로 요약하는 것이야."},
            {"role": "user", "content": self.create_user_prompt(youtube_transcript)}
        ]
