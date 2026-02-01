from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import User
from app import db
import re
import os
import requests
import urllib.parse

auth_bp = Blueprint('auth', __name__)

# Keycloak 설정
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'portfolio')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'portfolio-web')
# 보안: 환경 변수에서만 시크릿 키를 가져옴 (기본값 없음)
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET')
if not KEYCLOAK_CLIENT_SECRET:
    print("⚠️ 경고: KEYCLOAK_CLIENT_SECRET 환경 변수가 설정되지 않았습니다.")

def get_keycloak_url():
    """동적으로 Keycloak URL 생성"""
    keycloak_url = os.getenv('KEYCLOAK_URL')
    if keycloak_url:
        return keycloak_url
    
    # 환경 변수가 없으면 현재 요청의 호스트를 사용
    from flask import request
    if request:
        host = request.host.split(':')[0]  # 포트 제거
        return f"http://{host}:8080"
    
    # 기본값
    return 'http://localhost:8080'

@auth_bp.route('/keycloak-login')
def keycloak_login():
    """Keycloak 로그인"""
    # Keycloak 인증 URL 생성
    keycloak_url = get_keycloak_url()
    auth_url = f"{keycloak_url}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
    
    # 디버깅 로그
    print(f"🔍 Keycloak URL: {keycloak_url}")
    print(f"🔍 Auth URL: {auth_url}")
    print(f"🔍 Redirect URI: {request.url_root}auth/keycloak-callback")
    params = {
        'client_id': KEYCLOAK_CLIENT_ID,
        'redirect_uri': request.url_root + 'auth/keycloak-callback',
        'response_type': 'code',
        'scope': 'openid profile email'
    }
    
    auth_url_with_params = auth_url + '?' + urllib.parse.urlencode(params)
    return redirect(auth_url_with_params)

@auth_bp.route('/keycloak-callback')
def keycloak_callback():
    """Keycloak 콜백"""
    code = request.args.get('code')
    if not code:
        flash('인증에 실패했습니다.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # 토큰 교환
        keycloak_url = get_keycloak_url()
        token_url = f"{keycloak_url}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
        # Keycloak 클라이언트 시크릿 확인
        if not KEYCLOAK_CLIENT_SECRET:
            flash('Keycloak 설정이 올바르지 않습니다. 관리자에게 문의하세요.', 'error')
            return redirect(url_for('auth.login'))
        
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': KEYCLOAK_CLIENT_ID,
            'client_secret': KEYCLOAK_CLIENT_SECRET,
            'code': code,
            'redirect_uri': request.url_root + 'auth/keycloak-callback'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # 사용자 정보 가져오기
        userinfo_url = f"{keycloak_url}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        # 디버깅 로그
        print(f"🔍 Keycloak UserInfo: {userinfo}")
        print(f"🔍 Preferred Username: {userinfo.get('preferred_username')}")
        print(f"🔍 Email: {userinfo.get('email')}")
        
        # 사용자 생성 또는 업데이트
        user = User.query.filter_by(username=userinfo.get('preferred_username')).first()
        if not user:
            user = User(
                username=userinfo.get('preferred_username'),
                email=userinfo.get('email'),
                password_hash=None,  # Keycloak 사용자는 비밀번호 없음
                is_keycloak_user=True
            )
            db.session.add(user)
            db.session.commit()
        else:
            # 기존 사용자가 Keycloak 사용자로 업데이트되지 않은 경우 업데이트
            if not user.is_keycloak_user:
                user.is_keycloak_user = True
                user.password_hash = None
                db.session.commit()
        
        # 로그인
        login_user(user)
        flash('Keycloak 로그인 성공!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash(f'Keycloak 인증 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': '사용자명과 비밀번호를 입력해주세요.'}), 400
            flash('사용자명과 비밀번호를 입력해주세요.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        # Keycloak 사용자는 일반 로그인 불가
        if user and user.is_keycloak_user:
            if request.is_json:
                return jsonify({'error': 'Keycloak 사용자는 Keycloak 로그인을 사용해주세요.'}), 401
            flash('Keycloak 사용자는 Keycloak 로그인을 사용해주세요.', 'error')
        elif user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({'message': '로그인 성공', 'redirect': url_for('main.index')})
            return redirect(url_for('main.index'))
        else:
            if request.is_json:
                return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다.'}), 401
            flash('잘못된 사용자명 또는 비밀번호입니다.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # 유효성 검사
        errors = []
        
        if not username or len(username) < 3:
            errors.append('사용자명은 3자 이상이어야 합니다.')
        
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('올바른 이메일 주소를 입력해주세요.')
        
        if not password or len(password) < 6:
            errors.append('비밀번호는 6자 이상이어야 합니다.')
        
        if password != confirm_password:
            errors.append('비밀번호가 일치하지 않습니다.')
        
        # 중복 체크
        if User.query.filter_by(username=username).first():
            errors.append('이미 사용 중인 사용자명입니다.')
        
        if User.query.filter_by(email=email).first():
            errors.append('이미 사용 중인 이메일입니다.')
        
        if errors:
            if request.is_json:
                return jsonify({'errors': errors}), 400
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # 사용자 생성
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': '회원가입이 완료되었습니다.', 'redirect': url_for('auth.login')})
            flash('회원가입이 완료되었습니다.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': '회원가입 중 오류가 발생했습니다.'}), 500
            flash('회원가입 중 오류가 발생했습니다.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """로그아웃"""
    logout_user()
    return redirect(url_for('main.index'))



@auth_bp.route('/profile')
@login_required
def profile():
    """프로필 페이지 - 프로필 관리로 이동"""
    return redirect(url_for('profile.manage'))

