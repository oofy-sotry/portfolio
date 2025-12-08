#!/bin/bash

# 경량화 모델 다운로드 및 설정 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 포트폴리오 웹사이트 모델 설정 시작..."

# 스크립트가 있는 디렉토리 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 프로젝트 루트로 이동
cd "${PROJECT_ROOT}" || {
    echo "❌ 프로젝트 루트 디렉토리로 이동할 수 없습니다."
    exit 1
}

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

# 4. models 디렉토리 생성
echo "📁 models 디렉토리 확인 중..."
mkdir -p models

# 5. 모델 다운로드
echo ""
echo "📥 경량화 모델 다운로드 중..."
if python scripts/download_models.py; then
    DOWNLOAD_SUCCESS=true
else
    DOWNLOAD_SUCCESS=false
    echo "⚠️ 모델 다운로드 스크립트 실행 중 오류가 발생했습니다."
fi

# 6. 실제 모델 파일 존재 여부 확인
echo ""
echo "🔍 다운로드된 모델 파일 확인 중..."

MODELS_DIR="${PROJECT_ROOT}/models"
REQUIRED_MODELS=("embedding_model" "generation_model" "summarization_model")
ALL_MODELS_EXIST=true

for model_dir in "${REQUIRED_MODELS[@]}"; do
    model_path="${MODELS_DIR}/${model_dir}"
    if [ -d "${model_path}" ]; then
        # 디렉토리 내 파일 개수 확인
        file_count=$(find "${model_path}" -type f 2>/dev/null | wc -l)
        if [ "${file_count}" -gt 0 ]; then
            echo "  ✅ ${model_dir}: 존재함 (${file_count}개 파일)"
        else
            echo "  ⚠️  ${model_dir}: 디렉토리는 존재하지만 파일이 없음"
            ALL_MODELS_EXIST=false
        fi
    else
        echo "  ❌ ${model_dir}: 존재하지 않음"
        ALL_MODELS_EXIST=false
    fi
done

# 7. 최종 결과 출력
echo ""
echo "="*60
if [ "${ALL_MODELS_EXIST}" = true ] && [ "${DOWNLOAD_SUCCESS}" = true ]; then
echo "✅ 모델 설정 완료!"
echo ""
echo "📊 다운로드된 모델들:"
echo "  - 임베딩 모델: all-MiniLM-L6-v2 (~80MB)"
echo "  - 생성 모델: distilgpt2 (~500MB)"  
echo "  - 요약 모델: bart-large-cnn (~300MB)"
echo "  - 총 용량: 약 880MB"
    echo ""
    echo "📁 모델 저장 위치: ${MODELS_DIR}"
echo ""
echo "🚀 이제 다음 명령어로 Docker를 실행할 수 있습니다:"
echo "  docker compose up -d"
    exit 0
else
    echo "⚠️ 모델 설정이 완전히 완료되지 않았습니다."
    echo ""
    if [ "${DOWNLOAD_SUCCESS}" = false ]; then
        echo "❌ 모델 다운로드 스크립트 실행 실패"
    fi
    if [ "${ALL_MODELS_EXIST}" = false ]; then
        echo "❌ 일부 모델 파일이 누락되었습니다"
    fi
    echo ""
    echo "💡 해결 방법:"
    echo "  1. 네트워크 연결을 확인하세요"
    echo "  2. 디스크 공간을 확인하세요 (최소 1GB 필요)"
    echo "  3. 다시 실행: bash scripts/setup_models.sh"
    echo ""
    echo "⚠️ Docker 컨테이너 실행 시 HuggingFace에서 자동으로 다운로드됩니다."
    echo "   (첫 실행 시 시간이 오래 걸릴 수 있습니다)"
    exit 1
fi
