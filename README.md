# 22-tenten-ai

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
python main.py mode --gcp
```
### local
```bash
python main.py
```
