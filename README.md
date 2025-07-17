# 22-tenten-ai

## GCP 서버 이사갔을때 main.py 정상 작동 시키기
1. git clone
2. 가상환경 설정
```bash
python3 -m venv .venv
```
3. 가상환경 활성화
```bash
source .venv/bin/activate
```
4. requirements 다운로드
```bash
pip install -r requirements-gcp.txt
```
5. cuda(version : 12.4) 설정
```bash
sudo apt update
sudo apt install nvidia-driver-550
sudo reboot
```
---
## 가상환경 
### 가상환경 생성
```bash
python -m venv .venv
```
### 가상환경 활성화
```bash
source .venv/bin/activate
```
---
## requirements
### gcp
```bash
pip install -r requirements-gcp.txt
```
### local
```bash
pip install -r requirements.txt
```
---
## 실행
### gcp
```bash
python main.py --mode gcp-prod
```
```bash
python main.py --mode gcp-dev
```
### api(gemini)
```bash
python main.py --mode api-prod
```
```bash
python main.py --mode api-dev
```
### local (colab 통신)
```bash
python main.py
```
