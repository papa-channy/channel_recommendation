# 1. Base Image
# 앱과 동일한 Python 버전을 사용하여 환경을 통일합니다.
FROM python:3.11-slim

# 2. Environment Variables
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE=false
# Airflow 홈 디렉토리 지정
ENV AIRFLOW_HOME=/opt/airflow

# 3. Argument for User ID
# docker-compose.yml에서 전달된 사용자 ID를 받아 로컬 파일 권한 문제를 해결합니다.
ARG AIRFLOW_UID=50001

# 4. System Dependencies & User Creation
# Airflow 실행에 필요한 패키지를 설치하고, non-root 사용자를 생성합니다.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libmysqlclient-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash -u ${AIRFLOW_UID} airflow

# 5. Set Working Directory
WORKDIR ${AIRFLOW_HOME}

# 6. Install Poetry
RUN pip install poetry

# 7. Install Python Dependencies
# 레이어 캐싱을 위해 의존성 정의 파일만 먼저 복사
COPY pyproject.toml poetry.lock ./

# Airflow에 필요한 의존성만 설치합니다.
# 프로젝트 소스 코드를 DAG에서 직접 import할 수 있도록 프로젝트 자체도 설치합니다.
RUN poetry install --without dev,app

# 8. Copy Project Files
# Airflow DAG, 플러그인 등 관련 파일 복사
COPY ./airflow/dags ./dags
COPY ./airflow/plugins ./plugins
# DAG가 import할 수 있도록 애플리케이션 소스 코드 복사
COPY ./src ./src

# 9. Set Ownership & User
# 생성한 non-root 사용자에게 홈 디렉토리 소유권을 부여하고, 해당 사용자로 전환합니다.
RUN chown -R airflow: ${AIRFLOW_HOME}
USER airflow

# 10. Expose Ports
# Airflow 웹서버(8080), Flower(5555) 포트 노출
EXPOSE 8080 5555

# 11. Entrypoint/CMD
# Airflow의 공식 Docker Entrypoint를 사용하거나, docker-compose.yml에서
# 직접 command (webserver, scheduler 등)를 지정하는 것이 일반적이므로
# 여기서는 생략합니다.