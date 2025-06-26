### **Part 4: 도메인 및 프레젠테이션 계층 상세 설계**

이 파트는 시스템의 핵심 비즈니스 로직과 사용자 인터페이스를 정의한다. 클린 아키텍처의 의존성 규칙에 따라, 도메인 계층(Use Case)은 외부의 어떤 기술에도 의존하지 않으며, 프레젠테이션 계층은 사용자의 입력을 받아 Use Case를 실행하고 그 결과를 시각화하는 역할에 집중한다.

#### **4.1. 데이터 전송 객체 (DTOs) 설계 (src/domain/dtos.py)**

* **목표**: 각 계층 간에 데이터를 안정적이고 명확하게 전달하기 위해, Pydantic을 사용한 데이터 전송 객체(DTO)를 정의한다. 이는 데이터의 구조와 타입을 강제하여 런타임 에러를 방지하고, 코드의 가독성을 높인다.  
* **DTO 명세**:  
  \# src/domain/dtos.py  
  from pydantic import BaseModel, Field  
  from typing import List, Dict  
  from datetime import datetime

  class WatchedMovieDTO(BaseModel):  
      """페르소나의 가상 시청 기록을 나타내는 DTO"""  
      movie\_id: int  
      title: str  
      rating: float

  class LabelledContentDTO(BaseModel):  
      """LLM에 의해 라벨링된 콘텐츠를 나타내는 DTO"""  
      title: str  
      labels: List\[str\]  
      predicted\_rating: float | None \= None \# 영화 클러스터에만 해당

  class RecommendedProgramDTO(BaseModel):  
      """최종 추천된 TV 프로그램을 나타내는 DTO"""  
      channel: str  
      title: str  
      start\_time: datetime  
      end\_time: datetime  
      similarity\_score: float \= Field(..., ge=0, le=1) \# 0과 1 사이의 값  
      reason: str

  class RecommendationResultDTO(BaseModel):  
      """Use Case의 최종 실행 결과를 담는 메인 DTO"""  
      persona\_name: str  
      persona\_description: str  
      watch\_history: List\[WatchedMovieDTO\]  
      preference\_cluster: List\[LabelledContentDTO\]  
      recommended\_programs: List\[RecommendedProgramDTO\]

#### **4.2. 유스케이스(Use Case) 상세 설계 (src/domain/use\_cases/recommend\_channels\_use\_case.py)**

* **클래스명**: RecommendChannelsUseCase  
* **역할**: 시스템의 핵심 비즈니스 로직을 수행하는 **오케스트레이터**. 외부 세계(프레임워크, DB, API)에 대한 구체적인 구현을 전혀 알지 못하며, 오직 추상 인터페이스(Ports)에만 의존한다.  
* **상세 구현 계획**:  
  1. **\_\_init\_\_ 메서드 (의존성 주입)**:  
     * **Input**: Part 2에서 정의한 모든 인터페이스의 구현체 객체들.  
     * **Process**: 생성자에서 직접 객체를 생성하지 않고, 외부(Composition Root, 이 경우 app.py)로부터 인터페이스의 구현체를 주입받는다(Dependency Injection). 이는 DIP(의존성 역전 원칙)의 핵심 실천이다.  
     * **의사 코드(Pseudo-code)**:  
       \# src/domain/use\_cases/recommend\_channels\_use\_case.py  
       from src.domain.interfaces import \* \# 모든 인터페이스 임포트

       class RecommendChannelsUseCase:  
           def \_\_init\_\_(  
               self,  
               persona\_generator: PersonaGeneratorInterface,  
               rating\_predictor: RatingPredictorInterface,  
               content\_labeler: ContentLabelerInterface,  
               schedule\_crawler: ScheduleCrawlerInterface,  
               embedding\_model \# 실제 임베딩 모델 객체  
           ):  
               self.persona\_gen \= persona\_generator  
               self.rating\_predictor \= rating\_predictor  
               self.labeler \= content\_labeler  
               self.crawler \= schedule\_crawler  
               self.embedding\_model \= embedding\_model  
               \# ... 기타 설정 로드 ...

  2. **execute(self, persona\_id: str, target\_date: str) \-\> RecommendationResultDTO 메서드**:  
     * **Input**: persona\_id와 target\_date라는 순수한 데이터.  
     * **Process**: V1의 RecommendationEngine 로직을 그대로 수행하되, 모든 외부 상호작용은 주입받은 인터페이스의 메서드를 통해 이루어진다.  
       1. 가상 시청 기록 생성: self.persona\_gen.generate\_dummy\_watch\_history(...)  
       2. 잠재 선호 영화 예측: self.rating\_predictor.predict\_ratings(...)  
       3. 편성표 수집: self.crawler.fetch\_schedule(...)  
       4. 콘텐츠 라벨링: self.labeler.generate\_labels(...) (사용자 선호 영화, 방송 프로그램 모두에 적용)  
       5. 임베딩 및 유사도 계산: self.embedding\_model.encode(...) 및 코사인 유사도 계산.  
       6. 최종 결과 조합: 모든 처리된 데이터를 RecommendationResultDTO 객체에 담아 반환한다. 유효성 검사는 Pydantic이 자동으로 수행한다.  
     * **Output**: RecommendationResultDTO 객체. 실패 시 명시적인 예외를 발생시킨다.

#### **4.3. 프레젠테이션 계층(Presentation Layer) 상세 설계 (src/presentation/app.py)**

* **역할**: Streamlit을 사용하여 UI를 구축하고, 애플리케이션의 **Composition Root**로서 모든 의존성을 조립하며, Use Case를 실행하고 그 결과를 사용자에게 시각적으로 표현한다.  
* **상세 구현 계획**:  
  1. **애플리케이션 초기화 (Composition Root)**:  
     * **목표**: 애플리케이션 시작 시, 필요한 모든 구체적인 어댑터(Adapter) 인스턴스를 생성하고, 이를 Use Case에 주입하여 완전히 구성된 RecommendChannelsUseCase 객체를 만든다.  
     * **캐싱**: 이 과정은 비용이 많이 들므로, @st.cache\_resource 데코레이터를 사용하여 생성된 use\_case 객체를 캐싱하고, 페이지 리로드 시 재사용한다.  
     * **의사 코드(Pseudo-code)**:  
       \# src/presentation/app.py  
       import streamlit as st  
       from dotenv import load\_dotenv  
       from src.adapters import \* \# 모든 어댑터 구현체 임포트  
       from src.domain.use\_cases.recommend\_channels\_use\_case import RecommendChannelsUseCase  
       from sentence\_transformers import SentenceTransformer  
       import yaml

       @st.cache\_resource  
       def setup\_application():  
           """애플리케이션의 모든 의존성을 조립하고 Use Case를 반환한다."""  
           load\_dotenv() \# .env 파일 로드

           with open('config/default\_config.yml') as f:  
               config \= yaml.safe\_load(f)

           \# 1\. 모든 어댑터(구현체) 인스턴스 생성  
           data\_loader \= FileDataLoader(config)  
           movielens\_df \= data\_loader.get\_processed\_movielens\_data()  
           persona\_gen \= DefaultPersonaGenerator(config, movielens\_df)  
           rating\_predictor \= TorchRatingPredictor(config)  
           labeler \= GeminiContentLabeler(config) \# API 키는 내부적으로 os.getenv() 사용  
           crawler \= SeleniumScheduleCrawler(config)  
           embedding\_model \= SentenceTransformer(config\['paths'\]\['embedding\_model\_name'\])

           \# 2\. Use Case에 구현체들을 주입하여 최종 객체 생성  
           use\_case \= RecommendChannelsUseCase(  
               persona\_generator=persona\_gen,  
               rating\_predictor=rating\_predictor,  
               content\_labeler=labeler,  
               schedule\_crawler=crawler,  
               embedding\_model=embedding\_model  
           )  
           return use\_case

       \# 애플리케이션의 메인 진입점  
       try:  
           recommend\_use\_case \= setup\_application()  
           \# \--- Streamlit UI 코드 시작 \---  
       except Exception as e:  
           st.error(f"애플리케이션 초기화에 실패했습니다: {e}")

  2. **UI 로직 및 상호작용**:  
     * **사이드바 제어판**: V1 설계와 동일하게 st.sidebar를 사용하여 페르소나, 날짜, 시간을 선택하고 실행 버튼을 배치한다.  
     * **실행 및 에러 처리**:  
       * 실행 버튼 클릭 시, st.spinner를 표시하고 try-except 블록 내에서 recommend\_use\_case.execute()를 호출한다.  
       * **성공 시**: 반환된 RecommendationResultDTO 객체를 st.session\_state.results에 저장한다.  
       * **실패 시**: Use Case에서 발생한 예외를 잡아 st.error()를 통해 사용자에게 친화적인 에러 메시지(예: "편성표 정보를 가져오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")를 표시한다.  
     * **결과 시각화**:  
       * st.session\_state.results가 존재하면, DTO 객체에서 데이터를 꺼내 V1 계획서에서 설계했던 미려한 카드 레이아웃과 데이터프레임으로 결과를 시각화한다.  
       * 모든 데이터는 정형화된 DTO를 통해 전달되므로, UI 코드는 데이터의 존재 여부나 타입을 걱정할 필요 없이 안정적으로 렌더링에만 집중할 수 있다.  
     * **Next-Up 추천 로직**:  
       * '이어서 보기' 버튼 로직 역시 recommend\_use\_case.get\_next\_up\_recommendations()를 호출하는 방식으로 변경되어, UI는 비즈니스 로직을 직접 수행하지 않고 Use Case에 위임한다.

이러한 설계는 각 계층이 자신의 책임(SRP)에만 집중하도록 만든다. app.py는 오직 '보여주는 것'과 '의존성을 조립하는 것'에만 책임이 있고, recommend\_channels\_use\_case.py는 오직 '비즈니스 규칙을 실행하는 것'에만 책임이 있으며, 각 어댑터는 '특정 기술을 사용하여 인터페이스를 구현하는 것'에만 책임이 있다. 이것이 바로 코드 작성 가이드에서 강조하는 유지보수 가능하고 테스트 용이한 '살아있는 시스템'의 구체적인 모습이다.

**(다음 파트에서 테스팅, CI/CD, 그리고 최종 관리 계획을 상세히 설계합니다...)**