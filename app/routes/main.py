from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Post, Category
from app.models.profile import Profile
from app import db

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
def about():
    """자기소개 페이지"""
    try:
        profile = Profile.get_active_profile()
        return render_template('main/about.html', profile=profile)
    except Exception as e:
        return f"Error in about page: {str(e)}", 500

@main_bp.route('/contact')
def contact():
    """연락처 페이지"""
    return render_template('main/contact.html')

@main_bp.route('/search')
def search():
    """검색 페이지"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'latest')
    
    # 검색 쿼리 구성
    search_query = Post.query.filter_by(is_published=True)
    
    if query:
        search_query = search_query.filter(
            db.or_(
                Post.title.contains(query),
                Post.content.contains(query),
                Post.tags.contains(query)
            )
        )
    
    if category_id:
        search_query = search_query.filter(Post.category_id == category_id)
    
    # 정렬
    if sort_by == 'popular':
        search_query = search_query.order_by(Post.view_count.desc())
    elif sort_by == 'likes':
        # 좋아요 수로 정렬 (복잡한 쿼리 필요)
        search_query = search_query.order_by(Post.created_at.desc())
    else:  # latest
        search_query = search_query.order_by(Post.created_at.desc())
    
    posts = search_query.paginate(
        page=request.args.get('page', 1, type=int),
        per_page=10,
        error_out=False
    )
    
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('main/search.html',
                         posts=posts,
                         categories=categories,
                         query=query,
                         selected_category=category_id,
                         sort_by=sort_by)

