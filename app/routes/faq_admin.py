from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import FAQ
from app.services.elasticsearch_service import ElasticsearchService

faq_admin_bp = Blueprint('faq_admin', __name__, url_prefix='/admin/faq')


def _index_faq_to_es(faq: FAQ):
    """FAQ를 Elasticsearch에 인덱싱"""
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


def _delete_faq_from_es(faq_id: int):
    """FAQ를 Elasticsearch에서 삭제"""
    es = ElasticsearchService()
    es.delete_document(f"faq-{faq_id}")


@faq_admin_bp.before_request
@login_required
def require_admin():
    """관리자 전용 보호"""
    if not current_user.is_admin:
        flash("접근 권한이 없습니다.", "error")
        return redirect(url_for("main.index"))


@faq_admin_bp.route("/", methods=["GET"])
def manage():
    """FAQ 관리 목록 페이지"""
    faqs = FAQ.query.order_by(FAQ.id.asc()).all()
    return render_template("faq/manage.html", faqs=faqs)


@faq_admin_bp.route("/create", methods=["POST"])
def create():
    """FAQ 생성"""
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
    category = request.form.get("category", "").strip() or None

    if not question or not answer:
        flash("질문과 답변을 모두 입력해주세요.", "error")
        return redirect(url_for("faq_admin.manage"))

    faq = FAQ(question=question, answer=answer, category=category)
    try:
        db.session.add(faq)
        db.session.commit()
        _index_faq_to_es(faq)
        flash("FAQ가 추가되었습니다.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"FAQ 추가 중 오류가 발생했습니다: {e}", "error")

    return redirect(url_for("faq_admin.manage"))


@faq_admin_bp.route("/<int:faq_id>/update", methods=["POST"])
def update(faq_id):
    """FAQ 수정"""
    faq = FAQ.query.get_or_404(faq_id)

    faq.question = request.form.get("question", faq.question).strip()
    faq.answer = request.form.get("answer", faq.answer).strip()
    category = request.form.get("category", "").strip()
    faq.category = category or None
    faq.is_active = request.form.get("is_active") == "on"

    try:
        db.session.commit()
        _index_faq_to_es(faq)
        flash("FAQ가 수정되었습니다.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"FAQ 수정 중 오류가 발생했습니다: {e}", "error")

    return redirect(url_for("faq_admin.manage"))


@faq_admin_bp.route("/<int:faq_id>/delete", methods=["POST"])
def delete(faq_id):
    """FAQ 삭제"""
    faq = FAQ.query.get_or_404(faq_id)
    try:
        db.session.delete(faq)
        db.session.commit()
        _delete_faq_from_es(faq_id)
        flash("FAQ가 삭제되었습니다.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"FAQ 삭제 중 오류가 발생했습니다: {e}", "error")

    return redirect(url_for("faq_admin.manage"))


