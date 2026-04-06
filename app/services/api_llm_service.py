"""
API 기반 LLM 서비스 (Claude, ChatGPT, Gemini)
로컬 모델(KoGPT2)의 고급 답변 보완용
"""

import requests
import os


SYSTEM_PROMPT = (
    "당신은 개발자 포트폴리오 사이트의 AI 챗봇입니다. "
    "한국어로 친근하고 정확하게 답변해주세요."
)


class APILLMService:
    """외부 API LLM 통합 서비스"""

    def __init__(self):
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')

    def get_available_providers(self):
        """사용 가능한 API 제공자 목록 반환"""
        providers = []
        if self.anthropic_api_key:
            providers.append('claude')
        if self.openai_api_key:
            providers.append('chatgpt')
        if self.google_api_key:
            providers.append('gemini')
        return providers

    def generate_response(self, prompt, provider, mode="concise"):
        """지정된 provider로 응답 생성"""
        dispatch = {
            'claude': self._call_claude,
            'chatgpt': self._call_chatgpt,
            'gemini': self._call_gemini,
        }

        handler = dispatch.get(provider)
        if not handler:
            return None

        max_tokens = 150 if mode == "concise" else 500
        return handler(prompt, max_tokens)

    def _call_claude(self, prompt, max_tokens):
        """Anthropic Claude API 호출"""
        if not self.anthropic_api_key:
            return None

        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': self.anthropic_api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'claude-sonnet-4-20250514',
                    'max_tokens': max_tokens,
                    'system': SYSTEM_PROMPT,
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                print(f"Claude API 오류: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Claude API 오류: {e}")
            return None
