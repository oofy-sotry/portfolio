from flask import Blueprint, render_template, request, jsonify
import requests
import os
import json

chatbot_bp = Blueprint('chatbot', __name__)

# 간단한 FAQ 데이터
FAQ_DATA = {
    '자기소개': '안녕하세요! 저는 풀스택 개발자입니다. Flask, Python, JavaScript 등을 사용하여 웹 애플리케이션을 개발합니다.',
    '기술스택': '주요 기술스택: Python, Flask, JavaScript, HTML/CSS, MySQL, Docker, Git',
    '프로젝트': '이 포트폴리오 사이트는 Flask를 사용하여 개발한 풀스택 웹 애플리케이션입니다.',
    '연락처': '이메일이나 연락처 정보는 연락처 페이지에서 확인하실 수 있습니다.',
    '경력': '웹 개발 경험과 다양한 프로젝트를 통해 실무 역량을 쌓아왔습니다.',
    '학습': '지속적인 학습을 통해 최신 기술 트렌드를 따라가고 있습니다.'
}

@chatbot_bp.route('/')
def chat():
    """챗봇 페이지"""
    return render_template('chatbot/chat.html')

@chatbot_bp.route('/send', methods=['POST'])
def send_message():
    """챗봇 메시지 처리"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': '메시지를 입력해주세요.'}), 400
    
    # 간단한 키워드 매칭
    response = get_faq_response(user_message)
    
    # OpenAI API 연동 (선택사항)
    if not response and os.getenv('OPENAI_API_KEY'):
        response = get_openai_response(user_message)
    
    if not response:
        response = "죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다. 다른 질문을 해주시거나 연락처 페이지를 확인해주세요."
    
    return jsonify({'response': response})

def get_faq_response(message):
    """FAQ 데이터에서 응답 찾기"""
    message_lower = message.lower()
    
    for keyword, answer in FAQ_DATA.items():
        if keyword.lower() in message_lower:
            return answer
    
    # 부분 매칭
    for keyword, answer in FAQ_DATA.items():
        if any(word in message_lower for word in keyword.lower().split()):
            return answer
    
    return None

def get_openai_response(message):
    """OpenAI API를 통한 응답 생성"""
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': '당신은 개발자 포트폴리오 사이트의 챗봇입니다. 간단하고 친근하게 답변해주세요.'
                },
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return None
            
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return None

@chatbot_bp.route('/faq')
def faq():
    """FAQ 페이지"""
    return render_template('chatbot/faq.html', faq_data=FAQ_DATA)

@chatbot_bp.route('/advanced')
def advanced_chat():
    """고급 AI 챗봇 페이지"""
    return render_template('chatbot/advanced_chat.html')

@chatbot_bp.route('/ai-chat', methods=['POST'])
def ai_chat():
    """AI 기반 챗봇 응답"""
    from app.services.llm_service import LLMService
    from app.services.elasticsearch_service import ElasticsearchService
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    mode = data.get('mode', 'concise')
    search_mode = data.get('search_mode', 'faq')
    
    if not user_message:
        return jsonify({'error': '메시지를 입력해주세요.'}), 400
    
    llm_service = LLMService()
    es_service = ElasticsearchService()
    
    try:
        if search_mode == 'faq':
            # FAQ 모드 - 기본 응답
            response = get_faq_response(user_message)
            if not response:
                response = llm_service.generate_response(user_message, mode=mode)
            
            return jsonify({
                'response': response,
                'mode': mode,
                'search_mode': search_mode
            })
            
        elif search_mode == 'search':
            # 검색 모드 - Elasticsearch 검색 + LLM 응답
            search_result = es_service.search_documents(user_message, size=3)
            related_docs = []
            
            if search_result:
                related_docs = search_result.get('hits', {}).get('hits', [])
            
            # 검색 결과 기반 응답 생성
            if related_docs:
                context = ""
                for doc in related_docs:
                    context += f"제목: {doc['_source'].get('title', '')}\n"
                    context += f"내용: {doc['_source'].get('content', '')[:200]}...\n\n"
                
                prompt = f"다음 문서들을 참고하여 '{user_message}'에 대해 답변해주세요:\n\n{context}"
                response = llm_service.generate_response(prompt, mode=mode)
            else:
                response = llm_service.generate_response(user_message, mode=mode)
            
            return jsonify({
                'response': response,
                'related_docs': related_docs,
                'mode': mode,
                'search_mode': search_mode
            })
            
        elif search_mode == 'ai':
            # AI 모드 - 순수 LLM 응답
            response = llm_service.generate_response(user_message, mode=mode)
            
            return jsonify({
                'response': response,
                'mode': mode,
                'search_mode': search_mode
            })
            
    except Exception as e:
        print(f"AI 챗봇 오류: {e}")
        return jsonify({
            'error': 'AI 챗봇 처리 중 오류가 발생했습니다.',
            'response': '죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }), 500
