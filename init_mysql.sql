-- MySQL 초기화 스크립트
-- Keycloak 사용자 및 데이터베이스 생성

-- Keycloak 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Keycloak 사용자 생성 및 권한 부여
CREATE USER IF NOT EXISTS 'keycloak'@'%' IDENTIFIED BY 'keycloak123';
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';

-- 메인 애플리케이션 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 메인 애플리케이션 사용자 생성 및 권한 부여
CREATE USER IF NOT EXISTS 'portfolio'@'%' IDENTIFIED BY 'portfolio_password';
GRANT ALL PRIVILEGES ON portfolio.* TO 'portfolio'@'%';

-- 권한 새로고침
FLUSH PRIVILEGES;

-- 데이터베이스 목록 확인
SHOW DATABASES;

