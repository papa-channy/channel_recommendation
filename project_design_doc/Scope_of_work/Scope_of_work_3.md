### **Part 3 of 5: 애플리케이션 및 도메인 계층 상세 설계**

이 파트에서는 시스템의 '두뇌'에 해당하는 도메인 계층과, 이를 외부 기술과 연결하는 애플리케이션 계층을 상세히 설계합니다. `Code_Guide.md`에서 강조하는 SOLID 원칙, 특히 **의존성 역전 원칙(DIP)**을 철저히 적용하여, 시스템의 핵심 로직을 외부 변화로부터 보호하고 유연성을 극대화합니다.

---

### **3.1. 추상 인터페이스 (Ports) 설계 (`src/domain/interfaces/`)**

클린 아키텍처의 핵심은 **추상화에 의존하는 것**입니다. 유스케이스(핵심 로직)는 구체적인 기술(Adapter)을 직접 알지 못하며, 오직 이 추상 인터페이스(Port)에만 의존합니다. 이를 통해, 예를 들어 평점 예측 모델을 다른 모델로 교체하더라도 유스케이스 코드는 전혀 수정할 필요가 없습니다.

각 인터페이스는 `abc` 모듈을 사용하여 추상 베이스 클래스(ABC)로 정의됩니다.

- **`repository_interface.py`**: 데이터베이스와의 모든 상호작용을 추상화합니다.
    
    Python
    
    ```
    class RepositoryInterface(ABC):
        @abstractmethod
        def get_user_ratings(self, user_id: int) -> pd.DataFrame:
            """특정 사용자의 모든 평점 정보를 가져온다."""
            pass
        # ... 기타 DB I/O 메서드 (e.g., save_labels, get_movies)
    ```
    
- **`rating_predictor_interface.py`**: 특정 사용자와 영화 목록에 대한 예상 평점을 예측하는 책임을 정의합니다.
    
    Python
    
    ```
    class RatingPredictorInterface(ABC):
        @abstractmethod
        def predict_ratings(self, user_id: int, movie_ids: List[int]) -> Dict[int, float]:
            """주어진 사용자와 영화 목록에 대한 예상 평점을 예측한다."""
            pass
    ```
    
- **`content_labeler_interface.py`**: 콘텐츠(영화, TV 프로그램)의 제목과 줄거리를 기반으로 핵심적인 의미 태그(라벨)를 생성하는 책임을 정의합니다.
    
    Python
    
    ```
    class ContentLabelerInterface(ABC):
        @abstractmethod
        def generate_labels(self, title: str, overview: str) -> List[str]:
            """콘텐츠의 제목과 줄거리를 기반으로 시맨틱 라벨을 생성한다."""
            pass
    ```
    
- **`schedule_crawler_interface.py`**: 특정 날짜의 IPTV 편성표를 외부에서 가져오는 책임을 정의합니다.
    
    Python
    
    ```
    class ScheduleCrawlerInterface(ABC):
        @abstractmethod
        def fetch_schedule(self, target_date: str) -> List[Dict[str, Any]]:
            """특정 날짜의 IPTV 편성표를 가져온다."""
            pass
    ```
    

### **3.2. 구체적인 구현체 (Adapters) 설계 (`src/adapters/`)**

어댑터는 위에서 정의한 추상 인터페이스를 실제로 구현하는 구체적인 클래스들입니다. 각 어댑터는 특정 기술(TensorFlow, Selenium, Gemini API 등)에 직접 의존합니다.

- **`db_repository.py`**: `RepositoryInterface`를 구현합니다.
    
    - **기술 스택**: `SQLAlchemy`와 `pymysql` 드라이버를 사용하여 MySQL 데이터베이스와 통신합니다.
    - **주요 로직**: `.env` 파일로부터 DB 접속 정보를 읽어와 SQLAlchemy 엔진을 생성하고, 정의된 ORM 모델 또는 SQL 쿼리를 통해 데이터를 조회/저장합니다.
- **`keras_rating_predictor.py` (수정됨)**: `RatingPredictorInterface`를 구현합니다.
    
    - **기술 스택**: `TensorFlow/Keras`.
    - **주요 로직**: `tensorflow.keras.models.load_model()`을 사용하여 `data/ncf_model_light.keras` 모델 파일을 로드합니다. `predict_ratings` 메서드는 입력된 사용자 ID와 영화 ID를 모델이 학습한 내부 인덱스로 변환한 후, `model.predict()`를 호출하여 예상 평점을 계산하고 반환합니다.
- **`gemini_content_labeler.py`**: `ContentLabelerInterface`를 구현합니다.
    
    - **기술 스택**: `google-generativeai` 라이브러리.
    - **주요 로직**:
        1. `.env` 파일에서 `GEMINI_API_KEY`를 안전하게 로드합니다.
        2. `generate_labels`가 호출되면, 먼저 `labels_cache` 테이블에 해당 콘텐츠의 해시값이 있는지 `DBRepository`를 통해 조회합니다.
        3. 캐시가 존재하면 API 호출 없이 DB의 값을 즉시 반환합니다.
        4. 캐시가 없으면, Gemini API를 호출하여 라벨을 생성하고, 그 결과를 `labels_cache` 테이블에 저장한 후 반환합니다.
- **`selenium_schedule_crawler.py`**: `ScheduleCrawlerInterface`를 구현합니다.
    
    - **기술 스택**: `Selenium`과 `BeautifulSoup4`.
    - **주요 로직**: `webdriver-manager`를 사용하여 크롬 드라이버를 자동으로 설정하고, 지정된 IPTV 편성표 웹사이트에 접속하여 특정 날짜의 데이터를 스크레이핑합니다. 크롤링된 데이터는 DTO 형식에 맞게 파싱되어 반환됩니다.

### **3.3. 데이터 전송 객체 (DTOs) 설계 (`src/domain/dtos.py`)**

`Pydantic`을 사용하여 각 계층 간에 데이터를 안정적이고 명확하게 전달하는 DTO를 정의합니다. 이는 데이터의 구조와 타입을 강제하여 런타임 에러를 방지하고, 코드의 가독성을 높입니다.

- **`RecommendedProgramDTO`**: 최종 추천된 TV 프로그램을 나타냅니다.
    
    Python
    
    ```
    class RecommendedProgramDTO(BaseModel):
        channel: str
        title: str
        start_time: datetime
        end_time: datetime
        similarity_score: float = Field(..., ge=0, le=1) # 0과 1 사이의 값
        reason: str # 추천 이유 (XAI)
    ```
    
- **`RecommendationResultDTO`**: 유스케이스의 최종 실행 결과를 담는 메인 DTO입니다. 프레젠테이션 계층은 이 객체 하나만 받아 UI를 구성합니다.
    
    Python
    
    ```
    class RecommendationResultDTO(BaseModel):
        persona_name: str
        persona_description: str
        watch_history: List[WatchedMovieDTO]
        preference_cluster: List[LabelledContentDTO]
        recommended_programs: List[RecommendedProgramDTO]
    ```
    

### **3.4. 유스케이스(Use Case) 상세 설계 (`src/domain/use_cases/`)**

유스케이스는 시스템의 핵심 비즈니스 로직을 수행하는 **오케스트레이터**입니다. 외부 세계에 대한 구체적인 구현을 전혀 알지 못하며, 오직 추상 인터페이스(Ports)에만 의존합니다.

- **클래스명**: `RecommendChannelsUseCase`
    
- **의존성 주입(Dependency Injection)**: 생성자(`__init__`)를 통해 `RatingPredictorInterface`, `ContentLabelerInterface` 등 필요한 모든 인터페이스의 구현체를 외부(Composition Root)로부터 주입받습니다. 이는 DIP(의존성 역전 원칙)의 핵심 실천입니다.
    
    Python
    
    ```
    # src/domain/use_cases/recommend_channels_use_case.py
    class RecommendChannelsUseCase:
        def __init__(
            self,
            repository: RepositoryInterface,
            rating_predictor: RatingPredictorInterface,
            content_labeler: ContentLabelerInterface,
            schedule_crawler: ScheduleCrawlerInterface,
            embedding_model  # 실제 임베딩 모델 객체
        ):
            self.repository = repository
            self.rating_predictor = rating_predictor
            self.labeler = content_labeler
            self.crawler = schedule_crawler
            self.embedding_model = embedding_model
    ```
    
- **`execute(self, user_id: int, target_date: str) -> RecommendationResultDTO` 메서드 실행 흐름**:
    
    1. **사용자 정보 로드**: `self.repository.get_user_ratings(user_id)`를 호출하여 사용자의 과거 시청 기록(평점)을 가져옵니다.
    2. **잠재 선호 영화 예측**: 사용자가 아직 보지 않은 영화 목록에 대해 `self.rating_predictor.predict_ratings(...)`를 호출하여 예상 평점을 계산하고, 상위 N개의 영화를 '잠재 선호 영화'로 선정합니다.
    3. **편성표 수집**: `self.crawler.fetch_schedule(target_date)`를 호출하여 해당 날짜의 TV 편성표 데이터를 가져옵니다.
    4. **콘텐츠 라벨링**:
        - '잠재 선호 영화' 목록과 수집된 'TV 프로그램' 목록 각각에 대해 `self.labeler.generate_labels(...)`를 호출하여 의미론적 라벨을 생성합니다.
        - 이 과정에서 `gemini_content_labeler` 내부의 캐싱 로직이 동작하여 API 호출을 최소화합니다.
    5. **임베딩 및 유사도 계산**:
        - 라벨이 생성된 '잠재 선호 영화 클러스터'와 'TV 프로그램' 각각의 라벨들을 `self.embedding_model.encode()`를 사용하여 벡터로 변환합니다.
        - 코사인 유사도를 계산하여 각 TV 프로그램이 사용자의 잠재적 취향과 얼마나 유사한지 점수를 매깁니다.
    6. **최종 결과 조합**: 모든 처리된 데이터를 `RecommendationResultDTO` 객체에 담아 반환합니다. 이 객체는 데이터의 유효성을 자동으로 검증합니다.