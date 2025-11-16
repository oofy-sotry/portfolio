#!/bin/bash

# 현재 시스템의 IP 주소 자동 감지
HOST_IP=$(hostname -I | awk '{print $1}')

# .env 파일 생성
cat > .env << EOF
# 자동 생성된 환경 설정
KEYCLOAK_URL=http://${HOST_IP}:8080
KEYCLOAK_REALM=portfolio
KEYCLOAK_CLIENT_ID=portfolio-web
KEYCLOAK_CLIENT_SECRET=n11PXNqr3sqESefIjNg06LxUyTeIdVWk

# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://root:password@db:3306/portfolio_db

# Flask 설정
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production
EOF

echo "✅ 환경 설정이 생성되었습니다!"
echo "📍 감지된 IP: ${HOST_IP}"
echo "🔗 Keycloak URL: http://${HOST_IP}:8080"
echo "🌐 Portfolio URL: http://${HOST_IP}:5000"

