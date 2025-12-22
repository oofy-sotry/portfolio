from datetime import datetime
from app import db


class FAQ(db.Model):
    """FAQ 모델"""
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False, unique=True)
    answer = db.Column(db.Text, nullable=False)
    # 검색 가중치나 카테고리 분류가 필요하면 추후 확장 가능
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FAQ {self.question}>'


