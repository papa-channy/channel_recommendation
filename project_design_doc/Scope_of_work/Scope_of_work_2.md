### **Part 2 of 5: 데이터 계층 상세 설계 (ERD, 스키마, 테이블 명세)**

이 파트에서는 프로젝트의 뼈대인 데이터 계층을 집중적으로 설계합니다. `ERD_Guide.md`의 정규화, 무결성 원칙과 `Code_Guide.md`의 장인 정신을 바탕으로, 실제 운영을 가정한 프로덕션 등급의 **MySQL 데이터베이스 스키마**를 정의합니다.

---

### **2.1. 데이터베이스 설계 원칙 및 철학**

본 데이터베이스는 `ERD_Guide.md`에서 강조하는 다음 원칙들을 철저히 준수하여 설계합니다.

- **구조적 무결성**: 데이터 중복을 최소화하고 삽입/갱신/삭제 이상 현상을 방지하기 위해 **제3정규형(3NF) 또는 BCNF**까지 정규화를 수행합니다.
- **데이터 무결성 강제**: `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `CHECK` 제약조건을 적극적으로 활용하여 데이터의 정확성과 일관성을 애플리케이션이 아닌 **데이터베이스 수준에서 강제**합니다. 이는 시스템의 안정성을 높이는 가장 강력한 방어선입니다.
- **명확한 명명 규칙**: 테이블명은 복수형(e.g., `users`), 컬럼명은 `snake_case`를 사용하며, 기본 키(PK)는 `테이블명_id` (e.g., `user_id`) 형식으로 명명하여 조인 시 모호함을 제거합니다. 'id'와 같은 일반적인 PK명 안티패턴을 지양합니다.
- **성능 고려 설계**: 자주 조회되는 컬럼, 특히 외래 키(FK)와 `WHERE`절에 사용될 컬럼에는 **인덱스(Index)**를 선제적으로 설계하여 쿼리 성능을 보장합니다.

### **2.2. 개념적 설계: ERD (Entity-Relationship Diagram)**

시스템의 핵심 엔티티와 관계는 다음과 같습니다.

- **주요 엔티티**: `users`, `movies`, `genres`, `ratings`, `tv_programs`, `labels_cache`
- **주요 관계**:
    - `users`와 `ratings`는 1:N 관계입니다. (한 명의 사용자는 여러 평점을 남길 수 있습니다.)
    - `movies`와 `ratings`는 1:N 관계입니다. (하나의 영화는 여러 평점을 가질 수 있습니다.)
    - `movies`와 `genres`는 **M:N 관계**입니다. (하나의 영화는 여러 장르를, 하나의 장르는 여러 영화를 가질 수 있습니다.) -> 이를 해소하기 위해 중간에 **`movie_genres`** 라는 연결 테이블(Junction Table)을 둡니다.

**ERD 다이어그램 시각화:**

코드 스니펫

```
erDiagram
    users {
        INT user_id PK
        DATETIME created_at
    }
    ratings {
        INT rating_id PK
        INT user_id FK
        INT movie_id FK
        FLOAT rating
        DATETIME rated_at
    }
    movies {
        INT movie_id PK
        VARCHAR title
        TEXT overview
        INT release_year
        VARCHAR poster_path
    }
    genres {
        INT genre_id PK
        VARCHAR genre_name
    }
    movie_genres {
        INT movie_id PK, FK
        INT genre_id PK, FK
    }
    tv_programs {
        INT program_id PK
        VARCHAR channel_name
        VARCHAR title
        TEXT synopsis
        DATETIME start_time
        DATETIME end_time
    }
    labels_cache {
        VARCHAR content_hash PK
        TEXT labels_json
        DATETIME created_at
    }

    users ||--o{ ratings : "has"
    movies ||--o{ ratings : "receives"
    movies }|--|{ movie_genres : "maps"
    genres }|--|{ movie_genres : "maps"
```

### **2.3. 물리적 설계: MySQL 테이블 명세 (CREATE TABLE 구문)**

각 테이블의 상세 명세와 `CREATE TABLE` 구문은 다음과 같습니다. 모든 테이블은 `utf8mb4` 캐릭터셋을 사용하여 다양한 언어와 이모지를 지원하도록 설정합니다.

---

**1. `users` 테이블**

- **설명**: 사용자를 식별합니다. 현재는 외부 데이터셋(`ratings.csv`)의 `userId`를 그대로 사용하며, 페르소나 기반 시뮬레이션의 주체입니다.
- **컬럼**:
    - `user_id` (PK): 사용자 고유 ID. `ratings.csv`의 `userId`와 매핑됩니다.
    - `created_at`: 사용자 정보 생성 시점.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS users (
    user_id      INT UNSIGNED NOT NULL COMMENT '사용자 고유 ID (MovieLens의 userId)',
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
    PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보 테이블';
```

---

**2. `genres` 테이블**

- **설명**: 영화 및 TV 프로그램의 장르를 중복 없이 관리합니다. 'Action|Adventure'와 같은 데이터를 정규화하여 관리합니다.
- **컬럼**:
    - `genre_id` (PK): 장르 테이블의 고유 식별자 (Auto Increment).
    - `genre_name`: 장르명 (e.g., 'Action', 'Comedy'). `UNIQUE` 제약조건으로 중복을 방지합니다.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS genres (
    genre_id     INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '장르 고유 ID',
    genre_name   VARCHAR(50) NOT NULL COMMENT '장르명',
    PRIMARY KEY (genre_id),
    UNIQUE INDEX uix_genre_name (genre_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='장르 정보 마스터 테이블';
```

---

**3. `movies` 테이블**

- **설명**: 영화의 메타데이터를 저장합니다. `movies.csv`의 데이터를 기반으로 합니다.
- **컬럼**:
    - `movie_id` (PK): 영화 고유 ID. `movies.csv`의 `movieId`와 매핑됩니다.
    - `title`: 영화 제목.
    - `release_year`: 출시 연도 (제목에서 추출).
    - `overview`, `poster_path`: 추후 외부 API(TMDb 등) 연동을 통해 확장될 수 있는 필드입니다.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS movies (
    movie_id      INT UNSIGNED NOT NULL COMMENT '영화 고유 ID (MovieLens의 movieId)',
    title         VARCHAR(255) NOT NULL COMMENT '영화 제목',
    release_year  SMALLINT UNSIGNED NULL COMMENT '출시 연도',
    overview      TEXT NULL COMMENT '영화 줄거리 (TMDb 연동용)',
    poster_path   VARCHAR(255) NULL COMMENT '포스터 이미지 경로 (TMDb 연동용)',
    PRIMARY KEY (movie_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='영화 메타데이터 테이블';
```

---

**4. `movie_genres` 연결 테이블**

- **설명**: 영화와 장르의 다대다(M:N) 관계를 해소하기 위한 연결 테이블입니다.
- **컬럼**:
    - `movie_id` (PK, FK): `movies` 테이블을 참조하는 외래 키.
    - `genre_id` (PK, FK): `genres` 테이블을 참조하는 외래 키.
    - 두 컬럼을 복합 기본 키로 사용하여 (영화, 장르) 조합의 유일성을 보장합니다.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id     INT UNSIGNED NOT NULL COMMENT '영화 고유 ID',
    genre_id     INT UNSIGNED NOT NULL COMMENT '장르 고유 ID',
    PRIMARY KEY (movie_id, genre_id),
    CONSTRAINT fk_movie_genres_movie FOREIGN KEY (movie_id) REFERENCES movies (movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_movie_genres_genre FOREIGN KEY (genre_id) REFERENCES genres (genre_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='영화-장르 매핑 테이블';
```

---

**5. `ratings` 테이블**

- **설명**: 사용자가 영화에 대해 매긴 평점 정보를 저장합니다. `ratings.csv`의 핵심 데이터입니다.
- **컬럼**:
    - `rating_id` (PK): 평점 데이터의 고유 식별자 (Auto Increment).
    - `user_id` (FK): `users` 테이블을 참조합니다.
    - `movie_id` (FK): `movies` 테이블을 참조합니다.
    - `rating`: 평점 (0.5 ~ 5.0 사이의 값). `CHECK` 제약조건으로 데이터 유효성을 검증합니다.
    - `rated_at`: 평점을 매긴 시점. `ratings.csv`의 `timestamp`를 `DATETIME`으로 변환하여 저장합니다.
    - `(user_id, movie_id)`에 `UNIQUE` 인덱스를 설정하여 한 사용자가 한 영화에 대해 두 번 평점을 남기는 것을 방지합니다.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS ratings (
    rating_id    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '평점 고유 ID',
    user_id      INT UNSIGNED NOT NULL COMMENT '사용자 고유 ID',
    movie_id     INT UNSIGNED NOT NULL COMMENT '영화 고유 ID',
    rating       DECIMAL(2, 1) NOT NULL COMMENT '사용자가 매긴 평점',
    rated_at     TIMESTAMP NOT NULL COMMENT '평가 시각',
    PRIMARY KEY (rating_id),
    CONSTRAINT fk_ratings_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ratings_movie FOREIGN KEY (movie_id) REFERENCES movies (movie_id) ON DELETE CASCADE,
    UNIQUE INDEX uix_user_movie (user_id, movie_id),
    INDEX ix_movie_id (movie_id), -- 영화별 평점 조회를 위한 인덱스
    CONSTRAINT chk_rating CHECK (rating >= 0.5 AND rating <= 5.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자-영화 평점 정보';
```

---

**6. `tv_programs` 테이블**

- **설명**: 크롤링을 통해 수집된 실시간 IPTV 편성표 정보를 저장합니다.
- **컬럼**:
    - `program_id` (PK): 프로그램 정보의 고유 식별자.
    - `channel_name`: 방송 채널명.
    - `title`, `synopsis`: 프로그램 제목과 줄거리.
    - `start_time`, `end_time`: 방송 시작 및 종료 시각.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS tv_programs (
    program_id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '편성 프로그램 고유 ID',
    channel_name    VARCHAR(100) NOT NULL COMMENT '채널명',
    title           VARCHAR(255) NOT NULL COMMENT '프로그램 제목',
    synopsis        TEXT NULL COMMENT '프로그램 줄거리',
    start_time      TIMESTAMP NOT NULL COMMENT '방송 시작 시각',
    end_time        TIMESTAMP NOT NULL COMMENT '방송 종료 시각',
    crawled_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '정보 수집 시각',
    PRIMARY KEY (program_id),
    INDEX ix_start_time (start_time) -- 특정 시간대 방송 조회를 위한 인덱스
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='IPTV 편성표 정보';
```

---

**7. `labels_cache` 테이블**

- **설명**: LLM(Gemini)을 통해 생성된 콘텐츠 라벨을 캐싱하기 위한 테이블입니다. 중복 API 호출을 방지하여 비용과 시간을 절약합니다.
- **컬럼**:
    - `content_hash` (PK): 콘텐츠(영화 제목+줄거리)의 SHA256 해시값. 콘텐츠의 유일성을 보장합니다.
    - `labels_json`: 생성된 라벨 리스트를 JSON 문자열 형태로 저장합니다.
    - `created_at`: 캐시 생성 시점.

<!-- end list -->

SQL

```
CREATE TABLE IF NOT EXISTS labels_cache (
    content_hash  VARCHAR(64) NOT NULL COMMENT '콘텐츠(제목+줄거리)의 SHA256 해시값',
    labels_json   JSON NOT NULL COMMENT '라벨 리스트 (JSON 배열)',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '캐시 생성 시각',
    PRIMARY KEY (content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='LLM 생성 라벨 캐시 테이블';
```

### **2.4. 스키마 진화(Schema Evolution) 관리**

- **도구 채택**: **Alembic**
    - **근거**: Alembic은 SQLAlchemy를 위한 데이터베이스 마이그레이션 도구로, 모든 스키마 변경 이력을 파이썬 코드로 작성된 버전 스크립트로 관리합니다. 이는 "스키마를 코드로 취급(Schema-as-Code)"하는 원칙을 실현하며, Git을 통한 버전 관리와 CI/CD 파이프라인 통합을 용이하게 합니다.
- **프로세스**:
    1. **초기화**: `alembic init alembic` 명령어로 마이그레이션 환경을 설정합니다.
    2. **버전 생성**: 스키마 변경 시 `alembic revision -m "add new_feature table"`과 같이 새로운 마이그레이션 스크립트를 자동 생성합니다.
    3. **스크립트 작성**: 생성된 파일의 `upgrade()` 함수에는 스키마 변경 코드를, `downgrade()` 함수에는 롤백 코드를 작성합니다.
    4. **적용**: `alembic upgrade head` 명령어로 최신 버전의 스키마를 데이터베이스에 적용합니다.