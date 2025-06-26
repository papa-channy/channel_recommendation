-- 이 스크립트는 MySQL 컨테이너가 처음 시작될 때 자동으로 실행됩니다.
-- 데이터베이스, 사용자, 권한을 미리 설정합니다.
-- docker-compose.yml과 .env.example의 DB 관련 설정과 일치해야 합니다.

-- UTF-8을 지원하는 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS tv_recommendation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 애플리케이션이 사용할 사용자 생성
CREATE USER 'app_user'@'%' IDENTIFIED BY 'app_password';

-- 생성한 데이터베이스에 대한 모든 권한을 사용자에게 부여
GRANT ALL PRIVILEGES ON tv_recommendation_db.* TO 'app_user'@'%';

-- 변경사항 적용
FLUSH PRIVILEGES;

-- (선택 사항) Alembic을 사용하지 않고 초기에 테이블을 생성하고 싶을 경우
-- 여기에 CREATE TABLE 구문을 추가할 수 있습니다.
-- 예시:
-- USE tv_recommendation_db;
--
-- CREATE TABLE IF NOT EXISTS users (
--     user_id INTEGER PRIMARY KEY,
--     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );