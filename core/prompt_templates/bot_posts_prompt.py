from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
from langfuse import Langfuse
import json
from pathlib import Path

class BotPostsPrompt:
    def __init__(self):
        if os.environ.get("LLM_MODE") == "api-prod":
            load_dotenv(dotenv_path='/secrets/env')
        else:
            load_dotenv(override=True)
        
        # 소셜봇 페르소나 불러오기 시작
        persona_path_str = os.getenv("PERSONA_PATH")
        if not persona_path_str:
            raise RuntimeError("환경변수 PERSONA_PATH 가 설정되어 있지 않습니다.")
        
        persona_path = Path(persona_path_str)
        if not persona_path.is_file():
            raise FileNotFoundError(f"persona.json 파일을 찾을 수 없습니다: {persona_path}")

        # JSON 로드
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
        소셜봇 고정 유저 정보를 persona에서 반환합니다.
        """
        return {
            "id": self.persona["id"],
            "nickname": self.persona["nickname"],
            "class_name": self.persona["community"]
            }

        
    def get_time_range_and_now(self, posts):
        '''
        프롬프트에 사용할 시간 범위를 생성하는 함수.
        - posts: 게시물 리스트(PostRequest 모델 인스턴스 목록)
        '''
         # UTC → KST 변환
        tz = pytz.timezone("Asia/Seoul")
        times_kst = [
            datetime.strptime(p.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    .replace(tzinfo=pytz.utc)
                    .astimezone(tz)
            for p in posts
        ]
        
        # 예: 2025-04-27 (Sun) 10:30 AM
        fmt = "%Y-%m-%d (%a) %-I:%M %p"
        start_time = min(times_kst).strftime(fmt)
        end_time   = max(times_kst).strftime(fmt)
        current_time = datetime.now(tz).strftime(fmt)

        return start_time, end_time, current_time
    
    def json_to_messages(self, posts, mode):
        """
        json 형식의 BotPostsRequest에서 파싱된 게시물 리스트를 받아,
        소셜봇이 게시물을 작성하도록 prompt를 messages 형식으로 출력.
        - posts: 게시물 리스트(PostRequest 모델 인스턴스 목록)
        - mode : colab(default) / gcp
        """

        # 시간 범위 생성
        start_time, end_time, current_time = self.get_time_range_and_now(posts)
        
        # 프롬프트 가져오기
        if mode == "gcp":
            label="production"
        else : 
            label="latest"

        prompt_client = self.langfuse.get_prompt(
            name="posts_bot", 
            label=label,
            type="chat"
        )

        #langfuse 프롬프트에 변수 적용
        messages = prompt_client.compile(
            name=self.persona["name"],
            gender= self.persona["gender"],
            age=self.persona["age"],
            occupation = self.persona["occupation"],
            role=self.persona["role"],
            traits=self.persona["traits"],
            tone=self.persona["tone"],
            community=self.persona["community"],
            activity_scope=self.persona["activity_scope"],
            start_time=start_time,
            end_time=end_time,
            current_time=current_time
        )
        
        # user message 추가
        for post in posts:
            nickname = post.user.nickname
            class_name = post.user.class_name
            content = post.content
            
            messages.append({
                "role": "user",
                "content": f"[{nickname} from {class_name}] {content}"
            })
        
        # prompt 객체와 messages 를 함께 반환
        return prompt_client, messages