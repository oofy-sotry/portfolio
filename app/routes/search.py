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

    suggestions = _get_es().get_suggestions(query, size=5)
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
    """RAG 기반 게시글 검색 — ChromaDB에서 관련 문서 검색 → LLM이 답변 생성"""
    query = request.args.get('q', '')
    mode = request.args.get('mode', 'concise')

    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'})

    llm = _get_llm()

    # 1. ChromaDB에서 벡터 유사도로 관련 문서 검색 (Retrieval)
    relevant_docs = []
    try:
        from app.services.vector_store import VectorStore
        vs = VectorStore()
        results = vs.search(query, n_results=5)

        if results and results.get('documents') and results['documents'][0]:
            for i, doc_text in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                relevant_docs.append({
                    'text': doc_text,
                    'title': metadata.get('title', ''),
                    'doc_type': metadata.get('doc_type', ''),
                })
    except Exception as e:
        print(f"⚠️ ChromaDB 검색 실패, ES 폴백: {e}")
        search_result = _get_es().search_documents(query, size=5)
        if search_result:
            for hit in search_result.get('hits', {}).get('hits', []):
                src = hit.get('_source', {})
                relevant_docs.append({
                    'text': src.get('content', ''),
                    'title': src.get('title', ''),
                    'doc_type': src.get('doc_type', ''),
                })

    # 2. 검색된 문서를 LLM 컨텍스트로 전달하여 답변 생성 (Augmented Generation)
    context = ""
    for doc in relevant_docs:
        title = doc.get('title', '')
        text = doc.get('text', '')[:300]
        context += f"제목: {title}\n내용: {text}\n\n"

    if context:
        prompt = f"다음 문서들을 참고하여 '{query}'에 대해 한국어로 답변해주세요:\n\n{context}"
    else:
        prompt = query

    ai_response = llm.generate_response(prompt, mode=mode)

    return jsonify({
        'query': query,
        'ai_response': ai_response,
        'relevant_docs': relevant_docs,
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
