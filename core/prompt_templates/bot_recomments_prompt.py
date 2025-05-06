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
    
    def json_to_messages(self, request):
        """
        BotRecommentsRequest를 받아서 messages 리스트로 변환
        - request: BotRecommentsRequest 모델 인스턴스
        """
        post = request.post
        comment = request.comment
        recomments = request.comment.recomments

        # 시간 범위 생성
        start_time, end_time, current_time = self.get_time_range_and_now(post, comment, recomments)

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
                                        1) 게시물과 댓글, 대댓글의 분위기와 공통된 주제 파악  
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
                                        위 “생각 단계”를 머릿속으로 순서대로 실행한 뒤, 출력 규칙을 100% 준수하여 순수 본문 텍스트(2~3문장)로 어울리는 신규 대댓글을 작성해 주세요.
                                        """.strip()
                        }
                    ]


        # user context: 게시글, 원댓글, 기존 대댓글
        messages.append({
            "role": "user",
            "content": f"게시물: {post.content}"
        })
        messages.append({
            "role": "user",
            "content": f"원댓글: {comment.content}"
        })
        if recomments:
            for r in recomments:
                messages.append({
                    "role": "user",
                    "content": f"[{r.user.nickname} from {r.user.class_name}] {r.content}"
                })

        return messages