import requests
from dotenv import load_dotenv
import os, time

class KoalphaLoader:
    def __init__(self):
        load_dotenv()
        self.url = f"{os.getenv('MODEL_NGROK_URL')}/v1/chat/completions" #FastAPI와 Colab에서 열은 ngrok과 충돌나지 않게 변수명 변경
        self.headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer dummy-key"  # dummy-key: 아무거나 넣어도 됨
                        }
        self.data = {
                        "model": "allganize/Llama-3-Alpha-Ko-8B-Instruct",
                        "messages": [],
                        "temperature": 0.7
                    }
    
    def get_response(self, messages):
        '''
        messages 예시
        messages = [
                        {"role": "system", "content": "You are an AI assistant in a group chat. Let users talk, and only respond if your help seems needed. Users identify themselves using [Name]."},

                        {"role": "user", "content": "[Alice] 이번 주말에 뭐하지? 너무 심심할 것 같아."},
                        {"role": "user", "content": "[Bob] 나도. 그냥 넷플릭스나 볼까... 요즘 볼만한 거 뭐 있지?"},
                        
                        {"role": "assistant", "content": "혹시 영화 추천 원하시나요? 최근에 '죽지 않는 인간들의 밤'이 코믹하고 재미있어요!"},

                        {"role": "user", "content": "[Alice] 오 그거 들어봤어! 그거 무서운 영화야?"},
                        {"role": "user", "content": "[Bob] 좀비 나오는 거 아냐? 난 좀비 별로인데..."},
                    ]
        '''
        self.data["messages"] = messages

        start_time = time.time()
        response = requests.post(self.url, headers=self.headers, json=self.data)
        end_time = time.time()
        print(f"response time : {(end_time - start_time):.3f}")

       # 에러 상태(200 이외)는 세부 정보까지 모두 리턴
        if response.status_code != 200:
            # 가능하면 JSON으로도, 아니면 텍스트 그대로
            try:
                error_body = response.json()
            except ValueError:
                error_body = response.text
            return {
                "status_code": response.status_code,
                "url": response.url,
                "headers": dict(response.headers),
                "error": error_body
            }
        
        # 정상 응답 파싱
        body = response.json()
        return {
            "status_code": response.status_code,
            "url": response.url,
            "content": body["choices"][0]["message"]["content"]
        }
    
'''
KoalphaLoader 클래스 사용 방법 예시
'''
'''
messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "안녕! 날씨 어때?"}
            ]
koalpha=KoalphaLoader()
print(koalpha.get_response(messages))
'''