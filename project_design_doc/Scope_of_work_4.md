### **Part 5: 품질 보증 및 자동화: 살아있는 코드의 신진대사**

'살아있는 시스템'은 건강한 신진대사, 즉 품질을 지속적으로 검증하고 개선하는 자동화된 프로세스를 통해 유지된다. 본 파트는 TDD, CI/CD 파이프라인 등 현대적인 개발 프랙티스를 프로젝트에 적용하는 구체적인 방법을 설계한다.

#### **5.1. 테스트 주도 개발 (TDD) 실천 전략**

* **철학**: TDD는 단순히 버그를 찾는 활동이 아니라, 코드를 작성하기 전에 요구사항을 명확히 하고, 테스트 가능한 설계를 유도하는 **설계 기술**이다. 우리는 **Red-Green-Refactor** 사이클을 엄격히 준수한다.  
* **표준 도구**:  
  * **테스트 프레임워크**: pytest  
  * **모의 객체(Mocking) 라이브러리**: unittest.mock  
* **TDD 사이클 예시: DefaultPersonaGenerator의 평점 부여 로직**  
  1. **RED (실패하는 테스트 작성)**: 먼저, 선호 장르의 영화가 실제로 더 높은 평점을 받는지 검증하는 테스트를 tests/adapters/test\_persona\_generator.py에 작성한다. 이 시점에는 generate\_dummy\_watch\_history의 평점 부여 로직이 없으므로 테스트는 실패해야 한다.  
     \# tests/adapters/test\_persona\_generator.py

     def test\_dummy\_history\_gives\_higher\_ratings\_to\_favorite\_genres(persona\_generator, sample\_persona):  
         """선호 장르 영화가 비선호 장르 영화보다 평균 평점이 높은지 검증한다."""  
         \# GIVEN: 페르소나와 생성기  
         favorite\_genres \= sample\_persona\['favorite\_genres'\]

         \# WHEN: 가상 시청 기록 생성  
         history\_df \= persona\_generator.generate\_dummy\_watch\_history(sample\_persona\['persona\_id'\], num\_records=50)

         \# THEN: 평점 분리 및 평균 비교  
         is\_favorite \= history\_df\['genres'\].apply(lambda genres: any(g in genres for g in favorite\_genres))  
         favorite\_ratings\_mean \= history\_df\[is\_favorite\]\['rating'\].mean()  
         other\_ratings\_mean \= history\_df\[\~is\_favorite\]\['rating'\].mean()

         assert favorite\_ratings\_mean \> other\_ratings\_mean

  2. **GREEN (테스트를 통과하는 최소 코드 작성)**: 이제 src/adapters/default\_persona\_generator.py에 위 테스트를 통과시킬 최소한의 코드를 작성한다.  
     \# src/adapters/default\_persona\_generator.py  
     \# in generate\_dummy\_watch\_history method...

     \# 평점 부여 로직  
     ratings \= \[\]  
     for index, movie in final\_movies\_df.iterrows():  
         is\_favorite \= any(g in movie\['genres'\] for g in favorite\_genres)  
         if is\_favorite:  
             \# 높은 평점 부여  
             rating \= random.uniform(3.5, 5.0)  
         else:  
             \# 상대적으로 낮은 평점 부여  
             rating \= random.uniform(2.5, 4.0)  
         ratings.append(round(rating \* 2\) / 2\) \# 0.5 단위로 반올림

     final\_movies\_df\['rating'\] \= ratings

  3. **REFACTOR (코드 개선)**: 테스트가 통과하는 것을 확인한 후, 방금 작성한 코드의 가독성을 높이고 중복을 제거하는 등 설계를 개선한다. 예를 들어, 평점 부여 로직을 별도의 private 메서드로 분리할 수 있다.

#### **5.2. 향후 과제 (Future Roadmap)**

* **V1.1: 추천 로직 고도화**:  
  * **피드백 루프**: 사용자가 추천 결과에 대해 '좋아요/싫어요' 피드백을 남기는 기능을 추가하고, 이를 주기적으로 재학습 데이터에 반영하여 모델 성능을 점진적으로 개선한다.  
  * **상황 인지 추천**: 시간, 요일 정보를 추천 모델의 피처로 활용하여, '주말 오후에 볼만한 예능'과 같은 상황 맞춤형 추천을 제공한다.  
* **V1.2: 사용자 경험(UX) 혁신**:  
  * **설명 가능한 AI (XAI)**: 추천 이유를 단순히 '취향 유사'가 아닌, "고객님이 재미있게 보신 영화 \<인셉션\>의 '\#꿈조작', '\#치밀한구성' 라벨과 이 프로그램의 '\#시간여행', '\#두뇌싸움' 라벨이 유사하여 추천합니다."와 같이 구체적인 라벨 비교를 통해 제시한다.  
  * **대화형 인터페이스**: Streamlit 채팅 컴포넌트를 활용하여 "액션 영화 중에 요즘 볼만한 거 없어?"와 같은 자연어 질문에 답변하는 챗봇형 추천 기능을 구현한다.  
* **V2.0: 프로덕션 등급으로 전환**:  
  * **서버리스 배포**: Docker 컨테이너를 AWS Fargate나 Google Cloud Run에 배포하여 서버 관리가 필요 없는 운영 환경을 구축한다.  
  * **비동기 크롤러**: 편성표 크롤링과 LLM 라벨링처럼 시간이 오래 걸리는 I/O 바운드 작업을 asyncio와 HTTPX를 사용하여 비동기적으로 처리, 전체 시스템의 응답성을 향상시킨다.  
  * **데이터베이스 전환**: SQLite에서 PostgreSQL과 같은 프로덕션 등급의 관계형 데이터베이스로 마이그레이션하여 동시성 처리 능력과 안정성을 확보한다.

#### **5.3. 최종 결론**

본 상세 작업 계획서 V2는 단순한 기능 목록을 넘어, **'어떻게(How)'** 와 **'왜(Why)'** 를 담은 살아있는 설계도이다. 클린 아키텍처를 통한 유연한 구조, .env를 활용한 철저한 보안, ERD 설계 가이드맵에 입각한 견고한 데이터베이스, 그리고 TDD와 CI/CD로 자동화된 품질 보증 프로세스는 이 프로젝트가 단순한 프로토타입을 넘어, 지속적으로 성장하고 발전할 수 있는 \*\*'장인의 코드'\*\*가 될 것임을 보증한다.

이 청사진을 바탕으로, 우리는 사용자의 숨겨진 취향을 발견하고 정보의 홍수 속에서 가장 빛나는 콘텐츠를 제안하는 지능형 미디어 큐레이터를 성공적으로 만들어낼 것이다.