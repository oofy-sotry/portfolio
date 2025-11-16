#!/usr/bin/env python3
"""
HuggingFace 모델 사전 다운로드 스크립트
"""

import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

def download_models():
    """기본 모델들을 사전 다운로드"""
    print("🚀 HuggingFace 모델 다운로드 시작...")
    
    models = {
        'embedding': 'sentence-transformers/all-MiniLM-L6-v2',
        'generation': 'distilgpt2', 
        'summarization': 'facebook/bart-large-cnn'
    }
    
    for model_type, model_name in models.items():
        try:
            print(f"📥 {model_type} 모델 다운로드 중: {model_name}")
            
            if model_type == 'embedding':
                model = SentenceTransformer(model_name)
                print(f"✅ {model_type} 모델 다운로드 완료")
                
            elif model_type == 'generation':
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                print(f"✅ {model_type} 모델 다운로드 완료")
                
            elif model_type == 'summarization':
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                print(f"✅ {model_type} 모델 다운로드 완료")
                
        except Exception as e:
            print(f"❌ {model_type} 모델 다운로드 실패: {e}")
    
    print("🎉 모든 모델 다운로드 완료!")

if __name__ == "__main__":
    download_models()