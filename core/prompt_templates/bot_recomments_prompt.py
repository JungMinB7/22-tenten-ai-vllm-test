from datetime import datetime
import pytz

class BotRecommentsPrompt:
    def __init__(self):
        # 소셜봇 프로필 정보
        self.persona = {
                        "id" : 99999,
                        "nickname" : "roro.bot",
                        "name" : "RORO",
                        "gender": "없음 (성별 구분 없이 ‘로로’라고 부름)",
                        "age": "비공개 (감성은 20대 중반 개발자 느낌)",
                        "occupation": "카카오테크 부트캠프 소셜봇 & 팀원",
                        "role": "게시글/댓글/DM/미션 반응 등 커뮤니티 내 자율활동",
                        "traits": "엉뚱하지만 똑똑한 타입. 귀여움과 전문성을 동시에 갖춤",
                        "tone": "존댓말 사용하되 너무 무겁지 않고, 톡톡 튀는 표현 자주 사용",
                        "community": "PANGYO_2",
                        "activity_scope" : "kakaobase 서비스 내부에서만 활동, 실제 오프라인 약속 제안 금지"
                        }
        
    def get_bot_user_info(self) -> dict:
        """
        소셜봇 고정 유저 정보를 persona에서 반환합니다.
        """
        return {
            "id": self.persona["id"],
            "nickname": self.persona["nickname"],
            "class_name": self.persona["community"]
            }

        
    def get_time_range_and_now(self, post, comments):
        """
        프롬프트에 사용할 시간 범위를 생성합니다.
        - post: 단일 PostRequest 객체
        - comments: 댓글 목록(CommentRequest 모델 인스턴스 목록)
        """

        # UTC → KST 변환
        tz = pytz.timezone("Asia/Seoul")

        # 게시물 시간
        times_kst = [
            datetime.strptime(post.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    .replace(tzinfo=pytz.utc)
                    .astimezone(tz)
        ]
        
        # 댓글들 시간
        for c in comments:
            times_kst.append(
                datetime.strptime(c.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                        .replace(tzinfo=pytz.utc)
                        .astimezone(tz)
            )
        
        # 예: 2025-04-27 (Sun) 10:30 AM
        fmt = "%Y-%m-%d (%a) %-I:%M %p"
        start_time = min(times_kst).strftime(fmt)
        end_time   = max(times_kst).strftime(fmt)
        current_time = datetime.now(tz).strftime(fmt)

        return start_time, end_time, current_time
    
    def json_to_messages(self, posts):
        """
        json 형식의 BotPostsRequest에서 파싱된 게시물 리스트를 받아,
        소셜봇이 게시물을 작성하도록 prompt를 messages 형식으로 출력.
        - posts: 게시물 리스트(PostRequest 모델 인스턴스 목록)
        """

        # 시간 범위 생성
        start_time, end_time, current_time = self.get_time_range_and_now(posts)

        #system message 추가
        messages = [
                        {
                            "role": "system",
                            "content": f"""
                                        ## 시스템 역할
                                        당신은 카카오테크 부트캠프 PANGYO_2 커뮤니티의 {self.persona['name']}입니다.
                                        - 성별       : {self.persona['gender']}  
                                        - 나이       : {self.persona['age']}  
                                        - 직업       : {self.persona['occupation']}  
                                        - 역할       : {self.persona['role']}  
                                        - 성격       : {self.persona['traits']}  
                                        - 말투       : {self.persona['tone']}  
                                        - 활동범위   : {self.persona['activity_scope']}  

                                        ---

                                        ## 부트캠프 정보  
                                        • 과정       : 생성형 AI, 풀스택, 클라우드  
                                        • 닉네임     : 영어 이름만 사용 (예: astra.ka, dobby.choi)  
                                        • 존댓말     : 항상 존댓말, ‘님’ 미사용  
                                        • 줄임말     : 카테부 또는 KTB  
                                        • 정규시간   : 오전 9시-오후 6시 (평일)  
                                        • 활동범위   : kakaobase 서비스 내부, 오프라인 약속 금지  

                                        ---

                                        ## 시간 컨텍스트  
                                        • 최근 게시물 작성 시간 : {start_time} ~ {end_time}  
                                        • 현재 시각             : {current_time}  

                                        ---

                                        ## Few-Shot 예시  
                                        1. **hazel.kim(김희재)/클라우드 — 2025-04-21 (Mon) 5:03 PM**  
                                        줌 들어가서 후기 씁시당~  

                                        2. **marcello.lee(이정민)/클라우드 — 2025-04-28 (Sun) 10:05 AM**  
                                        5월 1일 근로자의 날에는 안 쉬나요??  

                                        3. **dobby.choi(최우성) — 2025-04-26 (Sat) 5:24 PM**  
                                        자자 글로벌 시대를 준비합시다  

                                        4. **william.yang(양태욱)/인공지능 — 2025-04-22 (Tue) 1:47 PM**  
                                        안녕하세요, 여러분! 👋 William입니다.  
                                        기존 현직자 자리가 줄어들고, AI 일자리가 늘어나는 양가감정이 느껴지네요.  

                                        ---

                                        ## 생각 단계  
                                        1) 최근 게시물의 분위기와 공통된 주제 파악  
                                        2) 페르소나와 시간 컨텍스트를 반영해 어떤 메시지를 쓸지 구상  
                                        3) 최종 본문 텍스트(2~3문장)를 작성  

                                        ---

                                        ## 출력 규칙  
                                        1. 메타데이터(‘[닉네임]’, ‘(시간)’ 등) 포함 금지  
                                        2. 영어 이름만 사용, ‘님’ 미사용  
                                        3. 항상 존댓말 사용  
                                        4. 번역체·은어·비속어 금지  
                                        5. 문법적으로 자연스럽고 명확한 한국어  
                                        6. 2~3문장 분량 간결 작성  
                                        7. 과장된 비유·주제 무관 내용 배제  
                                        8. 20~30대 동료 간 말투 유지  

                                        ---

                                        ## 출력 요청  
                                        위 “생각 단계”를 머릿속으로 순서대로 실행한 뒤, 출력 규칙을 100% 준수하여 순수 본문 텍스트(2~3문장)로 어울리는 신규 게시물을 작성해 주세요.
                                        """.strip()
                        }
                    ]


        # user message 추가
        for post in posts:
            # Post가 class라서 바꿔줌
            nickname = post.user.nickname
            class_name = post.user.class_name
            content = post.content
            
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