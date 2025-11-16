#!/usr/bin/env python3
"""
Keycloak 초기 설정 스크립트
"""

import requests
import json
import time
import os
import socket

def get_host_ip():
    """현재 호스트의 IP 주소를 동적으로 감지"""
    try:
        # 외부 서버에 연결하여 로컬 IP 확인
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # 실패시 localhost 사용
        return "localhost"

def wait_for_keycloak():
    """Keycloak 서비스가 준비될 때까지 대기"""
    host_ip = get_host_ip()
    keycloak_url = f"http://{host_ip}:8080"
    max_attempts = 30
    
    for attempt in range(max_attempts):
        try:
            # /realms/master 엔드포인트로 직접 확인 (실제로 동작하는 엔드포인트)
            response = requests.get(f"{keycloak_url}/realms/master", timeout=5)
            if response.status_code == 200:
                print("✅ Keycloak 서비스가 준비되었습니다.")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Keycloak 서비스 대기 중... ({attempt + 1}/{max_attempts})")
        time.sleep(10)
    
    print("❌ Keycloak 서비스가 준비되지 않았습니다.")
    return False

def setup_keycloak():
    """Keycloak 초기 설정"""
    if not wait_for_keycloak():
        return False
    
    host_ip = get_host_ip()
    keycloak_url = f"http://{host_ip}:8080"
    portfolio_url = f"http://{host_ip}:5000"
    admin_username = "admin"
    admin_password = "admin123"
    
    print(f"📍 감지된 IP: {host_ip}")
    print(f"🔗 Keycloak URL: {keycloak_url}")
    print(f"🌐 Portfolio URL: {portfolio_url}")
    
    # 관리자 토큰 획득
    token_url = f"{keycloak_url}/realms/master/protocol/openid-connect/token"
    token_data = {
        'grant_type': 'password',
        'client_id': 'admin-cli',
        'username': admin_username,
        'password': admin_password
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        token_info = response.json()
        
        if 'access_token' not in token_info:
            print("❌ 관리자 토큰 획득 실패")
            return False
        
        access_token = token_info['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Realm 생성
        realm_data = {
            "realm": "portfolio",
            "enabled": True,
            "displayName": "Portfolio Realm",
            "loginWithEmailAllowed": True,
            "duplicateEmailsAllowed": False,
            "resetPasswordAllowed": True,
            "editUsernameAllowed": True,
            "bruteForceProtected": True
        }
        
        realm_url = f"{keycloak_url}/admin/realms"
        response = requests.post(realm_url, json=realm_data, headers=headers)
        
        if response.status_code in [201, 409]:  # 409는 이미 존재하는 경우
            print("✅ Portfolio Realm 생성 완료")
        else:
            print(f"⚠️ Realm 생성 응답: {response.status_code}")
        
        # Client 생성
        client_data = {
            "clientId": "portfolio-web",
            "enabled": True,
            "publicClient": False,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": True,
            "redirectUris": [f"{portfolio_url}/auth/keycloak-callback"],
            "webOrigins": [portfolio_url],
            "rootUrl": portfolio_url,
            "baseUrl": portfolio_url,
            "protocol": "openid-connect"
        }
        
        client_url = f"{keycloak_url}/admin/realms/portfolio/clients"
        response = requests.post(client_url, json=client_data, headers=headers)
        
        if response.status_code in [201, 409]:
            print("✅ Portfolio Client 생성 완료")
            
            # Client Secret 가져오기
            if response.status_code == 201:
                client_id = response.headers.get('Location').split('/')[-1]
                secret_url = f"{keycloak_url}/admin/realms/portfolio/clients/{client_id}/client-secret"
                secret_response = requests.get(secret_url, headers=headers)
                
                if secret_response.status_code == 200:
                    secret_info = secret_response.json()
                    client_secret = secret_info.get('value')
                    print(f"🔑 Client Secret: {client_secret}")
                    
                    # 환경 변수 파일 업데이트
                    env_file = ".env"
                    if os.path.exists(env_file):
                        # 기존 KEYCLOAK_CLIENT_SECRET 라인 제거
                        with open(env_file, 'r') as f:
                            lines = f.readlines()
                        
                        # KEYCLOAK_CLIENT_SECRET 라인 제거
                        filtered_lines = [line for line in lines if not line.startswith('KEYCLOAK_CLIENT_SECRET=')]
                        
                        # 새로운 Client Secret 추가
                        with open(env_file, 'w') as f:
                            f.writelines(filtered_lines)
                            f.write(f"KEYCLOAK_CLIENT_SECRET={client_secret}\n")
                        
                        print("✅ .env 파일에 Client Secret 업데이트됨")
        else:
            print(f"⚠️ Client 생성 응답: {response.status_code}")
        
        # 테스트 사용자 생성
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "firstName": "Admin",
                "lastName": "User",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": "admin123",
                    "temporary": False
                }]
            },
            {
                "username": "testuser",
                "email": "test@example.com",
                "firstName": "Test",
                "lastName": "User",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": "test123",
                    "temporary": False
                }]
            }
        ]
        
        user_url = f"{keycloak_url}/admin/realms/portfolio/users"
        for user_data in users_data:
            response = requests.post(user_url, json=user_data, headers=headers)
            
            if response.status_code in [201, 409]:
                print(f"✅ 사용자 '{user_data['username']}' 생성 완료")
            else:
                print(f"⚠️ 사용자 '{user_data['username']}' 생성 응답: {response.status_code}")
        
        print("\n🎉 Keycloak 설정 완료!")
        print(f"📝 관리자 콘솔: {keycloak_url}/admin")
        print(f"🌐 Portfolio URL: {portfolio_url}")
        print("👤 관리자 계정: admin / admin123")
        print("👤 테스트 계정: testuser / test123")
        
        return True
        
    except Exception as e:
        print(f"❌ Keycloak 설정 중 오류: {e}")
        return False

if __name__ == '__main__':
    setup_keycloak()

