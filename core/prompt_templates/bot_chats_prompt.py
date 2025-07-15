from dotenv import load_dotenv
import os
from langfuse import Langfuse
import json
from pathlib import Path
from typing import List, Dict

class BotChatsPrompt:
    def __init__(self):
        """
        BotChatsPrompt 생성자
        - 환경 변수 및 페르소나 로드
        - Langfuse 클라이언트 초기화
        """
        if os.environ.get("LLM_MODE") in ["api-prod", "gcp-prod"]:
            load_dotenv(dotenv_path='/secrets/env')
        else:
            load_dotenv(override=True)
        
        # 소셜봇 페르소나 불러오기
        persona_path_str = os.getenv("PERSONA_PATH")
        if not persona_path_str:
            raise RuntimeError("환경변수 PERSONA_PATH 가 설정되어 있지 않습니다.")
        
        persona_path = Path(persona_path_str)
        if not persona_path.is_file():
            raise FileNotFoundError(f"persona.json 파일을 찾을 수 없습니다: {persona_path}")

        with persona_path.open("r", encoding="utf-8") as f:
            self.persona = json.load(f)
        
        # Langfuse 초기화
        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST')
        )
        
    def get_bot_user_info(self) -> dict:
        """
        소셜봇의 고정 유저 정보를 persona에서 반환합니다.
        """
        return {
            "id": self.persona["id"],
            "nickname": self.persona["nickname"],
            "class_name": self.persona["community"]
        }

    def get_messages_with_persona(self, recent_messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        최근 대화 기록에 페르소나 기반 시스템 프롬프트를 추가하여 반환합니다.
        Args:
            recent_messages (List[Dict[str, str]]): [{"role": ..., "content": ...}] 형태의 최근 대화 목록
        Returns:
            List[Dict[str, str]]: 시스템 프롬프트가 추가된 전체 대화 목록
        """
        mode = os.environ.get("LLM_MODE", "colab")
        label = "production" if "prod" in mode else "latest"

        try:
            prompt_client = self.langfuse.get_prompt(
                name="chats_bot", 
                label=label,
                type="chat"
            )

            # Langfuse 프롬프트에 페르소나 변수 적용
            system_prompt_messages = prompt_client.compile(
                name=self.persona["name"],
                gender=self.persona["gender"],
                age=self.persona["age"],
                occupation=self.persona["occupation"],
                role=self.persona["role"],
                traits=self.persona["traits"],
                tone=self.persona["tone"],
                community=self.persona["community"],
                activity_scope=self.persona["activity_scope"],
            )
        except Exception as e:
            # Langfuse에서 프롬프트를 가져오지 못할 경우를 대비한 폴백(Fallback)
            print(f"Warning: Failed to get prompt from Langfuse: {e}. Using fallback system prompt.")
            system_prompt_messages = [{
                "role": "system",
                "content": f"""당신은 소셜 커뮤니티 어플리케이션 '카카오베이스'에서 활동하는 소셜봇 '{self.persona["name"]}'입니다.
- 이름: {self.persona["name"]}
- 성별: {self.persona["gender"]}
- 나이: {self.persona["age"]}
- 직업: {self.persona["occupation"]}
- 역할: {self.persona["role"]}
- 특징: {self.persona["traits"]}
- 말투: {self.persona["tone"]}
- 활동 커뮤니티: {self.persona["community"]}
- 활동 범위: {self.persona["activity_scope"]}

위 페르소나에 맞춰서 사용자와 일상적인 대화를 나누세요. 항상 친근하고 자연스럽게 응답해야 합니다."""
            }]

        # 시스템 프롬프트와 최근 대화 기록을 결합하여 반환
        return system_prompt_messages + recent_messages
