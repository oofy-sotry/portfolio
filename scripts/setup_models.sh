#!/bin/bash

# 경량화 모델 다운로드 및 설정 스크립트

echo "🚀 포트폴리오 웹사이트 모델 설정 시작..."

# 1. Python 가상환경 확인
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

# 2. 가상환경 활성화
echo "🔄 가상환경 활성화 중..."
source venv/bin/activate

# 3. 필요한 패키지 설치
echo "📥 필요한 패키지 설치 중..."
pip install --upgrade pip
pip install torch transformers sentence-transformers

# 4. 모델 다운로드
echo "📥 경량화 모델 다운로드 중..."
python scripts/download_models.py

# 5. 모델 디렉토리 확인
echo "📁 모델 디렉토리 구조 확인..."
ls -la models/

echo "✅ 모델 설정 완료!"
echo ""
echo "📊 다운로드된 모델들:"
echo "  - 임베딩 모델: all-MiniLM-L6-v2 (~80MB)"
echo "  - 생성 모델: distilgpt2 (~500MB)"  
echo "  - 요약 모델: bart-large-cnn (~300MB)"
echo "  - 총 용량: 약 880MB"
echo ""
echo "🚀 이제 다음 명령어로 Docker를 실행할 수 있습니다:"
echo "  docker compose up -d"
