"""
Elasticsearch 인덱싱 유틸리티
게시글, FAQ 등의 문서를 Elasticsearch에 인덱싱하는 공통 함수
"""

from app.services.elasticsearch_service import ElasticsearchService


def index_post_to_es(post):
    """
    게시글을 Elasticsearch에 인덱싱
    
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
        return es.index_document(f"post-{post.id}", doc)
    except Exception as e:
        print(f"❌ 게시글 Elasticsearch 인덱싱 실패: {e}")
        return False


def index_faq_to_es(faq):
    """
    FAQ를 Elasticsearch에 인덱싱
    
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
        return es.index_document(f"faq-{faq.id}", doc)
    except Exception as e:
        print(f"❌ FAQ Elasticsearch 인덱싱 실패: {e}")
        return False


def delete_post_from_es(post_id):
    """
    게시글을 Elasticsearch에서 삭제
    
    Args:
        post_id: 게시글 ID
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        es = ElasticsearchService()
        return es.delete_document(f"post-{post_id}")
    except Exception as e:
        print(f"❌ 게시글 Elasticsearch 삭제 실패: {e}")
        return False


def delete_faq_from_es(faq_id):
    """
    FAQ를 Elasticsearch에서 삭제
    
    Args:
        faq_id: FAQ ID
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        es = ElasticsearchService()
        return es.delete_document(f"faq-{faq_id}")
    except Exception as e:
        print(f"❌ FAQ Elasticsearch 삭제 실패: {e}")
        return False


def update_post_in_es(post):
    """
    게시글을 Elasticsearch에서 업데이트
    
    Args:
        post: Post 모델 인스턴스
    
    Returns:
        bool: 업데이트 성공 여부
    """
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
        return es.update_document(f"post-{post.id}", doc)
    except Exception as e:
        print(f"❌ 게시글 Elasticsearch 업데이트 실패: {e}")
        return False

