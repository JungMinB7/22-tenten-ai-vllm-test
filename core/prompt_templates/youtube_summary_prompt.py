class YoutubeSummaryPrompt:
    def create_user_prompt(self, youtube_transcript: str) -> str:
        """
        유튜브 자막 텍스트로부터 사용자 프롬프트 생성
        
        Args:
            youtube_transcript: 요약할 유튜브 자막 텍스트
        
        Returns:
            사용자 프롬프트 문자열
        """
        return f"""아래 텍스트를 읽고, 가장 중요한 핵심 내용을 3가지로 요약해 주세요.
- 각 요약은 한 문장으로 간결하게 작성해 주세요.
- 불필요한 설명 없이 요약만 반환해 주세요.
- 각 요약 앞에 1., 2., 3. 번호를 붙여 주세요.
- 반드시 번호 형식으로만 답변해 주세요.
- "[요약]", "[요약 예시]" 같은 접두어를 사용하지 마세요.

[텍스트]
{youtube_transcript}

[응답 형식]
1. 첫 번째 핵심 요약
2. 두 번째 핵심 요약
3. 세 번째 핵심 요약
"""

    def create_messages(self, chunk: str, position: str, prev_summary: str = None) -> list:
        """
        LLM 요청을 위한 메시지 형식 생성
        
        Args:
            chunk: 요약할 텍스트 청크
            position: 텍스트의 위치 설명 (시작/중간/끝)
            prev_summary: 이전 청크의 요약 (선택적)
            
        Returns:
            system/user 메시지 리스트
        """
        system_msg = (
            f"너는 아주 친절한 AI 어시스턴트야. 아래 텍스트는 {position}에 해당하는 부분이야. "
            "이 부분을 한국어로 3개의 핵심 포인트로 요약해줘. "
            "각 요약은 한 문장으로 간결하게 작성하고, 반드시 요약만 반환해. "
            "절대 [텍스트]와 [응답 형식]을 복사하지 말고, 반드시 번호 형식(1. 2. 3.)으로만 시작하는 요약을 생성해. "
        )
        
        if prev_summary:
            system_msg += f" 반드시 이전 청크의 요약도 참고해서 문맥을 반영해 요약을 생성해야 해. 이전 청크의 요약은 다음과 같아: {prev_summary}"
        
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": self.create_user_prompt(chunk)}
        ]