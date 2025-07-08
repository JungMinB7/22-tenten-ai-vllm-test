FROM python:3.11-slim

WORKDIR /app

COPY requirements-gcp.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-gcp.txt

COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]