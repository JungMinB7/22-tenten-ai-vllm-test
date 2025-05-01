from datetime import datetime
import pytz

class BotPostsPrompt:
    def __init__(self):
        self.persona = {
                            "name": "Roro",
                            "traits": "a cheerful, supportive, and engaging AI social bot",
                            "community": "PANGYO_2"
                        }
        
    
    def get_time_range_and_now(self, posts):
        '''
        프롬프트에 사용할 시간 범위를 생성하는 함수입니다.
        - posts : 유저 게시물 리스트
        '''
        times_kst = [
            datetime.strptime(p["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            .replace(tzinfo=pytz.utc)
            .astimezone(pytz.timezone("Asia/Seoul"))
            for p in posts
        ]
        start_time = min(times_kst).strftime("%-I:%M %p")
        end_time = max(times_kst).strftime("%-I:%M %p")
        current_time = datetime.now(pytz.timezone("Asia/Seoul")).strftime("%-I:%M %p")

        return start_time, end_time, current_time
    
    def json_to_messages(self, posts):
        '''
        json형식으로 된 요청을 model에 넣기 전,
        소셜봇이 게시물을 작성하도록 prompt를 messages 형식으로 출력한다.
        - posts : 유저 게시물 리스트 
        '''

        # 시간 범위 생성
        start_time, end_time, current_time = self.get_time_range_and_now(posts)

        #system message 추가
        messages = [
                        {
                            "role": "system",
                            "content": (
                                f"당신은 {self.persona['community']} 커뮤니티의 {self.persona['name']}로, "
                                f"{self.persona['traits']} 성격을 지닌 AI 소셜 봇입니다. "
                                f"공유 게시판에서 친근하고 자연스럽게 참여합니다. "
                                f"최근 게시물은 {start_time}부터 {end_time} 사이에 작성되었습니다. "
                                f"현재 시각은 {current_time}입니다. "
                                "위 최근 게시물을 바탕으로 어울리는 새 게시물을 하나 작성해 주세요. "
                                "출력 시 절대 ‘[닉네임 from 클래스]’ 같은 메타데이터나 ‘(댓글 시간 …)’ 같은 타임스탬프를 포함하지 말고, 게시물 본문 내용만 작성해 주세요."
                            )
                        }
                    ]



        # user message 추가
        for post in posts:
            nickname = post["user"]["nickname"]
            class_name = post["user"]["class_name"]
            content = post["content"]
            
            messages.append({
                "role": "user",
                "content": f"[{nickname} from {class_name}] {content}"
            })
       
        return messages


'''
BotPostsPrompt 클래스 사용 방법 예시
'''

'''
from models.koalpha_loader import KoalphaLoader

# 게시물 데이터
posts = [
    {
        "id": 1110,
        "user": {"nickname": "hazel.kim", "class_name": "PANGYO_2"},
        "created_at": "2025-04-27T10:30:32.311141Z",
        "content": "좋은아침입니당"
    },
    {
        "id": 1111,
        "user": {"nickname": "rick.lee", "class_name": "PANGYO_2"},
        "created_at": "2025-04-27T10:41:32.311141Z",
        "content": "좋은아침입니다~"
    },
    {
        "id": 1112,
        "user": {"nickname": "marcello.lee", "class_name": "PANGYO_2"},
        "created_at": "2025-04-27T11:40:32.311141Z",
        "content": "혹시 커피 사러 같이 나가실 분 계신가요"
    },
    {
        "id": 1113,
        "user": {"nickname": "dobby.choi", "class_name": "PANGYO_2"},
        "created_at": "2025-04-27T11:41:32.311141Z",
        "content": "여러분 간식 리필됐대요"
    },
    {
        "id": 1114,
        "user": {"nickname": "daisy.kim", "class_name": "PANGYO_2"},
        "created_at": "2025-04-27T11:43:32.311141Z",
        "content": "아 진쨔?"
    }
]

bot_post_prompt = BotPostsPrompt()
messages = bot_post_prompt.json_to_messages(posts)

print(messages)

koalpha=KoalphaLoader()
print(koalpha.get_response(messages))

'''