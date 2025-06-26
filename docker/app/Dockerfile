# 1. Base Image
# 안정성과 이미지 크기를 고려하여 Python 3.11 slim 버전을 기반으로 합니다.
FROM python:3.13

# 2. Environment Variables
# Docker 컨테이너의 로그 출력이 버퍼링 없이 즉시 표시되도록 설정합니다.
ENV PYTHONUNBUFFERED 1
# Poetry가 프로젝트 외부에 별도의 가상 환경을 생성하지 않고, 시스템에 직접 의존성을 설치하도록 설정합니다.
# Docker 이미지 내에서는 격리된 환경이 이미 보장되므로 false로 설정하는 것이 일반적입니다.
ENV POETRY_VIRTUALENVS_CREATE=false

# 3. Set Working Directory
# 컨테이너 내에서 명령어가 실행될 기본 작업 디렉터리를 '/app'으로 설정합니다.
WORKDIR /app

# 4. Install Poetry
# 의존성 관리를 위해 pip를 사용해 Poetry를 설치합니다.
RUN pip install poetry

# 5. Install Dependencies
# 먼저 의존성 정의 파일만 복사하여 Docker의 레이어 캐싱 효과를 극대화합니다.
# 이 파일들이 변경되지 않으면, 'poetry install' 단계는 캐시를 사용하여 빌드 시간을 단축합니다.
COPY pyproject.toml poetry.lock ./

# Poetry를 사용하여 Streamlit 앱 실행에 필요한 'app' 그룹의 의존성만 설치합니다.
# --no-root: 프로젝트 자체는 설치하지 않습니다. (소스 코드는 아래 6번, 7번 단계에서 복사)
# --only app: pyproject.toml에 정의된 [tool.poetry.group.app.dependencies] 의존성만 설치하여 이미지 크기를 최적화합니다.
RUN poetry install --no-root --only app

# 6. Copy Configuration and Data Files
# 애플리케이션 실행에 필요한 설정 파일과 샘플 데이터를 이미지 안으로 복사합니다.
# 이 단계가 누락되면 'FileNotFoundError'가 발생할 수 있습니다.
COPY ./config ./config
COPY ./data ./data

# 7. Copy Application Code
# 실제 애플리케이션 소스 코드를 이미지 안으로 복사합니다.
COPY ./src ./src

# 8. Expose Port
# Streamlit의 기본 포트인 8501을 컨테이너 외부로 노출시켜 접근할 수 있도록 합니다.
EXPOSE 8501

# 9. Set Default Command
# 컨테이너가 시작될 때 실행될 기본 명령어를 설정합니다.
# 'poetry run'을 통해 Poetry가 관리하는 환경에서 Streamlit을 실행합니다.
# --server.address=0.0.0.0: Docker 환경에서 외부 접속을 허용하기 위해 필수적인 옵션입니다.
CMD ["poetry", "run", "streamlit", "run", "src/presentation/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
