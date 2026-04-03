"""
ChromaDB 벡터 스토어 서비스
게시글/FAQ를 임베딩 벡터로 저장하고 유사도 검색을 수행
"""

import chromadb
import os


class VectorStore:
    def __init__(self):
        host = os.getenv('CHROMADB_HOST', 'chromadb')
        port = int(os.getenv('CHROMADB_PORT', '8000'))
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection_name = 'portfolio_documents'

    def _get_collection(self):
        """컬렉션 반환 (없으면 생성)"""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_document(self, doc_id, text, metadata=None):
        """문서를 벡터로 변환하여 저장"""
        collection = self._get_collection()
        collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )

    def search(self, query_text, n_results=5, where=None):
        """텍스트 유사도 검색"""
        collection = self._get_collection()
        params = {
            "query_texts": [query_text],
            "n_results": n_results
        }
        if where:
            params["where"] = where

        results = collection.query(**params)
        return results

    def delete_document(self, doc_id):
        """문서 삭제"""
        collection = self._get_collection()
        collection.delete(ids=[doc_id])

    def get_document_count(self):
        """저장된 문서 수 반환"""
        collection = self._get_collection()
        return collection.count()
