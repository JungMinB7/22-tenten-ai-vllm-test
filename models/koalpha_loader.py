import requests
from dotenv import load_dotenv
import os, time

class KoalphaLoader:
    def __init__(self):
        load_dotenv()
        self.url = f"{os.getenv('NGROK_URL')}/v1/chat/completions"
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

        try : 
            return {"status_code":response.status_code, "content":response.json()["choices"][0]["message"]["content"]}
        except:
           return {"status_code":response.status_code, "content":str(response.reason)} 
    
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