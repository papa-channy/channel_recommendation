## **AI 기반 개인 맞춤형 TV 채널 추천 시스템: 상세 작업 계획서 (V2.0)**

### **문서 개요**

본 문서는 'AI 기반 개인 맞춤형 TV 채널 추천 시스템' 프로젝트의 \*\*실행 가능한 청사진(Executable Blueprint)\*\*이다. 코드 생성 AI가 본 문서를 해석하여 \*\*유지보수 가능하고, 확장 가능하며, 안전한 '살아있는 시스템'\*\*을 구현할 수 있도록, 모든 아키텍처 결정, 기능 명세, 데이터 흐름, 개발 프로세스를 장인 정신(Software Craftsmanship)에 입각하여 정의한다.

### **Part 1: 프로젝트 철학, 아키텍처 및 보안 환경 구축**

#### **1.1. 프로젝트 철학: 장인 정신과 살아있는 시스템**

본 프로젝트는 단순히 '작동하는 소프트웨어'를 넘어, \*\*'잘 만들어진 소프트웨어(Well-Crafted Software)'\*\*를 창조하는 것을 목표로 한다. 이는 코드 작성 가이드에서 제시된 장인 정신의 철학을 따르는 것으로, 다음과 같은 핵심 가치를 내재화한다:

* **내부 품질 우선**: 코드의 가독성, 테스트 용이성, 모듈성은 장기적인 개발 속도와 시스템의 건전성을 결정하는 가장 중요한 요소이다.  
* **지속적인 개선**: "보이스카우트 규칙"에 따라, 모든 코드는 발견했을 때보다 더 깨끗하게 만들어 놓고 떠나는 것을 원칙으로 하여 기술 부채를 적극적으로 관리한다.  
* **프로세스를 통한 품질 보증**: TDD, 코드 리뷰, CI/CD 자동화 등 체계화된 프로세스를 통해 품질을 개발 과정에 깊숙이 내재화한다.

궁극적인 목표는 시간이 지나도 가치를 잃지 않고, 변화에 유연하게 대응하며, 스스로의 건강 상태를 유지하는 \*\*'살아있는 유기체 같은 레포지토리'\*\*를 만드는 것이다.

#### **1.2. 시스템 아키텍처: 클린 아키텍처 (Clean Architecture)**

시스템의 유연성과 유지보수성을 극대화하기 위해, 로버트 C. 마틴의 **클린 아키텍처**를 채택한다. 이는 비즈니스 로직을 프레임워크, 데이터베이스, UI 등 외부 구현 세부사항으로부터 완벽하게 분리하는 것을 목표로 한다.

* **핵심 원칙: 의존성 규칙 (The Dependency Rule)**소스 코드의 모든 의존성은 오직 \*\*안쪽(고수준 정책)\*\*을 향해야 한다.  
* C4 모델 L1: 시스템 컨텍스트 (System Context)

  * **사용자(Persona)**: Streamlit 웹 UI를 통해 시스템과 상호작용한다.  
  * **AI TV 추천 시스템**: 본 프로젝트가 구축하는 핵심 시스템.  
  * **외부 시스템**:  
    * **MovieLens 데이터셋**: 시스템 초기 학습 데이터를 제공하는 정적 데이터 소스.  
    * **Google Gemini API**: 콘텐츠의 시맨틱 라벨링을 위해 실시간으로 호출되는 외부 LLM 서비스.  
    * **IPTV 편성표 웹사이트**: 실시간 방송 정보를 제공하는 외부 데이터 소스.  
* **계층 구조 (Layers)**  
  1. **Domain Layer (도메인 계층)**: 시스템의 가장 핵심.  
     * **Entities**: 전사적 비즈니스 규칙을 담는 객체. (이 프로젝트에서는 단순하여 명시적 Entity는 적음)  
     * **Use Cases (Interactors)**: 애플리케이션에 특화된 비즈니스 로직을 수행. RecommendationEngine이 여기에 해당한다. 이 계층은 외부의 어떤 변화에도 영향을 받지 않는다.  
  2. **Application Layer (애플리케이션 계층 \- Interface Adapters)**:  
     * **Interfaces (Ports)**: Use Case 계층이 외부 세계와 소통하기 위한 추상적인 '포트'를 정의한다. (e.g., ContentLabelerInterface, RatingPredictorInterface)  
     * **Controllers/Presenters**: 외부 요청을 Use Case가 이해할 수 있는 형식으로 변환하고, Use Case의 결과를 외부 세계가 이해할 수 있는 형식으로 변환한다. app.py의 Streamlit 코드 일부가 이 역할을 수행한다.  
  3. **Infrastructure Layer (인프라 계층 \- Frameworks & Drivers)**:  
     * **Adapters (구현체)**: Application 계층의 인터페이스에 대한 구체적인 구현. 외부 도구와 프레임워크에 직접 의존한다. (e.g., GeminiContentLabeler, TorchRatingPredictor, SeleniumScheduleCrawler)  
     * **Frameworks/DB**: Streamlit, PyTorch, Selenium, SQLite 등 실제 프레임워크와 드라이버.

#### **1.3. 폴더 구조 설계 (V2: 클린 아키텍처 반영)**

클린 아키텍처의 계층 구조를 명확히 반영하도록 폴더 구조를 재설계한다.

tv\_recommendation\_project/  
├── .github/workflows/         \# CI/CD 파이프라인  
├── config/  
│   └── default\_config.yml     \# ★★★ 비민감성 기본 설정만 포함  
├── data/                      \# 데이터 (이전과 동일)  
├── logs/                      \# 로그 파일 저장  
├── notebooks/                 \# 실험용 노트북  
├── saved\_models/              \# 학습된 모델 가중치  
├── src/  
│   ├── \_\_init\_\_.py  
│   ├── domain/                \# ★ 도메인 계층  
│   │   ├── \_\_init\_\_.py  
│   │   ├── use\_cases/         \# 유스케이스 (비즈니스 로직)  
│   │   │   └── recommend\_channels\_use\_case.py \# RecommendationEngine의 역할  
│   │   └── interfaces/        \# ★ 포트 (추상 인터페이스)  
│   │       ├── data\_loader\_interface.py  
│   │       ├── persona\_generator\_interface.py  
│   │       ├── rating\_predictor\_interface.py  
│   │       ├── content\_labeler\_interface.py  
│   │       └── schedule\_crawler\_interface.py  
│   ├── adapters/                \# ★ 어댑터 계층 (인터페이스 구현체)  
│   │   ├── \_\_init\_\_.py  
│   │   ├── file\_data\_loader.py  
│   │   ├── default\_persona\_generator.py  
│   │   ├── torch\_rating\_predictor.py  
│   │   ├── gemini\_content\_labeler.py  
│   │   └── selenium\_schedule\_crawler.py  
│   ├── infrastructure/          \# ★ 인프라 계층  
│   │   ├── \_\_init\_\_.py  
│   │   └── cache\_manager.py     \# SQLite 기반 캐시 관리  
│   ├── presentation/            \# ★ 프레젠테이션 계층  
│   │   ├── \_\_init\_\_.py  
│   │   └── app.py               \# Streamlit 애플리케이션  
│   └── utils/                   \# 범용 유틸리티  
│       └── ...  
├── tests/  
│   ├── domain/  
│   └── adapters/  
├── .env                       \# ★★★★★ 모든 민감 정보 저장 (API 키 등)  
├── .gitignore  
├── requirements.txt  
└── README.md

#### **1.4. 보안 환경 구축 및 설정 관리 (V2)**

* **보안 제1원칙: 민감 정보의 완벽한 분리**  
  * 모든 API 키, 비밀번호 등 민감 정보는 소스 코드 및 config.yml 파일에서 **완전히 제거**한다.  
  * 프로젝트 루트에 **.env** 파일을 생성하여 모든 민감 정보를 키-값 쌍으로 관리한다.  
  * **.gitignore** 파일에 .env를 **반드시 추가**하여 Git 저장소에 절대 포함되지 않도록 한다.  
* **.env 파일 예시**:  
  \# .env  
  \# Google Gemini API Key  
  GEMINI\_API\_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXX"

* **requirements.txt 의존성 추가**:  
  * python-dotenv: .env 파일을 읽어 환경 변수로 로드하기 위한 라이브러리.  
* **config/default\_config.yml (V2)**:  
  * 이 파일은 더 이상 민감 정보를 포함하지 않으며, 모델 파라미터, 파일 경로, 프롬프트 템플릿 등 **안전하게 공유 가능한 기본 설정**만을 담는다.  
  * api\_keys 섹션은 **완전히 삭제**된다.  
* **안전한 설정 로딩 프로세스**:  
  1. 애플리케이션 시작 시 (app.py 최상단) dotenv.load\_dotenv()를 호출하여 .env 파일의 변수들을 시스템 환경 변수로 로드한다.  
  2. API 키가 필요한 모듈(e.g., gemini\_content\_labeler.py)은 config 파일이 아닌, os.getenv("GEMINI\_API\_KEY")를 사용하여 환경 변수에서 직접 키를 가져온다.  
  3. **의사 코드(Pseudo-code) \- gemini\_content\_labeler.py**:  
     import os  
     import google.generativeai as genai  
     from dotenv import load\_dotenv

     class GeminiContentLabeler: \# Implements ContentLabelerInterface  
         def \_\_init\_\_(self, llm\_params):  
             \# 애플리케이션 시작점에서 한번만 호출되지만, 모듈별 안전장치로 추가 가능  
             load\_dotenv() 

             api\_key \= os.getenv("GEMINI\_API\_KEY")  
             if not api\_key:  
                 raise ValueError("GEMINI\_API\_KEY가 .env 파일에 설정되지 않았습니다.")

             genai.configure(api\_key=api\_key)  
             \# ... 이후 로직은 동일 ...

이러한 구조는 소스 코드를 안전하게 공개할 수 있도록 보장하며, 각 개발자는 자신의 로컬 .env 파일만 관리하면 된다. 배포 환경에서는 CI/CD 파이프라인을 통해 환경 변수를 안전하게 주입한다.

**(다음 파트에서 ERD 설계 가이드맵을 반영한 데이터 계층 설계를 계속합니다...)**