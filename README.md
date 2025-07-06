# 22-tenten-ai

## 가상환경 
### 가상환경 생성
```bash
python3 -m venv .venv
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
python main.py --mode gcp
```
### api
```bash
python main.py --mode api-dev
```
```bash
python main.py --mode api-prod
```
### local
```bash
python main.py
```
