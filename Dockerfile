FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 크론 작업 설정
COPY CRON_SETUP.md /app/
RUN chmod +x /app/market_automation/slots/*.py

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV TZ=Asia/Seoul

# 크론 서비스 시작 스크립트
RUN echo "#!/bin/bash\ncron && tail -f /var/log/cron.log" > /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
