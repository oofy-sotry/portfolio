from flask import Blueprint, render_template, request, jsonify
import requests
import os
import json
from app.models import FAQ
from app.services.elasticsearch_service import ElasticsearchService

chatbot_bp = Blueprint('chatbot', __name__)

def _load_faq_data():
    """DB에서 활성화된 FAQ를 읽어 dict로 반환 (기존 템플릿 호환용)"""
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.id.asc()).all()
    return {f.question: f.answer for f in faqs}

@chatbot_bp.route('/')
def chat():
    """챗봇 페이지"""
    faq_data = _load_faq_data()
    return render_template('chatbot/chat.html', faq_data=faq_data)

@chatbot_bp.route('/send', methods=['POST'])
def send_message():
    """챗봇 메시지 처리 (일반 챗봇 - 간단한 답변)"""
    from app.services.llm_service import LLMService
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': '메시지를 입력해주세요.'}), 400
    
    # 1단계: Elasticsearch에서 FAQ/게시글 검색
    es_service = ElasticsearchService()
    search_result = es_service.search_documents(user_message, size=5)
    high_score_faq_answer = None
    related_docs = []

    if search_result:
        hits = search_result.get('hits', {}).get('hits', [])
        related_docs = hits
        if hits:
            top_hit = hits[0]
            score = top_hit.get('_score', 0)
            source = top_hit.get('_source', {})
            # doc_type이 faq이고 점수가 임계값 이상이면 FAQ 직접 응답 (LLM 사용 안 함)
            if source.get('doc_type') == 'faq' and score >= 5.0:
                high_score_faq_answer = source.get('content')
    
    # 점수 높은 FAQ가 있으면 바로 응답
    if high_score_faq_answer:
        return jsonify({'response': high_score_faq_answer, 'related_docs': related_docs})
    
    # LLM을 사용한 응답 생성 (ES 검색 결과를 컨텍스트로 활용) - 100자 이내 간단한 답변
    try:
        llm_service = LLMService()
        context = ""
        if related_docs:
            for doc in related_docs[:3]:
                src = doc.get('_source', {})
                title = src.get('title') or src.get('question') or ''
                content = src.get('content', '')[:200]
                context += f"제목: {title}\n내용: {content}\n\n"
        
        if context:
            prompt = f"다음 FAQ/게시글 내용을 참고하여 사용자의 질문에 간단하게(100자 이내) 한국어로 답변해줘.\n\n[컨텍스트]\n{context}\n[질문]\n{user_message}\n[답변]"
        else:
            prompt = user_message

        # 일반 챗봇은 간단한 답변 (100자 이내)
        response = llm_service.generate_response(prompt, max_length=100, mode="concise")
        
        # 문자 수 제한 (100자 이내)
        if response and len(response) > 100:
            response = response[:100].rsplit(' ', 1)[0] + "..."
    except Exception as e:
        print(f"일반 챗봇 LLM 오류: {e}")
        response = None
    
    # OpenAI API 연동 (선택사항, 우선순위 3)
    if not response and os.getenv('OPENAI_API_KEY'):
        response = get_openai_response(user_message)
        # OpenAI 응답도 100자 이내로 제한
        if response and len(response) > 100:
            response = response[:100].rsplit(' ', 1)[0] + "..."
    
    # 기본 응답 (우선순위 4)
    if not response:
        response = "죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다. 다른 질문을 해주시거나 연락처 페이지를 확인해주세요."
    
    return jsonify({'response': response})

def get_faq_response(message):
    """
    (백업용) 간단한 FAQ 매칭 로직
    현재는 ES 기반 검색이 우선이며,
    이 함수는 검색 실패 시의 보조 수단으로만 사용될 수 있습니다.
    """
    faqs = FAQ.query.filter_by(is_active=True).all()
    message_lower = message.lower()

    # 완전 포함 매칭
    for faq in faqs:
        if faq.question.lower() in message_lower:
            return faq.answer

    # 부분 매칭
    for faq in faqs:
        words = faq.question.lower().split()
        if any(word in message_lower for word in words):
            return faq.answer

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
    faq_data = _load_faq_data()
    return render_template('chatbot/faq.html', faq_data=faq_data)

@chatbot_bp.route('/advanced')
def advanced_chat():
    """고급 AI 챗봇 페이지"""
    faq_data = _load_faq_data()
    return render_template('chatbot/advanced_chat.html', faq_data=faq_data)

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
        # 고급 챗봇은 300자 이내 상세한 답변
        max_chars = 300
        
        if search_mode == 'faq':
            # FAQ 모드 - 먼저 ES에서 FAQ/게시글 검색
            search_result = es_service.search_documents(user_message, size=5)
            related_docs = []
            response = None

            high_score_faq_answer = None

            if search_result:
                hits = search_result.get('hits', {}).get('hits', [])
                related_docs = hits
                if hits:
                    top_hit = hits[0]
                    score = top_hit.get('_score', 0)
                    source = top_hit.get('_source', {})
                    # doc_type이 faq이고 점수가 임계값 이상이면 FAQ 직접 응답 (LLM 사용 안 함)
                    if source.get('doc_type') == 'faq' and score >= 5.0:
                        high_score_faq_answer = source.get('content')

            # 점수 높은 FAQ가 있으면 바로 응답
            if high_score_faq_answer:
                return jsonify({
                    'response': high_score_faq_answer,
                    'related_docs': related_docs,
                    'mode': mode,
                    'search_mode': search_mode
                })

            # 그 외에는 ES 결과를 컨텍스트로 하여 LLM에 전달
            context = ""
            if related_docs:
                for doc in related_docs[:5]:
                    src = doc.get('_source', {})
                    title = src.get('title') or src.get('question') or ''
                    content = (src.get('content') or '')[:300]
                    context += f"제목: {title}\n내용: {content}\n\n"

            if context:
                prompt = (
                    "다음 FAQ/게시글 내용을 참고하여 사용자의 질문에 대해 최대 300자 이내로 상세하게 한국어로 답변해줘.\n\n"
                    f"[컨텍스트]\n{context}\n[질문]\n{user_message}\n[답변]"
                )
            else:
                # ES 결과가 없으면 기존 DB 기반 FAQ 매칭을 시도
                response = get_faq_response(user_message)
                if response:
                    return jsonify({
                        'response': response,
                        'mode': mode,
                        'search_mode': search_mode
                    })
                prompt = user_message

            response = llm_service.generate_response(prompt, max_length=300, mode=mode)
            if response and len(response) > max_chars:
                response = response[:max_chars].rsplit(' ', 1)[0] + "..."

            return jsonify({
                'response': response,
                'related_docs': related_docs,
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
                response = llm_service.generate_response(prompt, max_length=300, mode=mode)
            else:
                response = llm_service.generate_response(user_message, max_length=300, mode=mode)
            
            # 문자 수 제한
            if response and len(response) > max_chars:
                response = response[:max_chars].rsplit(' ', 1)[0] + "..."
            
            return jsonify({
                'response': response,
                'related_docs': related_docs,
                'mode': mode,
                'search_mode': search_mode
            })
            
        elif search_mode == 'ai':
            # AI 모드 - 순수 LLM 응답 (300자 이내 상세한 답변)
            response = llm_service.generate_response(user_message, max_length=300, mode=mode)
            
            # 문자 수 제한
            if response and len(response) > max_chars:
                response = response[:max_chars].rsplit(' ', 1)[0] + "..."
            
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
