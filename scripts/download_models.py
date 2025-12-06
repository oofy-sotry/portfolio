#!/usr/bin/env python3
"""
HuggingFace 모델 사전 다운로드 스크립트
"""

import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

def download_models():
    """기본 모델들을 사전 다운로드하고 ./models 디렉토리에 저장"""
    # 스크립트가 있는 디렉토리 찾기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    models_dir = os.path.join(project_root, "models")
    
    # models 디렉토리 생성
    os.makedirs(models_dir, exist_ok=True)
    print(f"📁 모델 저장 경로: {models_dir}")
    
    print("🚀 HuggingFace 모델 다운로드 시작...")
    
    models = {
        'embedding': 'sentence-transformers/all-MiniLM-L6-v2',
        'generation': 'distilgpt2', 
        'summarization': 'facebook/bart-large-cnn'
    }
    
    download_results = {}
    
    for model_type, model_name in models.items():
        try:
            print(f"\n📥 {model_type} 모델 다운로드 중: {model_name}")
            
            model_save_path = os.path.join(models_dir, f"{model_type}_model")
            
            if model_type == 'embedding':
                # 임베딩 모델 다운로드 및 저장
                model = SentenceTransformer(model_name)
                model.save(model_save_path)
                print(f"✅ {model_type} 모델 다운로드 및 저장 완료")
                print(f"   저장 위치: {model_save_path}")
                
            elif model_type == 'generation':
                # 생성 모델 다운로드 및 저장
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                tokenizer.save_pretrained(model_save_path)
                model.save_pretrained(model_save_path)
                print(f"✅ {model_type} 모델 다운로드 및 저장 완료")
                print(f"   저장 위치: {model_save_path}")
                
            elif model_type == 'summarization':
                # 요약 모델 다운로드 및 저장
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                tokenizer.save_pretrained(model_save_path)
                model.save_pretrained(model_save_path)
                print(f"✅ {model_type} 모델 다운로드 및 저장 완료")
                print(f"   저장 위치: {model_save_path}")
            
            # 저장 확인
            if os.path.exists(model_save_path) and os.path.isdir(model_save_path):
                # 디렉토리 내 파일 개수 확인
                file_count = len([f for f in os.listdir(model_save_path) if os.path.isfile(os.path.join(model_save_path, f))])
                if file_count > 0:
                    download_results[model_type] = True
                    print(f"   ✓ 저장 확인: {file_count}개 파일")
                else:
                    download_results[model_type] = False
                    print(f"   ⚠️ 저장 경로는 존재하지만 파일이 없습니다")
            else:
                download_results[model_type] = False
                print(f"   ❌ 저장 경로가 생성되지 않았습니다")
                
        except Exception as e:
            print(f"❌ {model_type} 모델 다운로드 실패: {e}")
            import traceback
            traceback.print_exc()
            download_results[model_type] = False
    
    # 최종 결과 확인
    print("\n" + "="*60)
    print("📊 다운로드 결과 요약:")
    print("="*60)
    
    all_success = True
    for model_type, success in download_results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {model_type:15s}: {status}")
        if not success:
            all_success = False
    
    print("="*60)
    
    if all_success:
        print("🎉 모든 모델 다운로드 및 저장 완료!")
        return 0
    else:
        print("⚠️ 일부 모델 다운로드에 실패했습니다.")
        print("💡 Docker 컨테이너 실행 시 HuggingFace에서 자동으로 다운로드됩니다.")
        return 1

if __name__ == "__main__":
    exit_code = download_models()
    sys.exit(exit_code)