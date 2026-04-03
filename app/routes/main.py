from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Post
from app.models.profile import Profile

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """메인 페이지"""
    # 최신 게시글 6개 가져오기
    recent_posts = Post.query.filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .limit(6).all()
    
    # 인기 게시글 5개 가져오기 (좋아요 수 기준)
    popular_posts = Post.query.filter_by(is_published=True)\
        .order_by(Post.view_count.desc())\
        .limit(5).all()
    
    return render_template('main/index.html', 
                         recent_posts=recent_posts,
                         popular_posts=popular_posts)

@main_bp.route('/about')
@login_required
def about():
    """자기소개 페이지"""
    try:
        profile = Profile.get_active_profile()
        return render_template('main/about.html', profile=profile)
    except Exception as e:
        return f"Error in about page: {str(e)}", 500

@main_bp.route('/contact')
@login_required
def contact():
    """연락처 페이지"""
    return render_template('main/contact.html')


