"""
HuggingFace LLM 서비스 (KoGPT2, KoBART)
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import os
import re

class LLMService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 LLM 서비스 초기화 - 사용 디바이스: {self.device}")
        self.embedding_model = None
        self.generation_model = None
        self.summarization_model = None
        self.tokenizer = None
        self.summarization_tokenizer = None
        
        # 모델 로딩
        self._load_models()
        
        # 모델 로딩 상태 확인
        self._check_models_loaded()
    
    def _load_models(self):
        """로컬 경량화 모델 로딩"""
        try:
            models_dir = "/app/models"
            
            # 1. 한글 임베딩 모델 로딩
            EMBEDDING_MODEL_NAME = 'jhgan/ko-sroberta-multitask'
            print(f"🔄 임베딩 모델 로딩 중... ({EMBEDDING_MODEL_NAME})")
            embedding_path = os.path.join(models_dir, "embedding_model")
            if os.path.exists(embedding_path) and os.listdir(embedding_path):
                try:
                    self.embedding_model = SentenceTransformer(embedding_path)
                    print("✅ 로컬 임베딩 모델 로딩 완료")
                except Exception as e:
                    print(f"⚠️ 로컬 임베딩 모델 로딩 실패: {e}")
                    self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            else:
                print("⚠️ 로컬 모델 없음. HuggingFace에서 다운로드...")
                self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
                os.makedirs(embedding_path, exist_ok=True)
                self.embedding_model.save(embedding_path)
                print(f"💾 임베딩 모델 저장 완료: {embedding_path}")
            
            # 2. 한글 생성 모델 로딩 (KoGPT2)
            GENERATION_MODEL_NAME = 'skt/kogpt2-base-v2'
            print(f"🔄 생성 모델 로딩 중... ({GENERATION_MODEL_NAME})")
            generation_path = os.path.join(models_dir, "generation_model")
            if os.path.exists(generation_path) and os.listdir(generation_path):
                self.tokenizer = AutoTokenizer.from_pretrained(generation_path)
                self.generation_model = AutoModelForCausalLM.from_pretrained(generation_path)
            else:
                print("⚠️ 로컬 모델 없음. HuggingFace에서 다운로드...")
                self.tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
                self.generation_model = AutoModelForCausalLM.from_pretrained(GENERATION_MODEL_NAME)
                os.makedirs(generation_path, exist_ok=True)
                self.tokenizer.save_pretrained(generation_path)
                self.generation_model.save_pretrained(generation_path)
                print(f"💾 생성 모델 저장 완료: {generation_path}")
            self.generation_model.to(self.device)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            print("✅ 생성 모델 로딩 완료")
            
            # 3. 한글 요약 모델 로딩 (KoBART)
            SUMMARIZATION_MODEL_NAME = 'digit82/kobart-summarization'
            print(f"🔄 요약 모델 로딩 중... ({SUMMARIZATION_MODEL_NAME})")
            summarization_path = os.path.join(models_dir, "summarization_model")
            if os.path.exists(summarization_path):
                self.summarization_tokenizer = AutoTokenizer.from_pretrained(summarization_path)
                self.summarization_model = AutoModelForSeq2SeqLM.from_pretrained(summarization_path)
            else:
                print("⚠️ 로컬 모델 없음. HuggingFace에서 다운로드...")
                self.summarization_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZATION_MODEL_NAME)
                self.summarization_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZATION_MODEL_NAME)
            self.summarization_model.to(self.device)
            print("✅ 요약 모델 로딩 완료")
            
            print("🎉 모든 로컬 모델 로딩 완료!")
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            import traceback
            traceback.print_exc()
            print("🔄 기본 응답 모드로 전환...")
            # 모델 로딩 실패 시 기본 응답 모드로 전환
            self.embedding_model = None
            self.generation_model = None
            self.summarization_model = None
    
    def _check_models_loaded(self):
        """모델 로딩 상태 확인 및 로그 출력"""
        print("\n" + "="*60)
        print("📊 모델 로딩 상태:")
        print("="*60)
        models = {
            "임베딩 (ko-sroberta)": self.embedding_model,
            "생성 (KoGPT2)": self.generation_model,
            "요약 (KoBART)": self.summarization_model,
        }
        for name, model in models.items():
            status = "✅ 로드됨" if model is not None else "❌ 로드 실패"
            print(f"  {name}: {status}")
        print("="*60 + "\n")
    
    def get_embeddings(self, texts):
        """텍스트 임베딩 생성"""
        if self.embedding_model is None:
            return None
        
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return None
    
    def summarize_text(self, text, max_length=100):
        """텍스트 요약"""
        if self.summarization_model is None or self.summarization_tokenizer is None:
            # 모델이 없으면 간단한 요약
            return text[:max_length] + "..." if len(text) > max_length else text
        
        try:
            # 입력 텍스트 전처리
            inputs = self.summarization_tokenizer(
                text,
                max_length=512,
                padding=True,
                truncation=True,
                return_tensors="pt"
            ).to(self.device)
            
            # 요약 생성
            with torch.no_grad():
                summary_ids = self.summarization_model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    min_length=30,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
            
            summary = self.summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
            
        except Exception as e:
            print(f"❌ 요약 생성 실패: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def generate_response(self, prompt, max_length=150, mode="concise"):
        """응답 생성"""
        if self.generation_model is None or self.tokenizer is None:
            # 모델이 없으면 기본 응답
            print(f"⚠️ LLM 모델이 로드되지 않아 기본 응답을 반환합니다.")
            print(f"   generation_model: {self.generation_model is not None}")
            print(f"   tokenizer: {self.tokenizer is not None}")
            return self._get_fallback_response(prompt)
        
        try:
            # 프롬프트 전처리
            if mode == "concise":
                formatted_prompt = f"질문: {prompt}\n답변:"
            else:
                formatted_prompt = f"질문: {prompt}\n상세한 답변:"
            
            # 토크나이징
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            ).to(self.device)
            
            # 생성
            with torch.no_grad():
                outputs = self.generation_model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # 응답 디코딩
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 프롬프트 부분 제거
            if "답변:" in response:
                response = response.split("답변:")[-1].strip()
            if "상세한 답변:" in response:
                response = response.split("상세한 답변:")[-1].strip()
            
            # 빈 응답 체크
            if not response or len(response.strip()) == 0:
                return self._get_fallback_response(prompt)
            
            return response
            
        except Exception as e:
            print(f"❌ 응답 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt):
        """모델 로딩 실패 시 기본 응답"""
        fallback_responses = {
            "자기소개": "안녕하세요! 풀스택 개발자입니다. Python, Flask, JavaScript 등을 사용하여 웹 애플리케이션을 개발합니다.",
            "기술스택": "주요 기술스택: Python, Flask, JavaScript, HTML/CSS, MySQL, Docker, Git",
            "프로젝트": "이 포트폴리오 사이트는 Flask를 사용하여 개발한 풀스택 웹 애플리케이션입니다.",
            "연락처": "이메일이나 연락처 정보는 연락처 페이지에서 확인하실 수 있습니다.",
            "경력": "웹 개발 경험과 다양한 프로젝트를 통해 실무 역량을 쌓아왔습니다."
        }
        
        # 키워드 매칭
        for keyword, response in fallback_responses.items():
            if keyword in prompt:
                return response
        
        return "죄송합니다. 해당 질문에 대한 답변을 준비 중입니다. 다른 질문을 해주시거나 연락처 페이지를 확인해주세요."
    
