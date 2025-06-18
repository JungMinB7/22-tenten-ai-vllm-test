from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
from langfuse import Langfuse
import json
from pathlib import Path

class BotRecommentsPrompt:
    def __init__(self):
        # 소셜봇 프로필 정보
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

        
    def get_time_range_and_now(self, post, comment, recomments):
        """
        프롬프트에 사용할 시간 범위를 생성합니다.
        - post: PostRequest 객체
        - comment: CommentRequest 객체
        - recomments: 대댓글 리스트
        """
        tz = pytz.timezone("Asia/Seoul")
        times_kst = []
        # 게시물 작성 시간
        times_kst.append(
            datetime.strptime(post.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    .replace(tzinfo=pytz.utc)
                    .astimezone(tz)
        )
        # 댓글 작성 시간
        times_kst.append(
            datetime.strptime(comment.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    .replace(tzinfo=pytz.utc)
                    .astimezone(tz)
        )
        # 대댓글들 작성 시간
        for r in recomments or []:
            times_kst.append(
                datetime.strptime(r.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                        .replace(tzinfo=pytz.utc)
                        .astimezone(tz)
            )
        fmt = "%Y-%m-%d (%a) %-I:%M %p"
        start_time = min(times_kst).strftime(fmt)
        end_time = max(times_kst).strftime(fmt)
        current_time = datetime.now(tz).strftime(fmt)
        return start_time, end_time, current_time
    
    def json_to_messages(self, request, mode):
        """
        BotRecommentsRequest를 받아서 messages 리스트로 변환
        - request: BotRecommentsRequest 모델 인스턴스
        - mode : colab(default) / gcp
        """
        post = request.post
        comment = request.comment
        recomments = request.comment.recomments

        # 시간 범위 생성
        start_time, end_time, current_time = self.get_time_range_and_now(post, comment, recomments)


        # 프롬프트 가져오기
        if mode == "gcp":
            label="production"
        else : 
            label="latest"

        prompt_client = self.langfuse.get_prompt(
            name="recomments_bot", 
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

        # user context: 게시글, 원댓글, 기존 대댓글
        messages.append({
            "role": "assistant",
            "content": f"게시물: [{post.user.nickname} from {post.user.class_name}] {post.content}"
        })
        messages.append({
            "role": "user",
            "content": f"원댓글: [{comment.user.nickname} from {comment.user.class_name}] {comment.content}"
        })
        if recomments:
            for r in recomments:
                if r.user.nickname == self.persona["nickname"]:
                    messages.append({
                        "role": "assistant",
                        "content": f"대댓글: [{r.user.nickname} from {r.user.class_name}] {r.content}"
                    })
                else : 
                    messages.append({
                        "role": "user",
                        "content": f"대댓글: [{r.user.nickname} from {r.user.class_name}] {r.content}"
                    })
        # prompt 객체와 messages 를 함께 반환
        return prompt_client, messages