# 1. Base Image
# 가볍고 안정적인 Python 3.11 slim 버전을 기반으로 합니다.
FROM python:3.11-slim

# 2. Environment Variables
# Docker 로그 출력을 원활하게 합니다.
ENV PYTHONUNBUFFERED 1
# Poetry가 프로젝트 내부에 가상 환경을 만들지 않도록 설정합니다.
ENV POETRY_VIRTUALENVS_CREATE=false

# 3. Set Working Directory
WORKDIR /app

# 4. Install Poetry
# 의존성 관리를 위해 Poetry를 설치합니다.
RUN pip install poetry

# 5. Install Dependencies
# pyproject.toml 파일을 먼저 복사하여 Docker의 레이어 캐싱을 활용합니다.
# 의존성이 변경되지 않으면 이 단계는 재실행되지 않아 빌드 속도가 향상됩니다.
COPY pyproject.toml poetry.lock ./

# Poetry를 사용해 Streamlit 앱에 필요한 의존성만 설치합니다.
# --no-root: 프로젝트 자체는 설치하지 않음 (소스 코드는 아래에서 복사)
# --without dev,airflow: 개발/Airflow용 의존성은 제외하여 이미지 크기를 최적화
RUN poetry install --no-root --without dev,airflow

# 6. Copy Application Code
# 의존성 설치 후, 실제 애플리케이션 소스 코드를 복사합니다.
COPY ./src ./src

# 7. Expose Port
# Streamlit 기본 포트인 8501을 외부에 노출합니다.
EXPOSE 8501

# 8. Set Default Command
# 컨테이너 실행 시 Streamlit 앱을 실행합니다.
# --server.address=0.0.0.0: 모든 네트워크 인터페이스에서 접속을 허용합니다 (Docker 필수).
CMD ["poetry", "run", "streamlit", "run", "src/presentation/app.py", "--server.port=8501", "--server.address=0.0.0.0"]