# 🤖 AI Agent 행동 제어를 위한 Default Docs File Tree 구성안

## 🎯 설계 원칙

파일 트리를 만들기 전에, AI Agent용 문서는 사람이 읽는 문서와 다르게 설계해야 합니다.

* **숫자 접두사 필수:** Agent의 참조 우선순위를 암시 (환각 방지)
* **산문보다 리스트/조건문:** 명확한 지시로 오류 최소화
* **행동 경계 명확화:** 허용/금지/승인필요 사항을 엄격히 분리
* **파일 단위 모듈화:** AI의 컨텍스트 윈도우(Context Window)를 효율적으로 사용
* **문서의 구조화:** AI 제어 문서와 일반 프로젝트 문서를 분리하여 참조 우선순위 고정

---

## 📂 권장 File Tree

```text
project-root/
│
├── .agent/                              # [최우선] Agent 전용 제어 문서
│   ├── 00_CHARTER.md                    # Agent 역할 정의, 핵심 원칙
│   ├── 01_FORBIDDEN_ACTIONS.md          # 절대 금지 행동 목록
│   ├── 02_APPROVAL_REQUIRED.md          # 사용자 승인 필요 행동 목록
│   ├── 03_DECISION_PRINCIPLES.md        # 충돌 상황 판단 기준 및 우선순위
│   └── 04_TASK_EXECUTION_POLICY.md      # 작업 수행 방식 (분석→계획→구현→검증)
│
├── docs/
│   ├── INDEX.md                         # 문서 전체 지도 + 상황별 참조 가이드
│   │
│   ├── 10_product/                      # 제품 도메인 이해
│   │   ├── overview.md                  # 제품 비전, 목적, 타겟 유저
│   │   ├── scope.md                     # In-scope / Out-of-scope 명시
│   │   ├── business-rules.md            # 비즈니스 규칙 및 핵심 워크플로우
│   │   ├── glossary.md                  # 도메인 용어 통일 사전 ★중요
│   │   └── success-metrics.md           # KPI, 성공 지표
│   │
│   ├── 20_architecture/                 # 구조적 제약
│   │   ├── system-overview.md           # 전체 시스템 구조 및 서비스 경계
│   │   ├── directory-structure.md       # 파일/폴더 생성 위치 규칙
│   │   ├── tech-stack.md                # 사용 언어, 프레임워크, 정확한 버전
│   │   ├── api-guidelines.md            # API 설계 규약 (REST/GraphQL 등)
│   │   └── data-model.md                # DB 스키마, 엔티티 관계
│   │
│   ├── 30_engineering/                  # 코드 품질 기준
│   │   ├── coding-standards.md          # 네이밍, 포맷팅, 설계 규칙
│   │   ├── error-handling.md            # 에러 처리 패턴, 로깅 규칙
│   │   ├── security-guidelines.md       # 보안 요구사항, 하드코딩 금지 등
│   │   └── performance-guidelines.md    # 성능 기준, 안티패턴
│   │
│   ├── 40_workflow/                     # 협업 및 개발 프로세스
│   │   ├── git-flow.md                  # 브랜치 전략, 커밋 메시지 규약
│   │   ├── implementation-process.md    # 구현 절차, 작업 단위 기준
│   │   ├── pr-policy.md                 # PR 단위, 작성 규칙
│   │   └── definition-of-done.md        # 완료 기준 (DoD)
│   │
│   ├── 50_quality/                      # 품질 보증
│   │   ├── test-strategy.md             # 테스트 범위, 도구, 필수 기준
│   │   ├── review-checklist.md          # 코드 리뷰 체크리스트
│   │   └── dependency-policy.md         # 새 라이브러리 추가 조건
│   │
│   ├── 60_templates/                    # 재사용 템플릿
│   │   ├── feature-spec.md
│   │   ├── bug-report.md
│   │   └── pr-template.md
│   │
│   └── 70_governance/                   # 문서 체계 운영
│       ├── doc-priority-order.md        # 문서 충돌 시 우선순위 규칙
│       ├── change-management.md         # 문서 변경 절차
│       └── CHANGELOG.md                 # 규칙 변경 이력
```

---

## 📄 핵심 파일 상세 설명

### 🛡️ `.agent/` — Agent 제어의 핵심 (최우선 참조)

이 폴더의 파일이 **다른 모든 문서보다 우선**합니다.

**`00_CHARTER.md` — Agent 헌장**
```markdown
# Role
You are a Senior Full-Stack Developer for [Product Name].

# Priority Rules (충돌 시 이 순서를 따름)
1. .agent/01_FORBIDDEN_ACTIONS.md
2. .agent/02_APPROVAL_REQUIRED.md
3. .agent/03_DECISION_PRINCIPLES.md
4. docs/ 하위 모든 문서

# Core Principles
- 모르는 것은 임의로 작성하지 말고 질문할 것
- 기존 코드 수정 시 반드시 원래 의도를 파악하고 유지할 것
- 한 번에 하나의 작업만 수행할 것
```

**`01_FORBIDDEN_ACTIONS.md` — 절대 금지**
```markdown
## 절대 금지 목록
- API Key, 비밀번호, 토큰 하드코딩
- 승인 없이 외부 라이브러리 추가
- 테스트 없이 핵심 비즈니스 로직 수정
- 프로덕션 데이터 직접 수정
- `any` 타입 사용 (TypeScript)
```

**`02_APPROVAL_REQUIRED.md` — 승인 필요**
```markdown
## 사용자 승인이 필요한 작업
- DB 스키마 변경
- 외부 의존성(라이브러리) 추가
- 아키텍처 패턴 변경
- 환경 변수 추가/수정
- 대규모 리팩토링 (50줄 이상 변경)
```

### 🧭 `docs/INDEX.md` — Agent의 네비게이션 맵

```markdown
## 상황별 참조 문서 가이드

| 상황 | 참조 문서 |
|------|-----------|
| 새 기능 구현 시작 | `10_product/scope.md` → `20_architecture/` |
| 새 파일 생성 위치 | `20_architecture/directory-structure.md` |
| 변수/함수 네이밍 | `30_engineering/coding-standards.md` |
| 에러 처리 방법 | `30_engineering/error-handling.md` |
| 커밋/PR 작성 | `40_workflow/git-flow.md` + `pr-policy.md` |
| 완료 여부 판단 | `40_workflow/definition-of-done.md` |
```

---

## 🚀 단계별 도입 전략

처음부터 모든 문서를 만들 필요는 없습니다. 프로젝트 상황에 맞게 점진적으로 확장하세요.

### Phase 1 — 즉시 시작 (필수 최소 세트)
```text
.agent/
  ├── 00_CHARTER.md
  ├── 01_FORBIDDEN_ACTIONS.md
  └── 02_APPROVAL_REQUIRED.md

docs/
  ├── INDEX.md
  ├── 10_product/overview.md
  ├── 10_product/glossary.md        ← 가장 먼저 만들 것 ★
  ├── 20_architecture/tech-stack.md
  ├── 30_engineering/coding-standards.md
  └── 40_workflow/definition-of-done.md
```

### Phase 2 — 팀 협업 시 추가
- `40_workflow/git-flow.md`
- `40_workflow/pr-policy.md`
- `50_quality/test-strategy.md`
- `60_templates/`
- `70_governance/doc-priority-order.md`

### Phase 3 — 확장 시 추가
- 나머지 전체 트리 구성

---

## 📌 문서 작성 핵심 원칙

| 나쁜 예 ❌ | 좋은 예 ✅ |
| :--- | :--- |
| "적절히 판단해서 처리" | **"A이면 B, B이면 C를 수행"** |
| "가능하면 테스트 작성" | **"로직 변경 시 단위 테스트 필수"** |
| "예쁜 변수명 사용" | **"변수명은 camelCase, 파일명은 kebab-case"** |
| "보안에 주의" | **"API Key는 반드시 환경변수로만 관리"** |

---

## 💡 운영 팁

1.  **`.agent/` 폴더를 최우선으로:** 이 폴더의 문서가 다른 모든 문서를 오버라이드하도록 설정하세요.
2.  **`glossary.md` 필수 관리:** AI와의 용어 통일이 안 되면 코드 전체가 꼬일 수 있습니다.
3.  **파일당 2,000 토큰 이내 유지:** AI가 프롬프트 컨텍스트를 잃어버리지 않도록 가볍게 유지하세요.
4.  **`CHANGELOG.md` 관리:** 규칙이 변경되었을 때 AI가 과거의 낡은 규칙을 참조하지 못하게 방지합니다.
5.  **RAG 환경 적용 시:** Vector DB를 활용한다면 `.agent/`를 항상 최우선 Chunk로 로드하도록 구성하세요.