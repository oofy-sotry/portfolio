"""
문서 인덱싱 유틸리티
게시글, FAQ 등의 문서를 Elasticsearch와 ChromaDB에 동기화하는 공통 함수
"""

from app.services.elasticsearch_service import ElasticsearchService
from app.services.vector_store import VectorStore


def index_post_to_es(post):
    """
    게시글을 Elasticsearch와 ChromaDB에 인덱싱

    Args:
        post: Post 모델 인스턴스

    Returns:
        bool: 인덱싱 성공 여부
    """
    try:
        es = ElasticsearchService()
        es.create_index()
        doc = {
            "doc_type": "post",
            "title": post.title,
            "content": post.content,
            "tags": post.get_tags_list(),
            "category": post.category.name if post.category else None,
            "author": post.author.username if post.author else None,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "view_count": post.view_count,
            "like_count": post.get_like_count(),
            "post_id": post.id,
        }
        es.index_document(f"post-{post.id}", doc)
    except Exception as e:
        print(f"❌ 게시글 ES 인덱싱 실패: {e}")

    # ChromaDB 벡터 저장
    try:
        vs = VectorStore()
        text = f"{post.title}\n{post.content}"
        metadata = {
            "doc_type": "post",
            "post_id": post.id,
            "title": post.title,
            "category": post.category.name if post.category else "",
        }
        vs.add_document(f"post-{post.id}", text, metadata)
    except Exception as e:
        print(f"❌ 게시글 ChromaDB 인덱싱 실패: {e}")

    return True


def index_faq_to_es(faq):
    """
    FAQ를 Elasticsearch와 ChromaDB에 인덱싱

    Args:
        faq: FAQ 모델 인스턴스

    Returns:
        bool: 인덱싱 성공 여부
    """
    try:
        es = ElasticsearchService()
        es.create_index()
        doc = {
            "doc_type": "faq",
            "title": faq.question,
            "content": faq.answer,
            "category": faq.category,
            "created_at": faq.created_at.isoformat() if faq.created_at else None,
            "faq_id": faq.id,
        }
        es.index_document(f"faq-{faq.id}", doc)
    except Exception as e:
        print(f"❌ FAQ ES 인덱싱 실패: {e}")

    # ChromaDB 벡터 저장
    try:
        vs = VectorStore()
        text = f"{faq.question}\n{faq.answer}"
        metadata = {
            "doc_type": "faq",
            "faq_id": faq.id,
            "title": faq.question,
        }
        vs.add_document(f"faq-{faq.id}", text, metadata)
    except Exception as e:
        print(f"❌ FAQ ChromaDB 인덱싱 실패: {e}")

    return True


def delete_post_from_es(post_id):
    """게시글을 Elasticsearch와 ChromaDB에서 삭제"""
    try:
        es = ElasticsearchService()
        es.delete_document(f"post-{post_id}")
    except Exception as e:
        print(f"❌ 게시글 ES 삭제 실패: {e}")

    try:
        vs = VectorStore()
        vs.delete_document(f"post-{post_id}")
    except Exception as e:
        print(f"❌ 게시글 ChromaDB 삭제 실패: {e}")

    return True


def delete_faq_from_es(faq_id):
    """FAQ를 Elasticsearch와 ChromaDB에서 삭제"""
    try:
        es = ElasticsearchService()
        es.delete_document(f"faq-{faq_id}")
    except Exception as e:
        print(f"❌ FAQ ES 삭제 실패: {e}")

    try:
        vs = VectorStore()
        vs.delete_document(f"faq-{faq_id}")
    except Exception as e:
        print(f"❌ FAQ ChromaDB 삭제 실패: {e}")

    return True


def update_post_in_es(post):
    """게시글을 Elasticsearch와 ChromaDB에서 업데이트"""
    try:
        es = ElasticsearchService()
        doc = {
            "doc_type": "post",
            "title": post.title,
            "content": post.content,
            "tags": post.get_tags_list(),
            "category": post.category.name if post.category else None,
            "author": post.author.username if post.author else None,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "view_count": post.view_count,
            "like_count": post.get_like_count(),
            "post_id": post.id,
        }
        es.update_document(f"post-{post.id}", doc)
    except Exception as e:
        print(f"❌ 게시글 ES 업데이트 실패: {e}")

    # ChromaDB 벡터 업데이트 (upsert)
    try:
        vs = VectorStore()
        text = f"{post.title}\n{post.content}"
        metadata = {
            "doc_type": "post",
            "post_id": post.id,
            "title": post.title,
            "category": post.category.name if post.category else "",
        }
        vs.add_document(f"post-{post.id}", text, metadata)
    except Exception as e:
        print(f"❌ 게시글 ChromaDB 업데이트 실패: {e}")

    return True

