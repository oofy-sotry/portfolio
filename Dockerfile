# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치 (CPU 전용 PyTorch)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 포트 노출
EXPOSE 5000

# 데이터베이스 초기화 및 애플리케이션 실행
CMD ["sh", "-c", "sleep 10 && python init_db.py && python scripts/download_models.py && gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 run:app"]
