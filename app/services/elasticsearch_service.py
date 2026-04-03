"""
Elasticsearch 검색 서비스
"""

from elasticsearch import Elasticsearch
from flask import current_app
import json
import os

class ElasticsearchService:
    def __init__(self):
        self.es = Elasticsearch(
            [os.getenv('ELASTICSEARCH_URL', 'http://elasticsearch:9200')],
            timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )
        self.index_name = 'portfolio_documents'
    
    def create_index(self):
        """Elasticsearch 인덱스 생성"""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "doc_type": {
                            "type": "keyword"  # 'faq' 또는 'post'
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "tags": {
                            "type": "keyword"
                        },
                        "category": {
                            "type": "keyword"
                        },
                        "author": {
                            "type": "keyword"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "view_count": {
                            "type": "integer"
                        },
                        "like_count": {
                            "type": "integer"
                        },
                        "faq_id": {
                            "type": "integer"
                        },
                        "post_id": {
                            "type": "integer"
                        },
                        "score_hint": {
                            "type": "float"
                        }
                    }
                }
            }
            
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"✅ Elasticsearch 인덱스 '{self.index_name}' 생성됨")
    
    def index_document(self, doc_id, document):
        """문서 인덱싱"""
        try:
            self.es.index(
                index=self.index_name,
                id=doc_id,
                body=document
            )
            return True
        except Exception as e:
            print(f"❌ 문서 인덱싱 실패: {e}")
            return False
    
    def search_documents(self, query, filters=None, size=10, from_=0):
        """문서 검색"""
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content", "tags"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},
                {"created_at": {"order": "desc"}}
            ],
            "size": size,
            "from": from_
        }
        
        # 필터 추가
        if filters:
            filter_conditions = []
            if filters.get('category'):
                filter_conditions.append({
                    "term": {"category": filters['category']}
                })
            if filters.get('tags'):
                filter_conditions.append({
                    "terms": {"tags": filters['tags']}
                })
            if filters.get('date_range'):
                filter_conditions.append({
                    "range": {
                        "created_at": {
                            "gte": filters['date_range']['from'],
                            "lte": filters['date_range']['to']
                        }
                    }
                })
            
            if filter_conditions:
                search_body["query"]["bool"]["filter"] = filter_conditions
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            return response
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return None
    
    def get_suggestions(self, query, size=5):
        """검색어 자동완성 — prefix 매칭으로 제목 검색"""
        search_body = {
            "query": {
                "match_phrase_prefix": {
                    "title": {
                        "query": query,
                        "max_expansions": 10
                    }
                }
            },
            "_source": ["title"],
            "size": size
        }

        try:
            response = self.es.search(index=self.index_name, body=search_body)
            hits = response.get('hits', {}).get('hits', [])
            return [hit['_source']['title'] for hit in hits]
        except Exception as e:
            print(f"❌ 자동완성 실패: {e}")
            return []
    
    def get_related_documents(self, doc_id, size=5):
        """관련 문서 추천"""
        try:
            # 문서 정보 가져오기
            doc = self.es.get(index=self.index_name, id=doc_id)
            doc_source = doc['_source']
            
            # 유사 문서 검색
            related_query = {
                "query": {
                    "more_like_this": {
                        "fields": ["title", "content", "tags"],
                        "like": [
                            {
                                "_index": self.index_name,
                                "_id": doc_id
                            }
                        ],
                        "min_term_freq": 1,
                        "max_query_terms": 12
                    }
                },
                "size": size
            }
            
            response = self.es.search(index=self.index_name, body=related_query)
            return response.get('hits', {}).get('hits', [])
        except Exception as e:
            print(f"❌ 관련 문서 검색 실패: {e}")
            return []
    
    def get_popular_searches(self, size=10):
        """인기 검색어 — ES 인덱스에서 자주 등장하는 태그/카테고리 추출"""
        agg_body = {
            "size": 0,
            "aggs": {
                "popular_tags": {
                    "terms": {
                        "field": "tags",
                        "size": size
                    }
                }
            }
        }

        try:
            response = self.es.search(index=self.index_name, body=agg_body)
            buckets = response.get('aggregations', {}).get('popular_tags', {}).get('buckets', [])
            if buckets:
                return [bucket['key'] for bucket in buckets]
        except Exception as e:
            print(f"⚠️ 인기 검색어 조회 실패: {e}")

        # ES 데이터가 없으면 기본값
        return ["Python", "Flask", "Docker", "MySQL", "JavaScript"]
    
    def delete_document(self, doc_id):
        """문서 삭제"""
        try:
            self.es.delete(index=self.index_name, id=doc_id)
            return True
        except Exception as e:
            print(f"❌ 문서 삭제 실패: {e}")
            return False
    
    def update_document(self, doc_id, document):
        """문서 업데이트"""
        try:
            self.es.index(
                index=self.index_name,
                id=doc_id,
                body=document
            )
            return True
        except Exception as e:
            print(f"❌ 문서 업데이트 실패: {e}")
            return False
