# channel_recommendation
MOVIELense, Netflix 데이터셋 기반으로 추천 시스템 → 모델 학습을 통해 나온 각 추천 프로그램에 대한 정보 표시 영화 제목, 장르 → IPTV의 편성표 정보를 크롤링(api로 받아와도 됨)해서 당일 방영하는 TV프로그램 목록을 저장 → 프로그램별 장르와 모델학습을 통해 나온 장르 정보를 매칭해서 해당 장르나 비슷한 장르의 카테고리에 있는 프로그램이 방영중인 채널이나 프로그램을 나열

MovieLense나 API로 크롤링한 데이터를 Mysql이나 gcp big Query에 밀어넣고 데이터 처리 예정

Mysql 연동해서 Streamlit 버튼 눌러서 채널이나 프로그램명 추천까지만 구현

## Running with Docker

각 서비스는 `docker-compose.yml`로 구성되어 있습니다. 다음 명령어로 전체 스택을 실행할 수 있습니다.

```bash
docker-compose up --build
```

Airflow는 포트 `8080`, Streamlit 애플리케이션은 포트 `8501`, MySQL은 포트 `3306`으로 노출됩니다.
