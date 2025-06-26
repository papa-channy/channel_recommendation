### **Part 1 of 5: 프로젝트 철학, 아키텍처 및 환경 구축**

첫 번째 파트에서는 프로젝트의 기본 철학을 재확인하고, 변경된 기술 스택을 반영하여 시스템 아키텍처와 폴더 구조, 보안 환경 설계를 상세하게 다시 정의합니다.

---

## **AI 기반 개인 맞춤형 TV 채널 추천 시스템: 상세 작업 계획서 V3.1**

### **Part 1: 프로젝트 철학, 아키텍처 및 보안 환경 구축**

#### **1.1. 프로젝트 철학: 장인 정신과 살아있는 시스템**

본 프로젝트는 단순히 '작동하는 소프트웨어'를 넘어, **'잘 만들어진 소프트웨어(Well-Crafted Software)'**를 창조하는 것을 목표로 합니다. 이는 코드 작성 가이드에서 제시된 장인 정신의 철학을 따르는 것으로, 다음과 같은 핵심 가치를 내재화합니다.

- **내부 품질 우선**: 코드의 가독성, 테스트 용이성, 모듈성은 장기적인 개발 속도와 시스템의 건전성을 결정하는 가장 중요한 요소입니다.
- **지속적인 개선**: "보이스카우트 규칙"에 따라, 모든 코드는 발견했을 때보다 더 깨끗하게 만들어 놓고 떠나는 것을 원칙으로 하여 기술 부채를 적극적으로 관리합니다.
- **프로세스를 통한 품질 보증**: TDD, 코드 리뷰, CI/CD 자동화 등 체계화된 프로세스를 통해 품질을 개발 과정에 깊숙이 내재화합니다.

궁극적인 목표는 시간이 지나도 가치를 잃지 않고, 변화에 유연하게 대응하며, 스스로의 건강 상태를 유지하는 **'살아있는 유기체 같은 레포지토리'**를 만드는 것입니다.

#### **1.2. 시스템 아키텍처: 클린 아키텍처 (Clean Architecture)**

시스템의 유연성과 유지보수성을 극대화하기 위해, 로버트 C. 마틴의 **클린 아키텍처**를 채택합니다. 이는 비즈니스 로직을 프레임워크, 데이터베이스, UI 등 외부 구현 세부사항으로부터 완벽하게 분리하는 것을 목표로 합니다.

- **핵심 원칙: 의존성 규칙 (The Dependency Rule)**: 소스 코드의 모든 의존성은 오직 **안쪽(고수준 정책)**을 향해야 합니다.
- **계층 구조 (Layers) (수정됨)**:
    1. **Domain Layer (도메인 계층)**: 시스템의 가장 핵심. Use Cases(비즈니스 로직)와 Interfaces(포트)를 포함하며 외부의 어떤 변화에도 영향을 받지 않습니다.
    2. **Application Layer (애플리케이션 계층)**: Use Case와 외부 세계(프레임워크, DB)를 연결하는 어댑터(Adapters)가 위치합니다. (e.g., `GeminiContentLabeler`, `KerasRatingPredictor`)
    3. **Infrastructure & Frameworks Layer (인프라 및 프레임워크 계층)**: Streamlit, **TensorFlow/Keras**, Selenium, **MySQL** 등 실제 프레임워크, 드라이버, 외부 서비스들이 위치합니다.

#### **1.3. 폴더 구조 설계 (수정됨)**

Airflow를 제거하고 `scripts` 폴더를 도입하는 등, 최신 아키텍처를 반영한 폴더 구조입니다.

```
channel_recommendation/
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
├── README.md
│
├── config/
│   └── default_config.yml
│
├── data/
│   ├── movies.csv
│   ├── ratings.csv
│   └── ncf_model_light.keras
│
├── scripts/
│   ├── fetch_schedule.py
│   └── retrain_model.py
│
├── src/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── keras_rating_predictor.py  # TensorFlow 모델용 어댑터
│   │   ├── gemini_content_labeler.py
│   │   ├── selenium_schedule_crawler.py
│   │   └── ...
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── dtos.py
│   │   ├── interfaces/
│   │   └── use_cases/
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── db_cache_manager.py
│   │
│   └── presentation/
│       ├── __init__.py
│       └── app.py
│
└── tests/
    ├── adapters/
    └── domain/
```

#### **1.4. 보안 환경 구축 및 설정 관리**

- **보안 제1원칙: 민감 정보의 완벽한 분리**
    
    - 모든 API 키, DB 접속 정보(사용자, 비밀번호, 호스트 등)는 소스 코드에서 **완전히 제거**합니다.
    - 프로젝트 루트에 **`.env`** 파일을 생성하여 모든 민감 정보를 키-값 쌍으로 관리합니다.
    - **`.gitignore`** 파일에 `.env`를 **반드시 추가**하여 Git 저장소에 포함되지 않도록 합니다.
- **.env 파일 예시 (수정됨)**:
    
    ```
    # .env
    
    # Google Gemini API Key
    GEMINI_API_KEY="your_gemini_api_key_here"
    
    # MySQL Database Connection
    DB_HOST=db
    DB_USER=root
    DB_PASSWORD=your_db_password
    DB_NAME=recommendation_db
    DB_PORT=3306
    ```
    
- **안전한 설정 로딩 프로세스**:
    
    1. 애플리케이션 시작 시(e.g., `app.py` 최상단) `dotenv.load_dotenv()`를 호출하여 `.env` 파일의 변수들을 시스템 환경 변수로 로드합니다.
    2. DB 접속이나 API 키가 필요한 모듈에서는 `os.getenv("VARIABLE_NAME")`을 사용하여 환경 변수에서 직접 값을 가져옵니다.
    3. `config/default_config.yml` 파일에는 모델 파라미터, 파일 경로 등 **안전하게 공유 가능한 기본 설정**만을 담습니다.

이러한 구조는 소스 코드를 안전하게 공개할 수 있도록 보장하며, 각 개발자는 자신의 로컬 `.env` 파일만 관리하면 됩니다. 배포 환경에서는 CI/CD 파이프라인을 통해 환경 변수를 안전하게 주입합니다.