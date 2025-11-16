"""
API 기반 LLM 서비스 (OpenAI, HuggingFace API 등)
"""

import requests
import os
import json

class APILLMService:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.huggingface_api_url = "https://api-inference.huggingface.co/models"
    
    def generate_response_openai(self, prompt, mode="concise"):
        """OpenAI API를 통한 응답 생성"""
        if not self.openai_api_key:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            max_tokens = 100 if mode == "concise" else 300
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': '당신은 개발자 포트폴리오 사이트의 AI 챗봇입니다. 간단하고 친근하게 답변해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"OpenAI API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"OpenAI API 오류: {e}")
            return None
    
    def generate_response_huggingface(self, prompt, model="microsoft/DialoGPT-medium"):
        """HuggingFace API를 통한 응답 생성"""
        if not self.huggingface_api_key:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.huggingface_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'inputs': prompt,
                'parameters': {
                    'max_length': 150,
                    'temperature': 0.7,
                    'do_sample': True
                }
            }
            
            response = requests.post(
                f'{self.huggingface_api_url}/{model}',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                return str(result)
            else:
                print(f"HuggingFace API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"HuggingFace API 오류: {e}")
            return None
    
    def summarize_text_api(self, text, max_length=100):
        """API 기반 텍스트 요약"""
        if not self.openai_api_key:
            # API가 없으면 간단한 요약
            return text[:max_length] + "..." if len(text) > max_length else text
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': f'다음 텍스트를 {max_length}자 이내로 요약해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': text
                    }
                ],
                'max_tokens': max_length,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return text[:max_length] + "..." if len(text) > max_length else text
                
        except Exception as e:
            print(f"요약 API 오류: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def get_fallback_response(self, prompt):
        """API 실패 시 기본 응답"""
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
