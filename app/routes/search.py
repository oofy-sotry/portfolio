"""
고급 검색 기능 라우트
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.elasticsearch_service import ElasticsearchService
from app.services.llm_service import LLMService
from app.models import Post, Category
from app import db

search_bp = Blueprint('search', __name__)

# 서비스 인스턴스
es_service = ElasticsearchService()
llm_service = LLMService()

@search_bp.route('/search')
def advanced_search():
    """고급 검색 페이지"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    tags = request.args.get('tags', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    sort_by = request.args.get('sort', 'relevance')
    
    # 검색 결과
    results = None
    total = 0
    suggestions = []
    
    if query:
        # 필터 설정
        filters = {}
        if category:
            filters['category'] = category
        if tags:
            filters['tags'] = tags.split(',')
        if date_from and date_to:
            filters['date_range'] = {
                'from': date_from,
                'to': date_to
            }
        
        # Elasticsearch 검색
        search_result = es_service.search_documents(
            query=query,
            filters=filters,
            size=20
        )
        
        if search_result:
            results = search_result.get('hits', {}).get('hits', [])
            total = search_result.get('hits', {}).get('total', {}).get('value', 0)
        
        # 검색어 자동완성
        suggestions = es_service.get_suggestions(query, size=5)
    
    # 카테고리 목록
    categories = Category.query.filter_by(is_active=True).all()
    
    # 인기 검색어
    popular_searches = es_service.get_popular_searches()
    
    return render_template('search/advanced.html',
                         query=query,
                         results=results,
                         total=total,
                         suggestions=suggestions,
                         categories=categories,
                         popular_searches=popular_searches,
                         selected_category=category,
                         selected_tags=tags,
                         date_from=date_from,
                         date_to=date_to,
                         sort_by=sort_by)

@search_bp.route('/api/search/suggestions')
def search_suggestions():
    """검색어 자동완성 API"""
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    suggestions = es_service.get_suggestions(query, size=10)
    return jsonify([s['text'] for s in suggestions])

@search_bp.route('/api/search/related')
def related_documents():
    """관련 문서 추천 API"""
    doc_id = request.args.get('id')
    
    if not doc_id:
        return jsonify([])
    
    related_docs = es_service.get_related_documents(doc_id, size=5)
    return jsonify(related_docs)

@search_bp.route('/api/search/popular')
def popular_searches():
    """인기 검색어 API"""
    popular = es_service.get_popular_searches()
    return jsonify(popular)

@search_bp.route('/search/ai')
def ai_search():
    """AI 기반 검색"""
    query = request.args.get('q', '')
    mode = request.args.get('mode', 'concise')  # concise 또는 detailed
    
    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'})
    
    # 1. Elasticsearch로 관련 문서 검색
    search_result = es_service.search_documents(query, size=5)
    relevant_docs = []
    
    if search_result:
        relevant_docs = search_result.get('hits', {}).get('hits', [])
    
    # 2. 관련 문서 요약
    summarized_docs = []
    for doc in relevant_docs:
        content = doc['_source'].get('content', '')
        summary = llm_service.summarize_text(content, max_length=100)
        doc['_source']['summary'] = summary
        summarized_docs.append(doc)
    
    # 3. LLM으로 최종 응답 생성
    context = ""
    for doc in summarized_docs:
        context += f"제목: {doc['_source'].get('title', '')}\n"
        context += f"요약: {doc['_source'].get('summary', '')}\n\n"
    
    prompt = f"다음 문서들을 참고하여 '{query}'에 대해 답변해주세요:\n\n{context}"
    
    ai_response = llm_service.generate_response(prompt, mode=mode)
    
    return jsonify({
        'query': query,
        'ai_response': ai_response,
        'relevant_docs': summarized_docs,
        'mode': mode
    })

@search_bp.route('/search/semantic')
def semantic_search():
    """의미 기반 검색"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'})
    
    # 1. 쿼리 임베딩 생성
    query_embedding = llm_service.get_embeddings([query])
    
    if query_embedding is None:
        # 임베딩 실패 시 일반 검색으로 폴백
        search_result = es_service.search_documents(query, size=10)
        return jsonify({
            'query': query,
            'results': search_result.get('hits', {}).get('hits', []) if search_result else [],
            'type': 'fallback'
        })
    
    # 2. 의미 기반 검색 (실제 구현에서는 벡터 데이터베이스 사용)
    # 여기서는 Elasticsearch의 more_like_this 쿼리 사용
    search_result = es_service.search_documents(query, size=10)
    
    return jsonify({
        'query': query,
        'results': search_result.get('hits', {}).get('hits', []) if search_result else [],
        'type': 'semantic'
    })
