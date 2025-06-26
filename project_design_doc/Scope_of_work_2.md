### **Part 2: 데이터 계층 상세 설계: 무결성과 진화의 공학**

데이터 계층은 시스템의 척추이다. ERD 설계 가이드맵의 원칙에 따라, 본 시스템의 데이터 계층은 단순히 데이터를 저장하는 것을 넘어, 데이터의 무결성을 시스템 수준에서 보장하고, 예측 가능한 성능을 제공하며, 비즈니스 요구사항의 변화에 유연하게 대응할 수 있도록 설계한다.

#### **2.1. 데이터베이스 스키마 설계 (ERD & Physical Design)**

* **데이터베이스 선택**: SQLite  
  * **근거**: 프로젝트 초기 단계에서는 별도의 DB 서버 구축 없이 파일 기반으로 쉽게 관리할 수 있으며, Python에 내장되어 있어 개발 환경 설정이 용이하다. 프로토타이핑과 로컬 실행에 최적화되어 있으며, 추후 MySQL이나 PostgreSQL로 마이그레이션할 수 있는 기반을 다진다.  
* ERD (Entity-Relationship Diagram)  
  \[ERD 이미지\]  
  * 주요 엔티티: Users, Movies, Genres, Ratings, TV\_Programs, Labels  
  * 주요 관계:  
    * Users와 Ratings (1:N)  
    * Movies와 Ratings (1:N)  
    * Movies와 Movie\_Genres (1:N)  
    * Genres와 Movie\_Genres (1:N) \-\> Movies와 Genres는 M:N 관계  
* **물리적 스키마 (SQL CREATE 구문)**  
  * 모든 테이블과 컬럼명은 일관성 있는 snake\_case 표기법을 따른다.  
  * '일반적인 주키(id)' 안티패턴을 피하기 위해, 주키는 테이블명\_id 형식으로 명명한다.  
  * 데이터 무결성을 위해 NOT NULL, CHECK, DEFAULT, FOREIGN KEY 제약 조건을 적극적으로 활용한다.

\-- Users: 사용자 정보를 저장. 현재는 페르소나의 ID만 관리.  
CREATE TABLE IF NOT EXISTS users (  
    user\_id INTEGER PRIMARY KEY, \-- MovieLens의 userId  
    created\_at TIMESTAMP NOT NULL DEFAULT CURRENT\_TIMESTAMP  
);

\-- Genres: 영화 및 TV 프로그램의 모든 장르를 중복 없이 관리.  
CREATE TABLE IF NOT EXISTS genres (  
    genre\_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    genre\_name TEXT NOT NULL UNIQUE  
);

\-- Movies: 영화의 메타데이터를 저장. TMDb 등 외부 데이터로 확장 가능.  
CREATE TABLE IF NOT EXISTS movies (  
    movie\_id INTEGER PRIMARY KEY, \-- MovieLens의 movieId  
    title TEXT NOT NULL,  
    release\_year INTEGER,  
    \-- TMDb 연동을 위한 확장 필드 (NULL 허용)  
    overview TEXT,  
    poster\_path TEXT,  
    tmdb\_id INTEGER UNIQUE  
);

\-- Movie\_Genres: 영화와 장르의 다대다 관계를 매핑하는 연결 테이블.  
CREATE TABLE IF NOT EXISTS movie\_genres (  
    movie\_id INTEGER NOT NULL,  
    genre\_id INTEGER NOT NULL,  
    PRIMARY KEY (movie\_id, genre\_id),  
    FOREIGN KEY (movie\_id) REFERENCES movies (movie\_id) ON DELETE CASCADE,  
    FOREIGN KEY (genre\_id) REFERENCES genres (genre\_id) ON DELETE CASCADE  
);

\-- Ratings: 사용자의 영화 평점 정보를 저장.  
CREATE TABLE IF NOT EXISTS ratings (  
    rating\_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    user\_id INTEGER NOT NULL,  
    movie\_id INTEGER NOT NULL,  
    rating REAL NOT NULL CHECK(rating \>= 0.5 AND rating \<= 5.0),  
    rated\_at TIMESTAMP NOT NULL,  
    FOREIGN KEY (user\_id) REFERENCES users (user\_id) ON DELETE CASCADE,  
    FOREIGN KEY (movie\_id) REFERENCES movies (movie\_id) ON DELETE CASCADE,  
    UNIQUE (user\_id, movie\_id) \-- 사용자는 한 영화에 대해 한 번만 평점을 매길 수 있음  
);

\-- TV\_Programs: 크롤링된 IPTV 편성표 정보를 저장.  
CREATE TABLE IF NOT EXISTS tv\_programs (  
    program\_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    channel\_name TEXT NOT NULL,  
    title TEXT NOT NULL,  
    episode\_title TEXT,  
    start\_time TIMESTAMP NOT NULL,  
    end\_time TIMESTAMP NOT NULL,  
    synopsis TEXT,  
    crawled\_at TIMESTAMP NOT NULL DEFAULT CURRENT\_TIMESTAMP  
);

\-- Labels: LLM으로 생성된 콘텐츠 라벨을 저장하는 캐시 테이블.  
CREATE TABLE IF NOT EXISTS labels\_cache (  
    content\_hash TEXT PRIMARY KEY, \-- title과 overview의 SHA256 해시  
    title TEXT NOT NULL,  
    labels\_json TEXT NOT NULL, \-- 라벨 리스트를 JSON 문자열로 저장  
    created\_at TIMESTAMP NOT NULL DEFAULT CURRENT\_TIMESTAMP  
);

* **스키마 설계 평가**:  
  * **정규화**: 제안된 스키마는 \*\*BCNF(Boyce-Codd Normal Form)\*\*를 만족한다. genres를 별도 테이블로 분리하여 다중 값 속성을 제거(1NF)하고, 복합키가 없어 부분 함수 종속이 원천적으로 존재하지 않으며(2NF), 키가 아닌 속성 간의 이행적 종속이 없다(3NF). 모든 결정자가 후보 키이므로 BCNF를 만족한다.  
  * **데이터 무결성**: PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK 제약조건을 통해 개체, 참조, 도메인 무결성을 데이터베이스 수준에서 강제한다. 이는 애플리케이션 코드의 실수를 방지하는 강력한 방어선 역할을 한다.

#### **2.2. 스키마 진화(Schema Evolution) 관리**

* **도구 채택**: Alembic  
  * **근거**: Alembic은 SQLAlchemy를 위한 경량 데이터베이스 마이그레이션 도구로, 모든 스키마 변경 사항을 파이썬 코드로 작성된 '마이그레이션 스크립트'로 관리할 수 있게 해준다. 이는 "스키마를 코드로 취급(Schema-as-Code)"하는 원칙을 실현하며, Git을 통한 버전 관리와 CI/CD 파이프라인 통합을 용이하게 한다.  
* **프로세스**:  
  1. **초기화**: alembic init alembic 명령어로 마이그레이션 환경을 설정한다.  
  2. **버전 생성**: alembic revision \-m "add tv\_programs table"과 같이 스키마 변경 시마다 새로운 마이그레이션 스크립트를 자동 생성한다.  
  3. **스크립트 작성**: 생성된 파일의 upgrade() 함수에는 스키마를 변경하는 코드(e.g., op.create\_table(...))를, downgrade() 함수에는 변경 사항을 되돌리는 코드(e.g., op.drop\_table(...))를 작성한다.  
  4. **적용**: alembic upgrade head 명령어로 최신 버전의 스키마를 데이터베이스에 적용한다.  
  * 이 모든 스크립트는 Git으로 관리되어, 팀원 모두가 동일한 데이터베이스 스키마 버전을 유지하고 변경 이력을 추적할 수 있다.

### **Part 3: 사전 준비 프로세스 상세 설계: 인터페이스와 구현체의 분리**

클린 아키텍처의 의존성 규칙을 준수하며, 각 기능 컴포넌트를 **추상 인터페이스(Port)** 와 **구체적인 구현체(Adapter)** 로 분리하여 설계한다. 이는 시스템의 유연성과 테스트 용이성을 극대화한다.

#### **3.1. 추상 인터페이스 (Ports) 설계 (src/domain/interfaces/)**

이 인터페이스들은 시스템의 핵심 로직(Use Case)이 "무엇을 할 것인가"만을 정의하며, "어떻게 할 것인가"에 대한 세부사항은 전혀 알지 못한다. abc 모듈을 사용하여 추상 베이스 클래스(ABC)로 정의한다.

* **data\_loader\_interface.py**:  
  from abc import ABC, abstractmethod  
  import pandas as pd

  class DataLoaderInterface(ABC):  
      @abstractmethod  
      def get\_processed\_movielens\_data(self) \-\> pd.DataFrame:  
          """전처리된 MovieLens 데이터를 로드하여 반환한다."""  
          pass

* **persona\_generator\_interface.py**:  
  from abc import ABC, abstractmethod  
  import pandas as pd

  class PersonaGeneratorInterface(ABC):  
      @abstractmethod  
      def generate\_dummy\_watch\_history(self, persona\_id: str) \-\> pd.DataFrame:  
          """특정 페르소나를 위한 가상 시청 기록을 생성한다."""  
          pass

* **rating\_predictor\_interface.py**:  
  from abc import ABC, abstractmethod  
  from typing import Dict, List

  class RatingPredictorInterface(ABC):  
      @abstractmethod  
      def predict\_ratings(self, user\_id: int, movie\_ids: List\[int\]) \-\> Dict\[int, float\]:  
          """주어진 사용자와 영화 목록에 대한 예상 평점을 예측한다."""  
          pass

* **content\_labeler\_interface.py**:  
  from abc import ABC, abstractmethod  
  from typing import List

  class ContentLabelerInterface(ABC):  
      @abstractmethod  
      def generate\_labels(self, title: str, overview: str) \-\> List\[str\]:  
          """콘텐츠의 제목과 줄거리를 기반으로 시맨틱 라벨을 생성한다."""  
          pass

* **schedule\_crawler\_interface.py**:  
  from abc import ABC, abstractmethod  
  from typing import List, Dict, Any

  class ScheduleCrawlerInterface(ABC):  
      @abstractmethod  
      def fetch\_schedule(self, target\_date: str) \-\> List\[Dict\[str, Any\]\]:  
          """특정 날짜의 IPTV 편성표를 가져온다."""  
          pass

#### **3.2. 구체적인 구현체 (Adapters) 설계 (src/adapters/)**

각 어댑터는 위에서 정의한 인터페이스를 상속받아, 특정 기술이나 라이브러리를 사용하여 실제 기능을 구현한다.

* **file\_data\_loader.py**:  
  * DataLoaderInterface를 구현.  
  * pandas를 사용하여 로컬 Parquet 파일에서 데이터를 읽어오는 로직을 포함.  
* **default\_persona\_generator.py**:  
  * PersonaGeneratorInterface를 구현.  
  * V1 계획서에서 설계된 로직(선호 장르 기반 샘플링 및 평점 부여)을 그대로 구현.  
* **torch\_rating\_predictor.py**:  
  * RatingPredictorInterface를 구현.  
  * PyTorch를 사용하여 NCFModel을 로드하고, 추론을 통해 예상 평점을 계산하는 로직을 포함.  
* **gemini\_content\_labeler.py**:  
  * ContentLabelerInterface를 구현.  
  * **Part 1에서 설계된 보안 원칙을 적용**: .env 파일에서 GEMINI\_API\_KEY를 로드하여 google-generativeai 라이브러리와 연동한다.  
  * **캐싱 로직 적용**: generate\_labels 메서드 내부에 infrastructure.cache\_manager를 사용하여 DB 캐시를 조회하고, 캐시 미스 시에만 API를 호출하도록 구현한다.  
* **selenium\_schedule\_crawler.py**:  
  * ScheduleCrawlerInterface를 구현.  
  * Selenium과 BeautifulSoup을 사용하여 특정 웹사이트의 편성표를 스크래핑하는 로직을 포함.  
  * **파일 캐싱 로직 적용**: 메서드 실행 시 먼저 파일 캐시가 있는지 확인하고, 없을 경우에만 크롤링을 실행하도록 구현한다.

이러한 분리 구조 덕분에, 예를 들어 나중에 Gemini API 대신 다른 LLM을 사용하고 싶다면, AnotherContentLabeler 클래스를 새로 만들어 ContentLabelerInterface를 구현하기만 하면 된다. 시스템의 핵심 로직인 use\_case 코드는 전혀 수정할 필요가 없다. 이것이 바로 클린 아키텍처가 제공하는 유연성과 유지보수성의 핵심이다.

**(다음 파트에서 Use Case와 Presentation 계층을 상세히 설계합니다...)**