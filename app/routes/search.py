"""
검색 기능 라우트
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.elasticsearch_service import ElasticsearchService
from app.models import Category

search_bp = Blueprint('search', __name__)


def _get_es():
    """ElasticsearchService 인스턴스 반환"""
    return ElasticsearchService()


def _get_llm():
    """LLMService 인스턴스 반환 (요청 시에만 로딩)"""
    from app.services.llm_service import LLMService
    return LLMService()


@search_bp.route('/')
def advanced_search():
    """검색 페이지"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    tags = request.args.get('tags', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    sort_by = request.args.get('sort', 'relevance')

    results = None
    total = 0

    if query:
        filters = {}
        if category:
            filters['category'] = category
        if tags:
            filters['tags'] = [t.strip() for t in tags.split(',')]
        if date_from and date_to:
            filters['date_range'] = {'from': date_from, 'to': date_to}

        search_result = _get_es().search_documents(
            query=query, filters=filters, size=20
        )

        if search_result:
            results = search_result.get('hits', {}).get('hits', [])
            total = search_result.get('hits', {}).get('total', {}).get('value', 0)

    categories = Category.query.filter_by(is_active=True).all()
    popular_searches = _get_es().get_popular_searches()

    return render_template('search/advanced.html',
                         query=query,
                         results=results,
                         total=total,
                         categories=categories,
                         popular_searches=popular_searches,
                         selected_category=category,
                         selected_tags=tags,
                         date_from=date_from,
                         date_to=date_to,
                         sort_by=sort_by)


@search_bp.route('/api/suggestions')
def search_suggestions():
    """검색어 자동완성 API"""
    query = request.args.get('q', '')

    if not query or len(query) < 2:
        return jsonify([])

    # prefix 매칭으로 제목 검색
    search_result = _get_es().search_documents(query, size=5)

    suggestions = []
    if search_result:
        hits = search_result.get('hits', {}).get('hits', [])
        for hit in hits:
            title = hit.get('_source', {}).get('title', '')
            if title and title not in suggestions:
                suggestions.append(title)

    return jsonify(suggestions)


@search_bp.route('/api/related')
def related_documents():
    """관련 문서 추천 API"""
    doc_id = request.args.get('id')

    if not doc_id:
        return jsonify([])

    related_docs = _get_es().get_related_documents(doc_id, size=5)
    return jsonify(related_docs)


@search_bp.route('/api/popular')
def popular_searches():
    """인기 검색어 API"""
    popular = _get_es().get_popular_searches()
    return jsonify(popular)


@search_bp.route('/ai')
def ai_search():
    """AI 기반 게시글 검색 — ES 결과를 LLM이 요약하여 응답"""
    query = request.args.get('q', '')
    mode = request.args.get('mode', 'concise')

    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'})

    es = _get_es()
    llm = _get_llm()

    # 1. Elasticsearch로 관련 게시글 검색
    search_result = es.search_documents(query, size=5)
    relevant_docs = []

    if search_result:
        relevant_docs = search_result.get('hits', {}).get('hits', [])

    # 2. 관련 문서 요약
    summarized_docs = []
    for doc in relevant_docs:
        content = doc['_source'].get('content', '')
        summary = llm.summarize_text(content, max_length=100)
        doc['_source']['summary'] = summary
        summarized_docs.append(doc)

    # 3. LLM으로 최종 응답 생성
    context = ""
    for doc in summarized_docs:
        context += f"제목: {doc['_source'].get('title', '')}\n"
        context += f"요약: {doc['_source'].get('summary', '')}\n\n"

    prompt = f"다음 문서들을 참고하여 '{query}'에 대해 답변해주세요:\n\n{context}"
    ai_response = llm.generate_response(prompt, mode=mode)

    return jsonify({
        'query': query,
        'ai_response': ai_response,
        'relevant_docs': summarized_docs,
        'mode': mode
    })


@search_bp.route('/semantic')
def semantic_search():
    """의미 기반 게시글 검색 — ChromaDB 벡터 유사도"""
    query = request.args.get('q', '')

    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'})

    try:
        from app.services.vector_store import VectorStore
        vs = VectorStore()
        results = vs.search(query, n_results=10)

        docs = []
        if results and results.get('ids') and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                distance = results['distances'][0][i] if results.get('distances') else 0
                docs.append({
                    '_id': doc_id,
                    '_source': metadata,
                    '_score': round(1 - distance, 4),
                    '_document': results['documents'][0][i] if results.get('documents') else ''
                })

        return jsonify({
            'query': query,
            'results': docs,
            'type': 'semantic'
        })

    except Exception as e:
        print(f"❌ 시맨틱 검색 실패, ES 폴백: {e}")
        search_result = _get_es().search_documents(query, size=10)
        return jsonify({
            'query': query,
            'results': search_result.get('hits', {}).get('hits', []) if search_result else [],
            'type': 'fallback'
        })
