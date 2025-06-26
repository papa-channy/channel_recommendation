# -*- coding: utf-8 -*-

import pendulum
from datetime import timedelta
import os
import sys

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

# --- 프로젝트 경로 설정 (위와 동일) ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# --- 프로젝트 모듈 임포트 ---
from src.adapters.file_data_loader import FileDataLoader
from src.adapters.torch_rating_predictor import TorchRatingPredictor # 학습 기능이 포함된 클래스
from src.utils.helpers import load_config
# 실제 학습에는 PyTorch의 DataLoader 등 추가 임포트가 필요합니다.
# 이 예시에서는 개념적인 흐름을 보여줍니다.

# --- DAG 기본 인수 정의 ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0, # 모델 학습은 자원 소모가 크므로 자동 재시도는 비활성화
}

def preprocess_movielens_data(**kwargs):
    """
    MovieLens 원본 데이터를 전처리하는 함수.
    """
    print("MovieLens 데이터 전처리 시작...")
    config_path = os.path.join(project_root, 'config', 'default_config.yml')
    config = load_config(config_path)
    
    data_loader = FileDataLoader(config)
    # load_and_preprocess_movielens는 전처리 후 파일로 저장하는 메서드로 가정
    success = data_loader.load_and_preprocess_movielens() 
    
    if success:
        print("데이터 전처리 완료.")
    else:
        raise ValueError("데이터 전처리 실패")

def train_rating_model(**kwargs):
    """
    전처리된 데이터를 사용하여 평점 예측 모델을 학습하는 함수.
    """
    print("추천 모델 학습 시작...")
    config_path = os.path.join(project_root, 'config', 'default_config.yml')
    config = load_config(config_path)
    
    # RatingPredictor가 학습 기능을 포함하고 있다고 가정
    # 실제 구현에서는 학습 데이터 로딩, DataLoader 생성 등의 과정이 필요
    predictor = TorchRatingPredictor(config)
    
    # train() 메서드가 내부적으로 데이터를 로드하고 학습을 수행한다고 가정
    history = predictor.train() 
    
    if history:
        print("모델 학습 완료.")
        print(f"최종 검증 손실: {history['best_val_loss']:.4f}")
    else:
        raise ValueError("모델 학습 실패")


# --- DAG 정의 ---
with DAG(
    dag_id="retrain_weekly_recommendation_model",
    default_args=default_args,
    description="매주 일요일, 최신 데이터로 추천 모델을 재학습하는 DAG",
    schedule="0 0 * * 0", # 매주 일요일 00:00에 실행
    start_date=pendulum.datetime(2025, 6, 26, tz="Asia/Seoul"),
    catchup=False,
    tags=["model_training", "ml"],
) as dag:

    # --- Task 정의 ---
    preprocess_task = PythonOperator(
        task_id="preprocess_source_data",
        python_callable=preprocess_movielens_data,
    )

    train_task = PythonOperator(
        task_id="train_ncf_model",
        python_callable=train_rating_model,
    )

    # --- Task 의존성 설정 ---
    # 전처리 태스크가 성공해야 학습 태스크가 실행됩니다.
    preprocess_task >> train_task

