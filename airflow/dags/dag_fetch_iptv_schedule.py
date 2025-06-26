# -*- coding: utf-8 -*-

import pendulum
from datetime import timedelta
import os
import sys

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

# -------------------------------------------------------------------------------------
# Airflow가 프로젝트의 소스 코드를 찾을 수 있도록 경로를 설정합니다.
# 이 DAG 파일이 있는 위치를 기준으로 프로젝트 루트 디렉토리를 찾아 sys.path에 추가합니다.
# 실제 운영 환경에서는 Airflow Worker의 PYTHONPATH 환경 변수에 프로젝트 경로를
# 직접 추가하는 것이 더 안정적인 방법입니다.
# -------------------------------------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# -------------------------------------------------------------------------------------
# 프로젝트 소스 코드에서 필요한 모듈과 클래스를 임포트합니다.
# 경로 설정이 올바르게 되어야 이 부분이 에러 없이 실행됩니다.
# -------------------------------------------------------------------------------------
from src.adapters.selenium_schedule_crawler import SeleniumScheduleCrawler
from src.utils.helpers import load_config

# --- DAG 기본 인수 정의 ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1, # 실패 시 1회 재시도
    "retry_delay": timedelta(minutes=5), # 재시도 간 5분 대기
}

def fetch_and_save_schedule(**kwargs):
    """
    IPTV 편성표를 크롤링하고 저장하는 Python 함수입니다.
    Airflow의 PythonOperator에 의해 실행됩니다.
    """
    # config 파일 로드
    # 프로젝트 루트를 기준으로 config 파일 경로를 설정합니다.
    config_path = os.path.join(project_root, 'config', 'default_config.yml')
    config = load_config(config_path)
    
    # Airflow의 실행 날짜(logical_date)를 가져옵니다.
    # 이 날짜를 기준으로 편성표를 가져오도록 합니다.
    execution_date = kwargs['ds'] # 'YYYY-MM-DD' 형식의 문자열
    target_date_str = execution_date.replace('-', '') # 'YYYYMMDD' 형식으로 변환

    print(f"편성표 수집 시작: {target_date_str}")
    
    # 크롤러 인스턴스 생성 및 실행
    crawler = SeleniumScheduleCrawler(config)
    schedule_data = crawler.fetch_schedule(target_date_str)
    
    if schedule_data:
        print(f"총 {len(schedule_data)}개의 프로그램 정보를 수집했습니다.")
        # 파일 캐싱은 fetch_schedule 내부 로직에서 처리되므로 여기서는 호출만 합니다.
    else:
        print("편성표 정보 수집에 실패했거나 데이터가 없습니다.")
        # 실패 시 Airflow가 재시도하도록 예외를 발생시킬 수 있습니다.
        # raise ValueError("편성표 데이터 수집 실패")

# --- DAG 정의 ---
with DAG(
    dag_id="fetch_daily_iptv_schedule",
    default_args=default_args,
    description="매일 자정, IPTV 편성표를 크롤링하여 로컬 파일 시스템에 저장하는 DAG",
    schedule=timedelta(days=1), # 매일 1회 실행
    start_date=pendulum.datetime(2025, 6, 26, tz="Asia/Seoul"), # DAG 시작 날짜
    catchup=False, # 시작 날짜와 현재 날짜 사이의 누락된 DAG 실행 안 함
    tags=["data_ingestion", "crawler"],
) as dag:

    # --- Task 정의 ---
    fetch_schedule_task = PythonOperator(
        task_id="fetch_and_save_tv_schedule",
        python_callable=fetch_and_save_schedule,
    )

