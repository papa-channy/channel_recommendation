### **Part 4 of 5: 프레젠테이션 계층 및 애플리케이션 조립**

이 파트에서는 사용자와 시스템이 만나는 지점인 **프레젠테이션 계층**과, 지금까지 설계한 모든 조각들을 하나로 꿰어 완전한 애플리케이션을 만드는 **의존성 조립(Composition Root)** 과정을 상세히 설계합니다. 이는 `Code_Guide.md`에서 강조하는 '살아있는 시스템'의 구체적인 모습을 보여주는 최종 단계입니다.

---

### **4.1. 프레젠테이션 계층(Presentation Layer) 상세 설계 (`src/presentation/app.py`)**

`app.py` 파일은 단순히 UI를 그리는 스크립트를 넘어, 클린 아키텍처에서 매우 중요한 두 가지 책임을 가집니다.

- **역할 1: 사용자 인터페이스(UI) 제공**
    
    - **기술 스택**: `Streamlit`
    - **구현**: 사용자가 페르소나를 선택하고, 추천받고 싶은 날짜와 시간을 입력하며, 최종 추천 결과를 시각적으로 확인할 수 있는 모든 UI 컴포넌트를 `Streamlit`을 사용하여 구축합니다.
- **역할 2: 컴포지션 루트(Composition Root)**
    
    - **정의**: 애플리케이션의 모든 구체적인 구현체(Adapters)들을 생성하고, 이를 유스케이스(Use Case)에 주입하여, 시스템의 모든 의존성 그래프를 완성하는 유일한 장소입니다.
    - **중요성**: 이 역할을 한 곳에 집중시킴으로써, 시스템의 핵심 로직(도메인 계층)은 어떤 구체적인 기술에도 의존하지 않는 순수성을 유지할 수 있습니다.

### **4.2. 애플리케이션 초기화 및 의존성 조립 (The Composition Root in Practice)**

애플리케이션이 시작될 때, 다음과 같은 과정으로 모든 의존성을 조립하고 완전히 작동 가능한 `RecommendChannelsUseCase` 객체를 생성합니다. 이 과정은 비용이 많이 들 수 있으므로, `@st.cache_resource` 데코레이터를 사용하여 생성된 객체를 캐싱하고 페이지 리로드 시 재사용하여 성능을 최적화합니다.

- **상세 구현 계획 (`setup_application` 함수)**:
    
    Python
    
    ```
    # src/presentation/app.py
    
    import streamlit as st
    import yaml
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from sqlalchemy import create_engine
    
    # 모든 어댑터와 유스케이스 임포트
    from src.adapters.db_repository import DBRepository
    from src.adapters.keras_rating_predictor import KerasRatingPredictor
    from src.adapters.gemini_content_labeler import GeminiContentLabeler
    from src.adapters.selenium_schedule_crawler import SeleniumScheduleCrawler
    from src.domain.use_cases.recommend_channels_use_case import RecommendChannelsUseCase
    from src.infrastructure.db_cache_manager import DBCacheManager
    
    @st.cache_resource
    def setup_application():
        """
        애플리케이션의 모든 의존성을 조립하고 완전히 구성된 Use Case 객체를 반환한다.
        이 함수가 바로 'Composition Root'의 실제 구현체이다.
        """
        # 1. 설정 및 환경 변수 로드
        load_dotenv()  # .env 파일에서 환경 변수 로드
    
        with open('config/default_config.yml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    
        # 2. 핵심 인프라 객체 생성 (DB 연결, 임베딩 모델)
        # SQLAlchemy 엔진 생성. .env에서 읽어온 정보 사용.
        db_connection_str = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        engine = create_engine(db_connection_str)
    
        # 문장 임베딩 모델 로드
        embedding_model = SentenceTransformer(config['paths']['embedding_model_name'])
    
        # 3. 모든 어댑터(구체적인 구현체) 인스턴스 생성
        # 각 어댑터는 필요한 인프라 객체나 설정을 주입받는다.
        repository = DBRepository(engine=engine)
        cache_manager = DBCacheManager(repository=repository) # 캐시 매니저는 DB 리포지토리에 의존
        rating_predictor = KerasRatingPredictor(model_path=config['paths']['model_path'])
        labeler = GeminiContentLabeler(
            api_key=os.getenv('GEMINI_API_KEY'),
            cache_manager=cache_manager,  # 라벨러는 캐시 매니저에 의존
            prompt_template=config['prompts']['labeling_prompt']
        )
        crawler = SeleniumScheduleCrawler(target_url=config['urls']['schedule_url'])
    
        # 4. 최종 단계: Use Case에 모든 구현체들을 주입하여 완전한 객체 생성
        # Use Case는 구체적인 클래스(Keras, Gemini 등)를 전혀 모르고, 오직 인터페이스에만 의존한다.
        use_case = RecommendChannelsUseCase(
            repository=repository,
            rating_predictor=rating_predictor,
            content_labeler=labeler,
            schedule_crawler=crawler,
            embedding_model=embedding_model
        )
    
        return use_case, config
    
    # --- 애플리케이션의 메인 진입점 ---
    try:
        # setup_application 함수를 호출하여 완전히 조립된 use_case 객체를 얻는다.
        recommend_use_case, app_config = setup_application()
    
        # --- Streamlit UI 코드 시작 ---
        st.title("📺 AI 기반 TV 채널 추천 시스템")
        # ... (이하 UI 로직) ...
    
    except Exception as e:
        # 초기화 실패 시, 사용자에게 명확한 에러 메시지를 보여준다.
        st.error(f"애플리케이션 초기화 중 오류가 발생했습니다: {e}")
        st.error("`.env` 파일에 API 키와 DB 정보가 올바르게 설정되었는지 확인해주세요.")
    
    ```
    

### **4.3. UI 로직 및 사용자 상호작용**

- **사이드바 제어판**: `st.sidebar`를 사용하여 사용자가 추천받기 위한 옵션들을 선택할 수 있는 제어판을 구성합니다.
    
    - **페르소나 선택**: 설정 파일(`default_config.yml`)에 정의된 페르소나 목록을 드롭다운으로 제공합니다.
    - **날짜 및 시간 선택**: `st.date_input`과 `st.time_input`을 사용하여 추천받고 싶은 기준 시점을 선택합니다.
    - **실행 버튼**: `st.button("추천 받기")` 버튼을 배치합니다.
- **실행 및 에러 처리**:
    
    - 사용자가 '추천 받기' 버튼을 클릭하면, `st.spinner("AI가 당신의 취향을 분석하고 있습니다...")`를 표시하여 시스템이 작동 중임을 알립니다.
    - `try-except` 블록 내에서 `recommend_use_case.execute()` 메서드를 호출합니다.
    - **성공 시**: 반환된 `RecommendationResultDTO` 객체를 `st.session_state.results`에 저장하여, 페이지가 다시 그려져도 결과가 유지되도록 합니다.
    - **실패 시**: Use Case에서 발생할 수 있는 구체적인 예외(e.g., `CrawlingError`, `APIError`)를 잡아 `st.error()`를 통해 사용자에게 친화적인 에러 메시지(예: "편성표 정보를 가져오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")를 표시합니다.
- **결과 시각화**:
    
    - `st.session_state.results`에 결과 DTO가 존재하면, UI를 그리기 시작합니다.
    - 모든 데이터는 정형화된 DTO를 통해 전달되므로, UI 코드는 데이터의 존재 여부나 타입을 걱정할 필요 없이 **안정적으로 렌더링에만 집중**할 수 있습니다.
    - 페르소나 정보, 과거 시청 기록, AI가 분석한 선호 콘텐츠 클러스터, 그리고 최종 추천 TV 프로그램 목록을 각각의 섹션으로 나누어 미려한 카드 레이아웃과 데이터프레임으로 시각화합니다.

이러한 설계는 각 계층이 자신의 **단일 책임 원칙(SRP)**에만 집중하도록 만듭니다. `app.py`는 오직 '보여주는 것'과 '의존성을 조립하는 것', `recommend_channels_use_case.py`는 오직 '비즈니스 규칙을 실행하는 것', 각 어댑터는 '특정 기술을 사용하여 인터페이스를 구현하는 것'에만 책임이 있습니다. 이것이 바로 `Code_Guide.md`에서 강조하는 유지보수 가능하고 테스트 용이한 '살아있는 시스템'의 구체적인 모습입니다.