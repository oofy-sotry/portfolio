from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app.models import Post, Comment, Like, Category
from app import db
from datetime import datetime

board_bp = Blueprint('board', __name__)

@board_bp.route('/')
def list_posts():
    """게시글 목록"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'latest')
    
    query = Post.query.filter_by(is_published=True)
    
    if category_id:
        query = query.filter(Post.category_id == category_id)
    
    # 정렬
    if sort_by == 'popular':
        query = query.order_by(Post.view_count.desc())
    elif sort_by == 'likes':
        query = query.order_by(Post.created_at.desc())  # 임시로 최신순
    else:  # latest
        query = query.order_by(Post.created_at.desc())
    
    posts = query.paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('board/list.html',
                         posts=posts,
                         categories=categories,
                         selected_category=category_id,
                         sort_by=sort_by)

@board_bp.route('/<int:post_id>')
def view_post(post_id):
    """게시글 상세보기"""
    post = Post.query.get_or_404(post_id)
    
    # 조회수 증가
    post.view_count += 1
    db.session.commit()
    
    # 댓글 가져오기
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None)\
        .order_by(Comment.created_at.asc()).all()
    
    return render_template('board/detail.html', post=post, comments=comments)

@board_bp.route('/write', methods=['GET', 'POST'])
@login_required
def write_post():
    """게시글 작성"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        title = data.get('title')
        content = data.get('content')
        category_id = data.get('category_id', type=int)
        tags = data.get('tags', '')
        
        if not title or not content or not category_id:
            if request.is_json:
                return jsonify({'error': '제목, 내용, 카테고리를 모두 입력해주세요.'}), 400
            flash('제목, 내용, 카테고리를 모두 입력해주세요.', 'error')
            return render_template('board/write.html')
        
        post = Post(
            title=title,
            content=content,
            tags=tags,
            user_id=current_user.id,
            category_id=category_id
        )
        
        try:
            db.session.add(post)
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': '게시글이 작성되었습니다.', 'redirect': url_for('board.view_post', post_id=post.id)})
            flash('게시글이 작성되었습니다.', 'success')
            return redirect(url_for('board.view_post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': '게시글 작성 중 오류가 발생했습니다.'}), 500
            flash('게시글 작성 중 오류가 발생했습니다.', 'error')
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('board/write.html', categories=categories)

@board_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """게시글 수정"""
    post = Post.query.get_or_404(post_id)
    
    # 권한 체크
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.tags = data.get('tags', post.tags)
        post.category_id = data.get('category_id', post.category_id, type=int)
        
        try:
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': '게시글이 수정되었습니다.', 'redirect': url_for('board.view_post', post_id=post.id)})
            flash('게시글이 수정되었습니다.', 'success')
            return redirect(url_for('board.view_post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': '게시글 수정 중 오류가 발생했습니다.'}), 500
            flash('게시글 수정 중 오류가 발생했습니다.', 'error')
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('board/edit.html', post=post, categories=categories)

@board_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """게시글 삭제"""
    post = Post.query.get_or_404(post_id)
    
    # 권한 체크
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    try:
        db.session.delete(post)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': '게시글이 삭제되었습니다.', 'redirect': url_for('board.list_posts')})
        flash('게시글이 삭제되었습니다.', 'success')
        return redirect(url_for('board.list_posts'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': '게시글 삭제 중 오류가 발생했습니다.'}), 500
        flash('게시글 삭제 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('board.view_post', post_id=post_id))

@board_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """좋아요 토글"""
    post = Post.query.get_or_404(post_id)
    
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        liked = True
    
    try:
        db.session.commit()
        return jsonify({'liked': liked, 'like_count': post.get_like_count()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '좋아요 처리 중 오류가 발생했습니다.'}), 500

@board_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """댓글 작성"""
    post = Post.query.get_or_404(post_id)
    data = request.get_json() if request.is_json else request.form
    content = data.get('content')
    parent_id = data.get('parent_id', type=int)
    
    if not content:
        if request.is_json:
            return jsonify({'error': '댓글 내용을 입력해주세요.'}), 400
        flash('댓글 내용을 입력해주세요.', 'error')
        return redirect(url_for('board.view_post', post_id=post_id))
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id if parent_id else None
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': '댓글이 작성되었습니다.'})
        flash('댓글이 작성되었습니다.', 'success')
        return redirect(url_for('board.view_post', post_id=post_id))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': '댓글 작성 중 오류가 발생했습니다.'}), 500
        flash('댓글 작성 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('board.view_post', post_id=post_id))
