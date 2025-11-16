from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models.profile import Profile
from app import db
import json
import os
import uuid
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# 이미지 업로드 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_image(file):
    """프로필 이미지 저장"""
    if file and allowed_file(file.filename):
        # 안전한 파일명 생성
        filename = secure_filename(file.filename)
        # 고유한 파일명 생성 (중복 방지)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # 업로드 폴더 경로
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_images')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 파일 저장
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def delete_profile_image(filename):
    """프로필 이미지 삭제"""
    if filename:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_images')
        file_path = os.path.join(upload_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

@profile_bp.route('/')
@login_required
def manage():
    """프로필 관리 페이지"""
    try:
        profile = Profile.get_active_profile()
        return render_template('profile/manage.html', profile=profile)
    except Exception as e:
        return f"Error in manage: {str(e)}", 500

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """프로필 편집"""
    try:
        profile = Profile.get_active_profile()
    except Exception as e:
        return f"Error getting profile: {str(e)}", 500
    
    if request.method == 'POST':
        try:
            # 기본 정보 업데이트
            profile.name = request.form.get('name', profile.name)
            profile.title = request.form.get('title', profile.title)
            profile.bio = request.form.get('bio', profile.bio)
            
            # 이미지 업로드 처리
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename:
                    # 파일 크기 확인
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_FILE_SIZE:
                        flash('파일 크기가 5MB를 초과합니다.', 'error')
                        return redirect(url_for('profile.edit'))
                    
                    # 기존 이미지 삭제
                    if profile.profile_image_filename:
                        delete_profile_image(profile.profile_image_filename)
                    
                    # 새 이미지 저장
                    new_filename = save_profile_image(file)
                    if new_filename:
                        profile.profile_image_filename = new_filename
                        profile.profile_image_url = None  # URL 방식 비활성화
                    else:
                        flash('지원하지 않는 파일 형식입니다. (PNG, JPG, JPEG, GIF, WEBP만 허용)', 'error')
                        return redirect(url_for('profile.edit'))
            
            # URL 방식 이미지 (기존 방식 유지)
            profile.profile_image_url = request.form.get('profile_image_url', profile.profile_image_url)
            
            # 기술 스택 업데이트
            skills_data = {
                'backend': request.form.getlist('backend_skills'),
                'frontend': request.form.getlist('frontend_skills'),
                'devops': request.form.getlist('devops_skills'),
                'other': request.form.getlist('other_skills')
            }
            profile.skills = skills_data
            
            # 경력/프로젝트 업데이트
            experiences = []
            experience_count = int(request.form.get('experience_count', 0))
            
            for i in range(experience_count):
                title = request.form.get(f'exp_title_{i}')
                period = request.form.get(f'exp_period_{i}')
                description = request.form.get(f'exp_description_{i}')
                technologies = request.form.getlist(f'exp_technologies_{i}')
                
                if title and period and description:
                    experiences.append({
                        'title': title,
                        'period': period,
                        'description': description,
                        'technologies': technologies
                    })
            
            profile.experiences = experiences
            
            # 연락처 정보 업데이트
            contact_info = {
                'email': request.form.get('email', ''),
                'github': request.form.get('github', ''),
                'linkedin': request.form.get('linkedin', ''),
                'website': request.form.get('website', '')
            }
            profile.contact_info = contact_info
            
            db.session.commit()
            flash('프로필이 성공적으로 업데이트되었습니다!', 'success')
            return redirect(url_for('profile.manage'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'프로필 업데이트 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return render_template('profile/edit.html', profile=profile)

@profile_bp.route('/api/skills', methods=['POST'])
@login_required
def add_skill():
    """기술 스택 추가 (AJAX)"""
    try:
        profile = Profile.get_active_profile()
        category = request.json.get('category')
        skill = request.json.get('skill')
        
        if not category or not skill:
            return jsonify({'success': False, 'message': '카테고리와 기술명이 필요합니다.'})
        
        if not profile.skills:
            profile.skills = {}
        
        if category not in profile.skills:
            profile.skills[category] = []
        
        if skill not in profile.skills[category]:
            profile.skills[category].append(skill)
            db.session.commit()
            return jsonify({'success': True, 'message': '기술이 추가되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '이미 존재하는 기술입니다.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@profile_bp.route('/api/skills', methods=['DELETE'])
@login_required
def remove_skill():
    """기술 스택 제거 (AJAX)"""
    try:
        profile = Profile.get_active_profile()
        category = request.json.get('category')
        skill = request.json.get('skill')
        
        if category in profile.skills and skill in profile.skills[category]:
            profile.skills[category].remove(skill)
            db.session.commit()
            return jsonify({'success': True, 'message': '기술이 제거되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '기술을 찾을 수 없습니다.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@profile_bp.route('/api/experience', methods=['POST'])
@login_required
def add_experience():
    """경력/프로젝트 추가 (AJAX)"""
    try:
        profile = Profile.get_active_profile()
        data = request.json
        
        if not profile.experiences:
            profile.experiences = []
        
        new_experience = {
            'title': data.get('title'),
            'period': data.get('period'),
            'description': data.get('description'),
            'technologies': data.get('technologies', [])
        }
        
        profile.experiences.append(new_experience)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '경력이 추가되었습니다.',
            'experience': new_experience
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@profile_bp.route('/api/experience/<int:index>', methods=['DELETE'])
@login_required
def remove_experience(index):
    """경력/프로젝트 제거 (AJAX)"""
    try:
        profile = Profile.get_active_profile()
        
        if profile.experiences and 0 <= index < len(profile.experiences):
            removed = profile.experiences.pop(index)
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': '경력이 제거되었습니다.',
                'removed': removed
            })
        else:
            return jsonify({'success': False, 'message': '경력을 찾을 수 없습니다.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@profile_bp.route('/delete-image', methods=['POST'])
@login_required
def delete_image():
    """프로필 이미지 삭제"""
    try:
        profile = Profile.get_active_profile()
        
        # 기존 이미지 파일 삭제
        if profile.profile_image_filename:
            delete_profile_image(profile.profile_image_filename)
            profile.profile_image_filename = None
        
        # URL 방식 이미지도 삭제
        profile.profile_image_url = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '프로필 이미지가 삭제되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'이미지 삭제 중 오류가 발생했습니다: {str(e)}'
        })

@profile_bp.route('/preview')
@login_required
def preview():
    """프로필 미리보기"""
    profile = Profile.get_active_profile()
    return render_template('main/about.html', profile=profile)
