"""
Pre-written default content for all harness template files.

These are not placeholders — they are production-quality defaults based on:
- Harness Engineering principles (Martin Fowler, Anthropic)
- Claude Code hooks & settings.json specification
- Battle-tested development best practices for AI-agent-driven projects

Load instantly without LLM calls via POST /api/harness/template.
"""

# ---------------------------------------------------------------------------
# .agent/ — Feedforward Controls (최우선 참조)
# ---------------------------------------------------------------------------

AGENT_00_CHARTER = """\
# Agent Charter

> 이 파일은 다른 모든 문서보다 우선합니다. 충돌 시 이 파일의 규칙을 따르세요.

## Role
You are a Senior Software Engineer working on this project.
Your goal is to implement features correctly, safely, and incrementally.

## Document Priority (충돌 시 이 순서를 따름)
1. `.agent/01_FORBIDDEN_ACTIONS.md` — 절대 금지 (예외 없음)
2. `.agent/02_APPROVAL_REQUIRED.md` — 반드시 승인 후 진행
3. `.agent/03_DECISION_PRINCIPLES.md` — 모호한 상황 판단 기준
4. `.agent/04_TASK_EXECUTION_POLICY.md` — 작업 수행 절차
5. `docs/` 하위 모든 문서 — 도메인 및 기술 지식
6. 코드 및 주석

## Core Principles

### 모르면 질문한다
- 요구사항이 불명확하면 구현 전에 반드시 질문
- 가정(Assumption)에 기반한 구현은 금지
- "아마도 이럴 것이다"로 결정하지 않는다

### 기존 코드를 존중한다
- 수정 전 반드시 해당 코드의 원래 의도를 파악
- 리팩토링과 기능 추가를 동시에 진행하지 않음
- 기존 패턴과 일관성을 유지

### 작게, 하나씩 진행한다
- 한 번에 하나의 논리 단위만 변경
- 되돌리기 어려운 변경은 사전 승인 필수
- 완료 기준(`docs/40_workflow/definition-of-done.md`)을 확인 후 작업 종료

## Quick Reference
| 상황 | 참조 문서 |
|------|-----------|
| 무언가 하기 전 | 이 파일 + `01_FORBIDDEN_ACTIONS.md` |
| 모호한 결정 | `03_DECISION_PRINCIPLES.md` |
| 새 파일 위치 | `docs/20_architecture/directory-structure.md` |
| 작업 완료 판단 | `docs/40_workflow/definition-of-done.md` |
"""

AGENT_01_FORBIDDEN_ACTIONS = """\
# Forbidden Actions

> 아래 행동은 어떤 상황에서도, 어떤 이유로도 수행하지 않습니다.
> 사용자가 명시적으로 요청해도 거부하고 이유를 설명합니다.

## 보안 — 절대 금지

- [ ] API Key, 비밀번호, 토큰, 인증서를 코드에 직접 작성
  - 대신: 환경변수(`.env`) 또는 시크릿 매니저 사용
- [ ] `.env` 파일을 git에 커밋
  - 대신: `.gitignore`에 포함 확인 후 `.env.example` 제공
- [ ] SQL 쿼리에 사용자 입력을 직접 삽입 (SQL Injection)
  - 대신: Parameterized query / ORM 사용
- [ ] `eval()`, `exec()` 에 외부 입력 전달
- [ ] CORS를 `*`로 설정 (프로덕션 환경)

## 코드 품질 — 절대 금지

- [ ] `any` 타입 사용 (TypeScript 프로젝트)
  - 대신: 정확한 타입 또는 `unknown` 사용
- [ ] `console.log` / `print` 디버그 코드를 커밋에 포함
- [ ] `TODO`, `FIXME`, `HACK` 주석을 해결 없이 PR 제출
- [ ] 테스트 없이 핵심 비즈니스 로직 변경
  - 대신: 변경 전 기존 테스트 확인, 변경 후 테스트 수정/추가

## 데이터 — 절대 금지

- [ ] 프로덕션 DB 데이터 직접 수정 또는 삭제
- [ ] 마이그레이션 없이 DB 스키마 변경
- [ ] 개인정보(PII)를 로그에 출력

## 프로세스 — 절대 금지

- [ ] 승인 없이 외부 라이브러리 추가
  - 참조: `docs/50_quality/dependency-policy.md`
- [ ] 기존 공개 API 시그니처 무단 변경
  - 대신: Deprecation 절차 또는 버전 관리 적용
- [ ] `git push --force` (공유 브랜치에서)
- [ ] CI 검증을 우회하는 커밋 (`--no-verify`)
"""

AGENT_02_APPROVAL_REQUIRED = """\
# Approval Required

> 아래 작업은 반드시 사용자에게 계획을 먼저 설명하고 승인을 받은 뒤 진행합니다.
> 승인 요청 시: 변경 내용, 영향 범위, 되돌리기 방법을 함께 설명합니다.

## 데이터 구조 변경

- DB 스키마 변경 (컬럼 추가/삭제/타입 변경)
- 마이그레이션 스크립트 실행
- 인덱스 생성/삭제

## 의존성 변경

- 새 외부 라이브러리 추가 (이유 + 대안 검토 결과 포함)
- 라이브러리 메이저 버전 업그레이드
- 라이브러리 제거

## 아키텍처 변경

- 폴더/모듈 구조 변경
- 새로운 서비스 또는 레이어 추가
- 기존 아키텍처 패턴 교체
- 새로운 외부 서비스 연동

## 환경 설정 변경

- 환경변수 추가/수정/삭제
- CI/CD 파이프라인 수정
- Docker/컨테이너 설정 변경
- 인프라 관련 설정 변경

## 대규모 코드 변경

- 50줄 이상의 기존 코드 수정
- 전체 파일 또는 모듈 재작성
- 여러 파일에 걸친 리팩토링

## 승인 요청 포맷
```
변경 내용: [무엇을 바꾸려 하는가]
변경 이유: [왜 필요한가]
영향 범위: [어떤 기능/모듈이 영향받는가]
롤백 방법: [문제 발생 시 어떻게 되돌리는가]
```
"""

AGENT_03_DECISION_PRINCIPLES = """\
# Decision Principles

> 모호하거나 충돌하는 상황에서 이 기준으로 판단합니다.

## 우선순위 체계

### 가치 우선순위 (충돌 시)
1. **보안** > 기능 > 성능 > 가독성 > 편의성
2. **명시된 규칙** > 관례 > 추론 > 추측
3. **가역적 선택** > 비가역적 선택

### 불확실할 때의 기본 원칙
- **최소 범위 원칙**: 필요한 최소한만 변경
- **명시적 원칙**: 암묵적 가정보다 명시적 질문
- **가역성 원칙**: 되돌리기 쉬운 방향 선택

## 코드 변경 판단

### "이 코드를 수정해야 하는가?"
```
기존 코드에 버그가 있는가?
  └─ Yes → 버그만 수정, 리팩토링 병행 금지
  └─ No  → 요청된 기능에 필요한 최소 변경만 수행
```

### "새 파일을 만들어야 하는가?"
```
기존 파일에 논리적으로 속하는가?
  └─ Yes → 기존 파일 수정
  └─ No  → docs/20_architecture/directory-structure.md 참조 후 생성
```

### "이 라이브러리를 추가해야 하는가?"
```
표준 라이브러리로 구현 가능한가?
  └─ Yes → 라이브러리 불필요
  └─ No  → docs/50_quality/dependency-policy.md 체크 후 승인 요청
```

## 코드 품질 판단

### 테스트 작성 기준
- 비즈니스 로직 변경 → 단위 테스트 필수
- API 엔드포인트 추가 → 통합 테스트 필수
- 버그 수정 → 재발 방지 테스트 추가
- 순수 UI 변경 → 테스트 선택적

### 에러 처리 기준
- 외부 API 호출 → 항상 예외 처리
- 사용자 입력 → 항상 유효성 검증
- 내부 함수 간 호출 → 전제조건(precondition) 명시
- 예상 불가능한 오류 → 로그 기록 후 상위로 전파

## 의사소통 판단

### 언제 질문하는가
- 요구사항이 두 가지 이상으로 해석될 때
- 기존 코드의 의도가 불분명할 때
- 02_APPROVAL_REQUIRED.md 해당 항목 발견 시
- 구현 방법이 여러 가지이고 트레이드오프가 있을 때

### 언제 바로 진행하는가
- 명확한 요구사항 + 단일 해석
- 기존 패턴이 명확히 존재
- 변경 범위가 작고 가역적
"""

AGENT_04_TASK_EXECUTION_POLICY = """\
# Task Execution Policy

> 모든 작업은 이 4단계 절차를 따릅니다.
> 단계를 건너뛰지 않습니다.

## 1단계: 분석 (Analyze) — 시작 전

### 체크리스트
- [ ] 요청의 의도와 범위를 정확히 파악했는가?
- [ ] 관련 파일/모듈을 모두 식별했는가?
- [ ] `docs/` 관련 문서를 참조했는가?
- [ ] `01_FORBIDDEN_ACTIONS.md` 해당 항목이 없는가?
- [ ] `02_APPROVAL_REQUIRED.md` 해당 항목이 없는가?

### 수행 내용
1. 관련 코드 읽기 (수정 전 전체 맥락 파악)
2. 영향 받는 파일 목록 작성
3. 기존 패턴과 관례 확인

## 2단계: 계획 (Plan) — 구현 전

### 체크리스트
- [ ] 변경 목록을 작성했는가?
- [ ] 각 변경의 이유를 설명할 수 있는가?
- [ ] 승인 필요 항목이 있다면 사용자에게 확인했는가?

### 수행 내용
1. 변경할 파일 목록 + 각 변경 내용 요약
2. 작업 순서 결정 (의존성 고려)
3. 승인 필요 시 `02_APPROVAL_REQUIRED.md` 포맷으로 요청

## 3단계: 구현 (Implement) — 실행

### 체크리스트
- [ ] 한 번에 하나의 논리 단위만 변경하고 있는가?
- [ ] 기존 코드 스타일을 따르고 있는가?
- [ ] 디버그 코드(`print`, `console.log`)를 남기지 않았는가?

### 수행 내용
1. 계획한 순서대로 파일 수정
2. 각 변경 후 즉시 영향 확인
3. 커밋 단위를 작게 유지 (하나의 논리 단위 = 하나의 커밋)

## 4단계: 검증 (Verify) — 완료 전

### 체크리스트 (Definition of Done)
- [ ] `docs/40_workflow/definition-of-done.md` 모든 항목 확인
- [ ] 테스트가 통과하는가?
- [ ] 새로 추가한 로직에 테스트가 있는가?
- [ ] 디버그 코드가 없는가?
- [ ] 타입 오류가 없는가?
- [ ] 보안 취약점이 없는가?

### 수행 내용
1. 테스트 실행 (`npm test` / `pytest` 등)
2. 변경 내용 요약 작성
3. 사용자에게 완료 보고 (변경 내용 + 테스트 결과 포함)

## 작업 단위 기준
- **작은 작업**: 파일 1-3개, 30줄 이하 변경 → 바로 진행
- **중간 작업**: 파일 4-10개, 30-100줄 변경 → 계획 공유 후 진행
- **큰 작업**: 파일 10개 이상 또는 100줄 이상 변경 → 승인 후 단계적 진행
"""

# ---------------------------------------------------------------------------
# docs/INDEX.md
# ---------------------------------------------------------------------------

DOCS_INDEX = """\
# Documentation Index

> Agent의 내비게이션 맵입니다. 무엇을 찾는지 모를 때 이 파일부터 시작하세요.

## 문서 우선순위
```
.agent/     최우선 (행동 제어)
docs/       도메인 지식 (이 파일 기준)
코드/주석   구현 세부사항
```

## 상황별 참조 가이드

| 상황 | 참조 문서 |
|------|-----------|
| 새 기능 구현 시작 | `10_product/scope.md` → `20_architecture/system-overview.md` |
| 새 파일 생성 위치 | `20_architecture/directory-structure.md` |
| 변수/함수 네이밍 | `30_engineering/coding-standards.md` |
| 에러 처리 방법 | `30_engineering/error-handling.md` |
| 보안 요구사항 | `30_engineering/security-guidelines.md` |
| 커밋/PR 작성 | `40_workflow/git-flow.md` + `40_workflow/pr-policy.md` |
| 완료 여부 판단 | `40_workflow/definition-of-done.md` |
| 새 라이브러리 추가 | `50_quality/dependency-policy.md` |
| 용어 확인 | `10_product/glossary.md` |
| 테스트 작성 기준 | `50_quality/test-strategy.md` |
| 기능 명세 작성 | `60_templates/feature-spec.md` |

## 문서 구조 개요

```
docs/
├── INDEX.md                  ← 지금 여기
├── 10_product/               제품이 무엇인지
│   ├── overview.md           비전, 목적, 타겟 유저
│   ├── scope.md              범위 안/밖 명시
│   ├── glossary.md           용어 사전 ★
│   ├── business-rules.md     핵심 비즈니스 규칙
│   └── success-metrics.md    성공 지표
├── 20_architecture/          어떻게 만들어졌는지
│   ├── system-overview.md    전체 구조
│   ├── directory-structure.md 파일 위치 규칙
│   ├── tech-stack.md         기술 스택 + 버전
│   ├── api-guidelines.md     API 설계 규약
│   └── data-model.md         데이터 모델
├── 30_engineering/           어떻게 코드를 작성하는지
│   ├── coding-standards.md   네이밍, 포맷팅
│   ├── error-handling.md     에러 처리 패턴
│   ├── security-guidelines.md 보안 요구사항
│   └── performance-guidelines.md 성능 기준
├── 40_workflow/              어떻게 협업하는지
│   ├── git-flow.md           브랜치 전략
│   ├── implementation-process.md 구현 절차
│   ├── pr-policy.md          PR 규칙
│   └── definition-of-done.md 완료 기준 ★
├── 50_quality/               품질을 어떻게 유지하는지
│   ├── test-strategy.md      테스트 전략
│   ├── review-checklist.md   리뷰 체크리스트
│   └── dependency-policy.md  의존성 관리
├── 60_templates/             재사용 문서
│   ├── feature-spec.md
│   ├── bug-report.md
│   └── pr-template.md
└── 70_governance/            문서 체계 운영
    ├── doc-priority-order.md
    ├── change-management.md
    └── CHANGELOG.md
```
"""

# ---------------------------------------------------------------------------
# docs/10_product/
# ---------------------------------------------------------------------------

DOCS_PRODUCT_OVERVIEW = """\
# Product Overview

> 이 문서를 업데이트하세요. 현재는 기본 템플릿입니다.

## What (무엇을 만드는가)
[제품/서비스 한 줄 설명]

## Why (왜 만드는가)
[해결하려는 문제]

## Who (누구를 위한가)

### Primary Users
- [주요 사용자 페르소나]

### Secondary Users
- [보조 사용자]

## Core Value Proposition
[제품의 핵심 가치 — 경쟁 제품과의 차별점]

## Key Metrics
- [핵심 지표 1]
- [핵심 지표 2]

## Current Status
- Phase: [개발 단계]
- Launch Target: [목표 일정]
"""

DOCS_PRODUCT_GLOSSARY = """\
# Glossary — 도메인 용어 사전

> ★ 이 파일은 프로젝트의 모든 용어 사용 기준입니다.
> 용어가 불명확하면 코드, 문서, 커뮤니케이션이 모두 어긋납니다.
> 새 용어 사용 전 이 파일에 추가하세요.

## 사용 규칙
- 코드(변수명, 함수명, 클래스명)에서도 이 용어를 그대로 사용
- 유사어가 있다면 **공식 용어**를 지정하고 동의어는 비고란에 기록
- 영문/한국어 혼용 기준도 명시

## 핵심 도메인 용어

| 용어 (코드) | 한국어 | 정의 | 동의어 (사용 금지) |
|-------------|--------|------|--------------------|
| `User` | 사용자 | 서비스에 가입한 계정 | Member, Account |
| `Admin` | 관리자 | 시스템 관리 권한을 가진 사용자 | Manager, Operator |
| [추가] | | | |

## 상태(Status) 값 표준

| 상태 | 코드 값 | 의미 |
|------|---------|------|
| 활성 | `active` | 정상 사용 가능 |
| 비활성 | `inactive` | 일시 중지 |
| 삭제됨 | `deleted` | 소프트 삭제 |
| [추가] | | |

## 약어 정의

| 약어 | 원문 | 의미 |
|------|------|------|
| [추가] | | |

## 네이밍 규칙 요약
- 파일명: `kebab-case` (예: `user-service.ts`)
- 변수/함수: `camelCase` (예: `getUserById`)
- 클래스/타입: `PascalCase` (예: `UserRepository`)
- 상수: `UPPER_SNAKE_CASE` (예: `MAX_RETRY_COUNT`)
- DB 컬럼: `snake_case` (예: `created_at`)
"""

DOCS_PRODUCT_SCOPE = """\
# Product Scope

## In-Scope (이 프로젝트에서 다루는 것)

### 현재 버전 (v1.0)
- [ ] [기능 1]
- [ ] [기능 2]

### 다음 버전 계획
- [ ] [기능 3]

## Out-of-Scope (이 프로젝트에서 다루지 않는 것)

> 명시적으로 제외된 항목입니다. 구현 요청 시 Scope 변경 논의가 필요합니다.

- [제외 이유와 함께 명시]
- [예: "결제 기능 — 외부 서비스(Stripe) 사용, 자체 구현 불필요"]

## 경계 조건 (Boundary Conditions)

| 항목 | 기준 | 처리 방법 |
|------|------|-----------|
| [예: 파일 업로드 크기] | [예: 최대 10MB] | [예: 클라이언트에서 차단] |
"""

DOCS_PRODUCT_BUSINESS_RULES = """\
# Business Rules

> 비즈니스 로직 구현 시 반드시 참조하세요.
> 규칙 변경은 `docs/70_governance/change-management.md` 절차를 따릅니다.

## 핵심 규칙

### [규칙 그룹 1 — 예: 사용자 관리]
- 이메일은 전체 시스템에서 유일해야 한다
- 비밀번호는 최소 8자, 영문+숫자+특수문자 조합

### [규칙 그룹 2 — 예: 권한]
- 관리자만 다른 사용자를 삭제할 수 있다
- 일반 사용자는 자신의 데이터만 수정 가능

## 계산 규칙

| 항목 | 공식/기준 | 예시 |
|------|-----------|------|
| [항목] | [공식] | [예시] |

## 예외 처리 규칙

| 상황 | 처리 방법 |
|------|-----------|
| [상황] | [처리 방법] |
"""

DOCS_PRODUCT_SUCCESS_METRICS = """\
# Success Metrics

## North Star Metric
[가장 중요한 단일 지표]

## Key Performance Indicators (KPIs)

| 지표 | 현재 | 목표 | 측정 방법 |
|------|------|------|-----------|
| [지표 이름] | [현재 값] | [목표 값] | [측정 방법] |

## Health Metrics (시스템 상태)

| 지표 | 기준 | 알림 임계값 |
|------|------|-------------|
| API 응답 시간 (P95) | < 500ms | > 1000ms |
| 오류율 | < 1% | > 5% |
| 업타임 | > 99.9% | < 99% |
"""

# ---------------------------------------------------------------------------
# docs/20_architecture/
# ---------------------------------------------------------------------------

DOCS_ARCH_SYSTEM_OVERVIEW = """\
# System Overview

## 전체 구조 다이어그램
```
[클라이언트] ←→ [API Gateway / BFF] ←→ [백엔드 서비스]
                                              ↕
                                         [데이터베이스]
                                              ↕
                                         [외부 서비스]
```

## 서비스 경계

| 서비스 | 역할 | 기술 | 포트 |
|--------|------|------|------|
| Frontend | UI 렌더링 | [기술] | [포트] |
| Backend | 비즈니스 로직 | [기술] | [포트] |
| Database | 데이터 영속성 | [기술] | [포트] |

## 주요 데이터 흐름

### [플로우 1 — 예: 사용자 인증]
```
1. 클라이언트 → POST /auth/login
2. 백엔드 → DB에서 사용자 조회
3. 비밀번호 검증 → JWT 발급
4. 클라이언트 ← JWT 토큰
```

## 외부 의존성

| 서비스 | 용도 | 장애 시 동작 |
|--------|------|--------------|
| [서비스 이름] | [용도] | [Fallback 동작] |

## 알려진 기술 부채
- [부채 항목 + 해결 계획]
"""

DOCS_ARCH_DIRECTORY_STRUCTURE = """\
# Directory Structure

> 새 파일을 만들기 전에 이 문서를 참조하세요.
> 규칙에 맞지 않는 위치에 파일을 생성하기 전 승인을 받으세요.

## 루트 구조
```
project-root/
├── .agent/          Agent 제어 문서 (수정 신중히)
├── .claude/         Claude Code 하네스 설정
├── docs/            프로젝트 문서
├── src/             소스 코드
├── tests/           테스트 코드
├── scripts/         유틸리티 스크립트
├── .env.example     환경변수 예시 (실제 .env는 git 제외)
└── CLAUDE.md        Claude Code 진입점
```

## 소스 코드 구조 (`src/`)
```
src/
├── [도메인 기준 폴더 구조를 여기에 정의]
```

## 파일 생성 위치 규칙

| 파일 유형 | 위치 | 예시 |
|-----------|------|------|
| 비즈니스 로직 | `src/[domain]/` | `src/user/user-service.ts` |
| API 핸들러 | `src/[domain]/` | `src/user/user-controller.ts` |
| 타입/인터페이스 | `src/types/` 또는 도메인 내 | `src/user/user.types.ts` |
| 유틸리티 | `src/utils/` | `src/utils/date.ts` |
| 테스트 | `tests/` 또는 `*.test.ts` 같은 위치 | `src/user/user-service.test.ts` |
| 환경 설정 | 루트 | `.env`, `vite.config.ts` |

## 금지 패턴
- `src/` 루트에 직접 파일 생성 (서브디렉토리 필수)
- `tests/` 외부에 `test_*` 파일 생성 (단, `*.test.ts` 패턴은 허용)
"""

DOCS_ARCH_TECH_STACK = """\
# Tech Stack

> 정확한 버전을 기재합니다. 버전 변경은 `02_APPROVAL_REQUIRED.md` 항목입니다.

## 언어 & 런타임

| 항목 | 버전 | 비고 |
|------|------|------|
| [언어] | [버전] | |
| [런타임] | [버전] | |

## 프레임워크 & 라이브러리

### Frontend
| 패키지 | 버전 | 용도 |
|--------|------|------|
| [패키지] | [버전] | [용도] |

### Backend
| 패키지 | 버전 | 용도 |
|--------|------|------|
| [패키지] | [버전] | [용도] |

## 인프라 & 도구

| 도구 | 버전 | 용도 |
|------|------|------|
| [도구] | [버전] | [용도] |

## 개발 도구

| 도구 | 버전 | 용도 |
|------|------|------|
| [도구] | [버전] | [용도] |

## 버전 관리 정책
- Node.js: `.nvmrc` 또는 `.node-version` 파일로 고정
- Python: `.python-version` 파일로 고정
- 의존성: `package-lock.json` / `poetry.lock` git에 포함
"""

DOCS_ARCH_API_GUIDELINES = """\
# API Guidelines

## 기본 원칙
- RESTful 설계 원칙 준수
- 모든 응답은 일관된 형식 사용
- 에러 코드는 HTTP 표준 준수

## URL 설계 규칙

### 리소스 네이밍
```
✅ /api/users           (복수형 명사)
✅ /api/users/{id}
✅ /api/users/{id}/posts
❌ /api/getUser
❌ /api/user_list
```

### HTTP 메서드
| 메서드 | 용도 | 예시 |
|--------|------|------|
| GET | 조회 (멱등성 보장) | `GET /api/users` |
| POST | 생성 | `POST /api/users` |
| PUT | 전체 수정 | `PUT /api/users/{id}` |
| PATCH | 부분 수정 | `PATCH /api/users/{id}` |
| DELETE | 삭제 | `DELETE /api/users/{id}` |

## 응답 형식

### 성공 응답
```json
{
  "data": { ... },
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### 에러 응답
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "사용자에게 표시할 메시지",
    "details": [
      { "field": "email", "message": "유효하지 않은 이메일 형식" }
    ]
  }
}
```

## 버전 관리
- URL 경로 버전: `/api/v1/users`
- 하위 호환성이 깨지는 변경 → 새 버전
- 기존 버전은 최소 6개월 유지

## 인증
- Bearer Token (JWT): `Authorization: Bearer {token}`
- 토큰 만료: [기준 설정]
- Refresh Token 정책: [기준 설정]

## 페이지네이션
```
GET /api/users?page=1&per_page=20&sort=created_at&order=desc
```
"""

DOCS_ARCH_DATA_MODEL = """\
# Data Model

## 엔티티 관계도
```
[ERD 또는 텍스트 다이어그램]
```

## 핵심 테이블

### users
| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID/BIGINT | PK | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | |
| created_at | TIMESTAMP | NOT NULL | |
| updated_at | TIMESTAMP | NOT NULL | |

### [다른 테이블]

## 소프트 삭제 정책
- `deleted_at` 컬럼 사용 (NULL = 활성)
- 물리 삭제는 별도 승인 필요

## 인덱스 전략
- 자주 조회되는 컬럼: 인덱스 추가
- 복합 인덱스: 쿼리 패턴 기반 설계
- 인덱스 추가/삭제: `02_APPROVAL_REQUIRED.md` 항목
"""

# ---------------------------------------------------------------------------
# docs/30_engineering/
# ---------------------------------------------------------------------------

DOCS_ENG_CODING_STANDARDS = """\
# Coding Standards

> 코드 스타일 자동화 도구 설정이 이 문서보다 우선합니다.
> 이 문서는 도구로 잡을 수 없는 설계 규칙을 다룹니다.

## 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수/함수 | `camelCase` | `getUserById`, `isActive` |
| 클래스/타입/인터페이스 | `PascalCase` | `UserService`, `ApiResponse` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 파일명 | `kebab-case` | `user-service.ts` |
| DB 컬럼 | `snake_case` | `created_at` |
| CSS 클래스 | `kebab-case` | `user-profile-card` |

## 함수 설계 원칙
- 함수 하나 = 하나의 역할 (Single Responsibility)
- 매개변수 최대 3개 (초과 시 객체로 묶음)
- 함수 길이 최대 30줄 (초과 시 분리 검토)
- 부작용(Side Effect)이 있는 함수는 이름에 반영 (`saveUser`, `sendEmail`)

## 주석 규칙
```
✅ "왜(Why)" 설명 — 비즈니스 이유, 우회 이유
✅ 복잡한 알고리즘 설명
❌ 코드를 그대로 번역하는 주석
❌ 자동완성 가능한 내용

// ✅ 좋은 예
// 레거시 API 호환성을 위해 camelCase 대신 snake_case 사용
const user_id = params.userId;

// ❌ 나쁜 예
// 사용자 ID를 가져옴
const userId = params.userId;
```

## 상수 관리
- 매직 넘버 금지: 의미있는 이름의 상수로 정의
- 설정값: 환경변수 또는 설정 파일로 분리
```
❌ if (retryCount > 3)
✅ if (retryCount > MAX_RETRY_COUNT)
```

## 불변성 원칙
- 변수는 기본적으로 `const` (재할당 필요 시만 `let`)
- 객체/배열 직접 수정 대신 복사 후 수정
- 함수 파라미터 수정 금지

## 에러 처리
→ `30_engineering/error-handling.md` 참조

## 포맷팅
- 린터/포매터 설정 파일(`.eslintrc`, `.prettierrc`, `pyproject.toml`)이 최우선
- 탭 vs 스페이스: 설정 파일 기준
- 줄 길이: 최대 100자
"""

DOCS_ENG_ERROR_HANDLING = """\
# Error Handling

## 에러 계층 구조

### 에러 유형 분류
| 유형 | 원인 | 처리 방법 |
|------|------|-----------|
| 유효성 오류 | 잘못된 사용자 입력 | 400 Bad Request + 상세 메시지 |
| 인증 오류 | 미인증/만료 | 401 Unauthorized |
| 권한 오류 | 접근 권한 없음 | 403 Forbidden |
| 리소스 없음 | 존재하지 않는 데이터 | 404 Not Found |
| 충돌 | 중복/상태 충돌 | 409 Conflict |
| 서버 오류 | 예상치 못한 오류 | 500 Internal Server Error |

## 에러 처리 원칙

### 외부 경계에서만 try-catch
```
✅ API 핸들러 (외부 입력 진입점)
✅ 외부 서비스 호출 (DB, API, 파일시스템)
❌ 내부 비즈니스 로직 (전제조건이 맞으면 예외 없음)
```

### 에러 전파 규칙
1. 복구 가능한 오류 → 현재 레이어에서 처리
2. 복구 불가능한 오류 → 상위 레이어로 전파
3. 외부 서비스 오류 → 래핑하여 내부 에러 타입으로 변환

### 로깅 기준
```
ERROR  — 즉시 대응 필요 (서비스 장애, 데이터 손실 위험)
WARN   — 주의 필요 (재시도 성공, 성능 저하)
INFO   — 정상 운영 흐름 기록 (요청 시작/종료)
DEBUG  — 개발/디버깅용 (프로덕션 비활성화)
```

### 로그에 포함할 것 / 금지할 것
```
✅ 포함: request_id, user_id(마스킹), timestamp, error_code, stack_trace
❌ 금지: 비밀번호, API Key, 개인정보(이메일, 전화번호)
```

## 패턴 예시

### Result 타입 패턴 (TypeScript)
```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };
```

### 재시도 정책
- 네트워크 오류: 최대 3회, 지수 백오프 (1s, 2s, 4s)
- DB 연결 오류: 최대 5회, 고정 간격 (500ms)
- 비즈니스 로직 오류: 재시도 없음
"""

DOCS_ENG_SECURITY_GUIDELINES = """\
# Security Guidelines

> 보안 요구사항은 기능보다 우선합니다. (`.agent/03_DECISION_PRINCIPLES.md` 참조)

## 필수 보안 규칙

### 인증 & 인가
- [ ] 모든 API 엔드포인트에 인증 확인 (public 엔드포인트만 예외, 명시 필요)
- [ ] 권한 확인은 서버에서만 수행 (클라이언트 검증 신뢰 금지)
- [ ] JWT는 짧은 만료시간 + Refresh Token 패턴 사용
- [ ] 세션/토큰은 HttpOnly, Secure 쿠키 또는 메모리 저장

### 입력 검증
- [ ] 모든 외부 입력 유효성 검증 (API 파라미터, 폼 입력, 파일 업로드)
- [ ] SQL Injection 방지: ORM 또는 Parameterized Query 사용
- [ ] XSS 방지: 사용자 입력 출력 시 이스케이프
- [ ] 파일 업로드: 타입 + 크기 검증, 실행 권한 없는 디렉토리에 저장

### 시크릿 관리
- [ ] API Key, 비밀번호, 토큰은 환경변수로만 관리
- [ ] `.env` 파일은 `.gitignore`에 포함
- [ ] 로그에 시크릿 절대 출력 금지
- [ ] 시크릿 로테이션 계획 수립

### 의존성 보안
- [ ] `npm audit` / `pip-audit` 정기 실행
- [ ] 알려진 취약점(CVE) 있는 패키지 즉시 업데이트
- [ ] Lock 파일(`package-lock.json`, `poetry.lock`) git에 포함

## OWASP Top 10 대응

| 취약점 | 대응 방법 |
|--------|-----------|
| SQL Injection | ORM 사용, Parameterized Query |
| XSS | 출력 시 이스케이프, CSP 헤더 |
| IDOR | 모든 리소스 접근에 소유권 확인 |
| 민감 데이터 노출 | TLS 강제, 로그 마스킹 |
| 인증 취약점 | 강한 비밀번호 정책, Rate Limiting |

## 보안 사고 대응
보안 취약점 발견 시:
1. 즉시 사용자에게 보고
2. 임시 완화 조치 논의
3. 영구 수정 계획 수립
4. 사고 기록 (`docs/70_governance/CHANGELOG.md`)
"""

DOCS_ENG_PERFORMANCE_GUIDELINES = """\
# Performance Guidelines

## 성능 목표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| API 응답 시간 (P95) | < 500ms | APM 도구 |
| 페이지 초기 로드 | < 3s (LCP) | Lighthouse |
| DB 쿼리 시간 | < 100ms | 쿼리 로그 |

## 안티패턴 — 금지

### N+1 쿼리
```
❌ 루프 안에서 DB 쿼리
✅ JOIN 또는 IN 절로 한 번에 조회
```

### 불필요한 데이터 로드
```
❌ SELECT * (모든 컬럼 조회)
✅ 필요한 컬럼만 명시
```

### 동기 블로킹
```
❌ 긴 동기 작업을 메인 스레드에서 실행
✅ 비동기 처리 또는 백그라운드 작업 큐 사용
```

## 최적화 가이드

### 캐싱
- DB 조회가 빈번하고 변경이 적은 데이터: 캐시 적용
- 캐시 무효화 전략 명시 (TTL 또는 Event-driven)
- 캐시 히트율 모니터링

### 인덱스
- 자주 사용되는 WHERE, ORDER BY 컬럼에 인덱스
- 복합 인덱스: 조건 순서 고려
- 인덱스 추가는 `02_APPROVAL_REQUIRED.md` 항목

### 페이지네이션
- 목록 API는 반드시 페이지네이션 구현
- Offset 기반: 작은 데이터셋
- Cursor 기반: 대용량 데이터셋

## 성능 테스트
- 새 기능 배포 전: 부하 테스트 실행
- 응답 시간 목표 미달 시: 배포 차단
"""

# ---------------------------------------------------------------------------
# docs/40_workflow/
# ---------------------------------------------------------------------------

DOCS_WORKFLOW_GIT_FLOW = """\
# Git Flow

## 브랜치 전략

```
main          프로덕션 배포 브랜치 (직접 커밋 금지)
  └─ develop  통합 개발 브랜치
       ├─ feature/[ticket-id]-[description]   새 기능
       ├─ bugfix/[ticket-id]-[description]    버그 수정
       ├─ hotfix/[ticket-id]-[description]    긴급 수정 (main에서 분기)
       └─ chore/[description]                 설정, 문서, 리팩토링
```

## 브랜치 규칙
- `main`, `develop` 직접 커밋 금지 — PR만 허용
- 브랜치명은 소문자 + kebab-case
- 작업 완료 후 브랜치 삭제

## 커밋 메시지 규약

### 형식
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type 목록
| Type | 용도 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서만 변경 |
| `style` | 포맷팅 (기능 변경 없음) |
| `refactor` | 리팩토링 (기능/버그 변경 없음) |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 변경 |
| `perf` | 성능 개선 |

### 예시
```
✅ feat(auth): JWT 토큰 갱신 기능 추가
✅ fix(user): 이메일 중복 검증 누락 수정
✅ docs(api): 사용자 API 엔드포인트 문서 업데이트
❌ update code
❌ fix bug
❌ WIP
```

## 병합 전략
- `feature` → `develop`: Squash & Merge (커밋 히스토리 정리)
- `develop` → `main`: Merge Commit (릴리즈 추적)
- `hotfix` → `main` + `develop`: Cherry-pick
"""

DOCS_WORKFLOW_IMPLEMENTATION_PROCESS = """\
# Implementation Process

> `.agent/04_TASK_EXECUTION_POLICY.md`와 함께 읽으세요.
> 이 문서는 팀 협업 관점의 구현 절차를 다룹니다.

## 작업 시작 전

1. **티켓 확인**: 요구사항, 인수 조건(Acceptance Criteria), 우선순위 확인
2. **의존성 확인**: 다른 작업의 완료를 기다려야 하는지 확인
3. **브랜치 생성**: `feature/[ticket-id]-[description]` 형식
4. **범위 확인**: `docs/10_product/scope.md` 참조

## 구현 중

1. **작은 단위 커밋**: 논리적 단위로 자주 커밋
2. **테스트 병행**: 구현과 테스트를 함께 작성
3. **진행 상황 공유**: 예상보다 오래 걸릴 경우 즉시 공유

## 작업 완료 시

1. **Definition of Done 확인**: `docs/40_workflow/definition-of-done.md`
2. **셀프 리뷰**: PR 올리기 전 본인이 먼저 검토
3. **PR 생성**: `docs/60_templates/pr-template.md` 형식 사용
4. **리뷰 요청**: 적절한 리뷰어 지정

## 작업 단위 기준

| 크기 | 기준 | 처리 방법 |
|------|------|-----------|
| Small | 파일 1-3개, ~30줄 | 바로 진행 |
| Medium | 파일 4-10개, 30-100줄 | 계획 공유 후 진행 |
| Large | 10개+ 파일 또는 100줄+ | 단계 분리 + 단계별 PR |
"""

DOCS_WORKFLOW_PR_POLICY = """\
# Pull Request Policy

## PR 단위 원칙
- 하나의 PR = 하나의 목적 (기능 추가 + 리팩토링 혼재 금지)
- PR 크기: 리뷰어가 30분 내 리뷰 가능한 수준
- 목표: 파일 10개 이하, 변경 줄 200줄 이하

## PR 생성 규칙

### 제목 형식
```
[type] 간결한 변경 내용 요약
예: [feat] 사용자 프로필 이미지 업로드 기능
예: [fix] 로그인 시 이메일 대소문자 구분 오류 수정
```

### 본문 (템플릿: `docs/60_templates/pr-template.md`)
- 변경 내용 요약
- 테스트 방법
- 스크린샷 (UI 변경 시)
- 체크리스트

## 리뷰 프로세스
- 승인 필요 인원: 최소 1명
- 리뷰어는 24시간 내 응답
- 모든 Comment 해결 후 병합
- CI 통과 필수

## 병합 전 체크리스트
- [ ] CI 모든 검사 통과
- [ ] 리뷰어 승인 완료
- [ ] 모든 리뷰 코멘트 해결
- [ ] `definition-of-done.md` 확인
- [ ] 충돌 해결 완료

## Draft PR 활용
- 작업 중 피드백이 필요할 때 Draft PR 활용
- WIP 커밋 금지 — Draft PR로 대체
"""

DOCS_WORKFLOW_DEFINITION_OF_DONE = """\
# Definition of Done (DoD)

> 이 체크리스트의 모든 항목이 완료되어야 작업이 완료된 것입니다.
> 하나라도 미완료 시 작업을 완료로 간주하지 않습니다.

## 필수 항목 (모든 작업)

### 코드 품질
- [ ] 린터 오류 없음
- [ ] 타입 오류 없음 (TypeScript)
- [ ] 디버그 코드 없음 (`console.log`, `print`, `debugger`)
- [ ] 하드코딩된 값 없음 (상수 또는 환경변수 사용)

### 테스트
- [ ] 기존 테스트 모두 통과
- [ ] 새로 추가한 비즈니스 로직에 테스트 추가
- [ ] 버그 수정 시 재발 방지 테스트 추가

### 보안
- [ ] 시크릿이 코드에 없음
- [ ] 사용자 입력 유효성 검증 완료
- [ ] 권한 확인 로직 포함

### 문서
- [ ] 공개 API 변경 시 API 문서 업데이트
- [ ] 복잡한 로직에 설명 주석 추가

## 추가 항목 (해당 시)

### UI 변경
- [ ] 모바일/태블릿 레이아웃 확인
- [ ] 접근성(a11y) 기본 요구사항 충족

### DB 변경
- [ ] 마이그레이션 스크립트 작성
- [ ] 롤백 스크립트 또는 방법 확인

### 외부 서비스 연동
- [ ] 타임아웃 및 에러 처리 구현
- [ ] 연동 실패 시 Fallback 동작 확인

## 완료 보고 형식
```
완료한 작업: [작업 내용]
변경 파일: [파일 목록]
테스트: [테스트 실행 결과]
특이사항: [있다면 기재]
```
"""

# ---------------------------------------------------------------------------
# docs/50_quality/
# ---------------------------------------------------------------------------

DOCS_QUALITY_TEST_STRATEGY = """\
# Test Strategy

## 테스트 피라미드

```
        /\\
       /E2E\\         소수 (핵심 사용자 플로우)
      /------\\
     /통합 테스트\\    중간 (서비스 간 통합)
    /------------\\
   /  단위 테스트  \\  다수 (함수/클래스 단위)
  /--------------\\
```

## 테스트 유형별 기준

### 단위 테스트 (Unit Tests)
- **대상**: 비즈니스 로직 함수, 유틸리티 함수
- **필수 작성**: 로직 변경 시
- **목표 커버리지**: 비즈니스 로직 80% 이상
- **원칙**: 빠르고 독립적 (외부 의존성 모킹)

### 통합 테스트 (Integration Tests)
- **대상**: API 엔드포인트, DB 연동
- **필수 작성**: 새 API 추가 시
- **원칙**: 실제 DB 사용 (모킹 금지 — 실제 동작 검증)

### E2E 테스트
- **대상**: 핵심 사용자 플로우 (로그인, 주요 기능)
- **범위 최소화**: 중요한 플로우만

## 테스트 파일 구조
```
describe('[모듈명]', () => {
  describe('[함수/메서드명]', () => {
    it('[정상 케이스 설명]', () => { ... })
    it('[엣지 케이스 설명]', () => { ... })
    it('[에러 케이스 설명]', () => { ... })
  })
})
```

## 테스트 커버리지 기준
| 레이어 | 최소 커버리지 |
|--------|--------------|
| 비즈니스 로직 | 80% |
| API 핸들러 | 70% |
| 유틸리티 | 90% |
| UI 컴포넌트 | 선택적 |

## CI 테스트 정책
- PR 병합 전 모든 테스트 통과 필수
- 테스트 실패 시 배포 차단
- Flaky 테스트는 즉시 수정 또는 격리
"""

DOCS_QUALITY_REVIEW_CHECKLIST = """\
# Code Review Checklist

## 리뷰어 체크리스트

### 기능 & 로직
- [ ] 요구사항/인수 조건을 충족하는가?
- [ ] 엣지 케이스가 처리되었는가?
- [ ] 기존 기능에 영향을 주지 않는가?

### 코드 품질
- [ ] `coding-standards.md` 규칙을 따르는가?
- [ ] 함수/변수명이 의도를 명확히 표현하는가?
- [ ] 중복 코드가 없는가?
- [ ] 불필요한 복잡성이 없는가?

### 보안
- [ ] `security-guidelines.md` 항목을 위반하지 않는가?
- [ ] 사용자 입력 검증이 있는가?
- [ ] 시크릿이 코드에 없는가?

### 테스트
- [ ] 핵심 로직에 테스트가 있는가?
- [ ] 테스트가 실제로 의미있는 검증을 하는가?
- [ ] 테스트 이름이 무엇을 검증하는지 명확한가?

### 문서 & 주석
- [ ] 복잡한 로직에 설명이 있는가?
- [ ] API 변경 시 문서가 업데이트되었는가?

## 리뷰 코멘트 레벨
| 레벨 | 의미 | 예시 |
|------|------|------|
| `[blocking]` | 반드시 수정 | 보안 취약점, 버그 |
| `[suggestion]` | 수정 권장 | 코드 품질 개선 |
| `[question]` | 이해를 위한 질문 | 의도 파악 |
| `[nit]` | 사소한 개선 | 네이밍 등 |

## PR 작성자 체크리스트
- [ ] 셀프 리뷰 완료
- [ ] `definition-of-done.md` 확인
- [ ] PR 설명이 충분한가?
"""

DOCS_QUALITY_DEPENDENCY_POLICY = """\
# Dependency Policy

## 새 라이브러리 추가 전 체크리스트

### 필요성 검증
- [ ] 표준 라이브러리로 구현 불가능한가?
- [ ] 기존 설치된 라이브러리로 해결 불가능한가?
- [ ] 라이브러리 없이 직접 구현 시 비용이 더 크가?

### 라이브러리 품질 기준
- [ ] 주간 다운로드 10,000+ (npm/PyPI 기준)
- [ ] 최근 6개월 내 업데이트 이력
- [ ] GitHub Stars 1,000+ (가이드라인, 절대적 기준 아님)
- [ ] MIT, Apache 2.0, BSD 등 허용 라이선스
- [ ] 알려진 보안 취약점(CVE) 없음

### 승인 프로세스
1. 필요성 + 대안 검토 결과 작성
2. `02_APPROVAL_REQUIRED.md` 형식으로 승인 요청
3. 승인 후 `docs/20_architecture/tech-stack.md` 업데이트

## 라이브러리 제거 정책
- 사용하지 않는 라이브러리는 즉시 제거
- 제거 전 의존 코드 전체 확인
- 제거도 `02_APPROVAL_REQUIRED.md` 항목

## 버전 관리
- 버전 고정: `^` 또는 `~` 사용 시 의도 명시
- 메이저 버전 업그레이드: 반드시 CHANGELOG 확인
- 보안 취약점 패치: 즉시 업데이트
"""

# ---------------------------------------------------------------------------
# docs/60_templates/
# ---------------------------------------------------------------------------

DOCS_TEMPLATE_FEATURE_SPEC = """\
# Feature Spec Template

> 이 템플릿을 복사하여 새 기능 명세서를 작성하세요.
> 파일명: `docs/60_templates/specs/[feature-name].md`

---

# [기능 이름]

## 개요
[기능의 목적과 해결하는 문제를 2-3문장으로]

## 배경
- **요청자**: [누가 요청했는가]
- **우선순위**: [High / Medium / Low]
- **관련 티켓**: [#ticket-id]

## 사용자 스토리
```
As a [사용자 유형],
I want to [원하는 것],
So that [얻는 가치].
```

## 인수 조건 (Acceptance Criteria)
- [ ] Given [전제 조건], When [동작], Then [결과]
- [ ] [추가 인수 조건]

## 범위 (Scope)

### In-Scope
- [포함되는 것]

### Out-of-Scope
- [포함되지 않는 것]

## 기술 구현 노트
[구현 방향, 주의사항, 참조 문서]

## 테스트 시나리오
| 시나리오 | 기대 결과 |
|----------|-----------|
| [시나리오] | [결과] |

## 완료 기준
`docs/40_workflow/definition-of-done.md` + 위 인수 조건 모두 충족
"""

DOCS_TEMPLATE_BUG_REPORT = """\
# Bug Report Template

---

# Bug: [버그 제목]

## 심각도
- [ ] Critical (서비스 중단)
- [ ] High (주요 기능 불가)
- [ ] Medium (기능 저하)
- [ ] Low (사소한 이슈)

## 환경
- 운영 환경: [Production / Staging / Development]
- 버전/커밋: [버전 또는 커밋 해시]
- OS/브라우저: [해당 시]

## 재현 방법
1. [첫 번째 단계]
2. [두 번째 단계]
3. [결과 확인]

## 예상 동작
[어떻게 동작해야 하는가]

## 실제 동작
[실제로 어떻게 동작했는가]

## 스크린샷 / 로그
[첨부]

## 원인 분석 (알고 있다면)
[원인]

## 관련 코드/파일
[파일명:라인번호]
"""

DOCS_TEMPLATE_PR_TEMPLATE = """\
# PR Template

---

## 변경 유형
- [ ] 새 기능 (feat)
- [ ] 버그 수정 (fix)
- [ ] 리팩토링
- [ ] 문서
- [ ] 기타

## 변경 내용
[무엇을 왜 변경했는가 — 2-5줄]

## 관련 티켓
Closes #[ticket-id]

## 테스트 방법
[리뷰어가 직접 테스트하는 방법]

## 스크린샷 (UI 변경 시)
[Before / After]

## 체크리스트
- [ ] `definition-of-done.md` 확인
- [ ] 테스트 통과
- [ ] 셀프 리뷰 완료
- [ ] 문서 업데이트 (해당 시)
- [ ] `02_APPROVAL_REQUIRED.md` 항목 승인 완료 (해당 시)
"""

# ---------------------------------------------------------------------------
# docs/70_governance/
# ---------------------------------------------------------------------------

DOCS_GOVERNANCE_DOC_PRIORITY = """\
# Document Priority Order

## 충돌 해결 우선순위

1. `.agent/01_FORBIDDEN_ACTIONS.md` — 절대 금지 (예외 없음)
2. `.agent/02_APPROVAL_REQUIRED.md` — 승인 필요
3. `.agent/03_DECISION_PRINCIPLES.md` — 판단 기준
4. `.agent/04_TASK_EXECUTION_POLICY.md` — 실행 절차
5. `.agent/00_CHARTER.md` — 역할 및 원칙
6. `docs/30_engineering/security-guidelines.md` — 보안 (기능보다 우선)
7. `docs/20_architecture/` — 구조적 제약
8. `docs/30_engineering/` — 코드 품질 기준
9. `docs/40_workflow/` — 프로세스
10. `docs/10_product/` — 도메인 지식
11. `docs/50_quality/` ~ `docs/70_governance/` — 품질 및 운영

## 충돌 발생 시 처리
1. 우선순위가 높은 문서의 규칙을 따름
2. 판단 불가 시 사용자에게 질문
3. 충돌 해결 결과를 문서에 반영 (change-management 절차)
"""

DOCS_GOVERNANCE_CHANGE_MANAGEMENT = """\
# Change Management

> 하네스 문서(`.agent/`, `docs/`) 변경 절차입니다.
> 규칙 변경은 코드 변경과 동일한 무게로 다룹니다.

## 변경이 필요한 경우
- 프로젝트 요구사항 변경
- 기존 규칙의 모순/불명확성 발견
- 새로운 기술 도입
- 팀 규칙 합의 변경

## 변경 절차

### 1. 변경 제안
- 변경할 문서, 변경 내용, 이유를 작성
- 영향받는 다른 문서 확인

### 2. 리뷰
- `.agent/` 문서: 팀 전체 합의 필요
- `docs/` 문서: 관련 담당자 승인

### 3. 적용
- 변경 내용 반영
- `CHANGELOG.md` 업데이트
- 팀에 변경 공지

## CHANGELOG 업데이트 형식
```
## [날짜] — [변경 유형]
**변경 파일**: [파일 경로]
**변경 내용**: [무엇이 바뀌었는가]
**변경 이유**: [왜 바뀌었는가]
**영향**: [이 변경으로 달라지는 Agent 동작]
```
"""

DOCS_GOVERNANCE_CHANGELOG = """\
# Rules Changelog

> 이 파일은 하네스 규칙 변경 이력을 기록합니다.
> Agent가 최신 규칙을 참조하도록 중요한 변경사항을 반드시 기록하세요.

## 형식
```
## [YYYY-MM-DD] — [Added|Changed|Removed|Fixed]
변경 파일: [경로]
내용: [변경 내용]
이유: [변경 이유]
```

---

## [초기 생성]
**내용**: 기본 하네스 템플릿으로 초기 생성
**이유**: 프로젝트 AI Agent 행동 제어 문서 설정
"""

# ---------------------------------------------------------------------------
# .claude/settings.json — Sensor (Feedback Controls)
# ---------------------------------------------------------------------------

CLAUDE_SETTINGS_JSON = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash|Edit|Write",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/guard-secrets.sh",
                        "description": "하드코딩된 시크릿 감지 및 차단"
                    }
                ]
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Edit|Write",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/check-test-reminder.sh",
                        "description": "비즈니스 로직 변경 시 테스트 알림"
                    }
                ]
            }
        ],
        "Stop": [
            {
                "matcher": ".*",
                "hooks": [
                    {
                        "type": "prompt",
                        "prompt": "작업을 완료하기 전, docs/40_workflow/definition-of-done.md의 체크리스트를 확인하세요. 미완료 항목이 있다면 나열하고 처리 방법을 제안하세요."
                    }
                ]
            }
        ]
    }
}

# ---------------------------------------------------------------------------
# .claude/hooks/ — Hook Scripts
# ---------------------------------------------------------------------------

HOOK_GUARD_SECRETS = """\
#!/bin/bash
# guard-secrets.sh
# PreToolUse hook: 하드코딩된 시크릿 패턴 감지 및 차단
#
# Claude Code hooks receive JSON on stdin with:
# { "tool_name": "...", "tool_input": { ... } }

set -euo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', ''))
except:
    print('')
" 2>/dev/null || echo "")

# Extract content based on tool type
CONTENT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    # Bash: command field
    # Edit/Write: new_string or content field
    content = inp.get('command', '') or inp.get('content', '') or inp.get('new_string', '')
    print(content)
except:
    print('')
" 2>/dev/null || echo "")

if [ -z "$CONTENT" ]; then
    echo '{"decision": "allow"}'
    exit 0
fi

# Detect hardcoded secret patterns
if echo "$CONTENT" | grep -qiE '(API_KEY|SECRET_KEY|PASSWORD|PRIVATE_KEY|AUTH_TOKEN|ACCESS_TOKEN)\s*=\s*["\x27][^"\x27]{8,}'; then
    echo '{"decision": "block", "reason": "하드코딩된 시크릿이 감지되었습니다. 환경변수(.env 파일)를 사용하세요. 예: API_KEY = os.getenv(\"API_KEY\")"}'
    exit 0
fi

# Detect .env file being committed (git add .env)
if echo "$CONTENT" | grep -qE 'git (add|stage).*\\.env[^.ex]'; then
    echo '{"decision": "block", "reason": ".env 파일을 git에 추가하려 합니다. .gitignore를 확인하고 .env.example을 사용하세요."}'
    exit 0
fi

echo '{"decision": "allow"}'
"""

HOOK_CHECK_TEST_REMINDER = """\
#!/bin/bash
# check-test-reminder.sh
# PostToolUse hook: 비즈니스 로직 변경 시 테스트 파일 존재 여부 확인
#
# Returns a warning (not a block) — agent can continue but is reminded.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Only check source files (not tests, not docs, not config)
if ! echo "$FILE_PATH" | grep -qE '\\.(py|ts|js|go|java|rb|rs)$'; then
    exit 0
fi

# Skip if it's already a test file
if echo "$FILE_PATH" | grep -qE '(test|spec|_test|\.test\.|\.spec\.)'; then
    exit 0
fi

# Skip docs, config, migrations
if echo "$FILE_PATH" | grep -qE '(docs/|\.agent/|\.claude/|migrations?/|config/)'; then
    exit 0
fi

# Look for a corresponding test file
BASE=$(basename "$FILE_PATH" | sed 's/\\.[^.]*$//')
DIR=$(dirname "$FILE_PATH")

FOUND=false
for pattern in \
    "${DIR}/${BASE}.test.*" \
    "${DIR}/${BASE}.spec.*" \
    "${DIR}/__tests__/${BASE}*" \
    "tests/${BASE}*" \
    "test/${BASE}*" \
    "**/test_${BASE}.*" \
    "**/${BASE}_test.*"; do
    if compgen -G "$pattern" > /dev/null 2>&1; then
        FOUND=true
        break
    fi
done

if [ "$FOUND" = false ]; then
    # Output as a warning message to Claude (not a block)
    echo "{\"type\": \"warning\", \"message\": \"⚠️  ${FILE_PATH} 변경 감지 — 대응하는 테스트 파일을 찾을 수 없습니다. 비즈니스 로직 변경이라면 테스트 추가를 검토하세요. (.agent/04_TASK_EXECUTION_POLICY.md 4단계 검증 참조)\"}"
fi
"""

# ---------------------------------------------------------------------------
# CLAUDE.md (Entry Point)
# ---------------------------------------------------------------------------

CLAUDE_MD = """\
# Project Harness

이 프로젝트의 AI Agent 행동 제어 진입점입니다.
**Claude Code 세션 시작 시 이 파일을 가장 먼저 읽으세요.**

## 참조 우선순위

```
1순위  .agent/01_FORBIDDEN_ACTIONS.md   절대 금지
2순위  .agent/02_APPROVAL_REQUIRED.md   승인 필요
3순위  .agent/03_DECISION_PRINCIPLES.md 판단 기준
4순위  .agent/00_CHARTER.md             역할 및 원칙
5순위  docs/                            도메인 & 기술 지식
```

## 지금 바로 읽어야 할 파일

작업 전 반드시:
- [`.agent/00_CHARTER.md`](.agent/00_CHARTER.md) — 역할과 핵심 원칙
- [`.agent/01_FORBIDDEN_ACTIONS.md`](.agent/01_FORBIDDEN_ACTIONS.md) — 절대 금지 목록

상황별:
- 새 파일 위치: [`docs/20_architecture/directory-structure.md`](docs/20_architecture/directory-structure.md)
- 용어 확인: [`docs/10_product/glossary.md`](docs/10_product/glossary.md)
- 완료 기준: [`docs/40_workflow/definition-of-done.md`](docs/40_workflow/definition-of-done.md)
- 전체 문서 지도: [`docs/INDEX.md`](docs/INDEX.md)

## 자동화된 Sensor (Feedback Controls)

이 프로젝트는 `.claude/settings.json` 훅이 활성화되어 있습니다:

| 이벤트 | 동작 |
|--------|------|
| `PreToolUse` (Bash/Edit/Write) | 하드코딩된 시크릿 자동 차단 |
| `PostToolUse` (Edit/Write) | 테스트 누락 경고 |
| `Stop` | Definition of Done 체크 프롬프트 |

훅은 `.claude/hooks/` 디렉토리에 있습니다.
"""

# ---------------------------------------------------------------------------
# Master registry — path → content
# ---------------------------------------------------------------------------

DEFAULT_DOCS: dict[str, str] = {
    # .agent/ — Feedforward Controls
    ".agent/00_CHARTER.md": AGENT_00_CHARTER,
    ".agent/01_FORBIDDEN_ACTIONS.md": AGENT_01_FORBIDDEN_ACTIONS,
    ".agent/02_APPROVAL_REQUIRED.md": AGENT_02_APPROVAL_REQUIRED,
    ".agent/03_DECISION_PRINCIPLES.md": AGENT_03_DECISION_PRINCIPLES,
    ".agent/04_TASK_EXECUTION_POLICY.md": AGENT_04_TASK_EXECUTION_POLICY,
    # docs/
    "docs/INDEX.md": DOCS_INDEX,
    "docs/10_product/overview.md": DOCS_PRODUCT_OVERVIEW,
    "docs/10_product/glossary.md": DOCS_PRODUCT_GLOSSARY,
    "docs/10_product/scope.md": DOCS_PRODUCT_SCOPE,
    "docs/10_product/business-rules.md": DOCS_PRODUCT_BUSINESS_RULES,
    "docs/10_product/success-metrics.md": DOCS_PRODUCT_SUCCESS_METRICS,
    "docs/20_architecture/system-overview.md": DOCS_ARCH_SYSTEM_OVERVIEW,
    "docs/20_architecture/directory-structure.md": DOCS_ARCH_DIRECTORY_STRUCTURE,
    "docs/20_architecture/tech-stack.md": DOCS_ARCH_TECH_STACK,
    "docs/20_architecture/api-guidelines.md": DOCS_ARCH_API_GUIDELINES,
    "docs/20_architecture/data-model.md": DOCS_ARCH_DATA_MODEL,
    "docs/30_engineering/coding-standards.md": DOCS_ENG_CODING_STANDARDS,
    "docs/30_engineering/error-handling.md": DOCS_ENG_ERROR_HANDLING,
    "docs/30_engineering/security-guidelines.md": DOCS_ENG_SECURITY_GUIDELINES,
    "docs/30_engineering/performance-guidelines.md": DOCS_ENG_PERFORMANCE_GUIDELINES,
    "docs/40_workflow/git-flow.md": DOCS_WORKFLOW_GIT_FLOW,
    "docs/40_workflow/implementation-process.md": DOCS_WORKFLOW_IMPLEMENTATION_PROCESS,
    "docs/40_workflow/pr-policy.md": DOCS_WORKFLOW_PR_POLICY,
    "docs/40_workflow/definition-of-done.md": DOCS_WORKFLOW_DEFINITION_OF_DONE,
    "docs/50_quality/test-strategy.md": DOCS_QUALITY_TEST_STRATEGY,
    "docs/50_quality/review-checklist.md": DOCS_QUALITY_REVIEW_CHECKLIST,
    "docs/50_quality/dependency-policy.md": DOCS_QUALITY_DEPENDENCY_POLICY,
    "docs/60_templates/feature-spec.md": DOCS_TEMPLATE_FEATURE_SPEC,
    "docs/60_templates/bug-report.md": DOCS_TEMPLATE_BUG_REPORT,
    "docs/60_templates/pr-template.md": DOCS_TEMPLATE_PR_TEMPLATE,
    "docs/70_governance/doc-priority-order.md": DOCS_GOVERNANCE_DOC_PRIORITY,
    "docs/70_governance/change-management.md": DOCS_GOVERNANCE_CHANGE_MANAGEMENT,
    "docs/70_governance/CHANGELOG.md": DOCS_GOVERNANCE_CHANGELOG,
    # Root
    "CLAUDE.md": CLAUDE_MD,
}

# Sensor defaults
DEFAULT_SETTINGS_JSON = CLAUDE_SETTINGS_JSON
DEFAULT_HOOK_SCRIPTS = [
    {
        "path": ".claude/hooks/guard-secrets.sh",
        "content": HOOK_GUARD_SECRETS,
        "executable": True,
    },
    {
        "path": ".claude/hooks/check-test-reminder.sh",
        "content": HOOK_CHECK_TEST_REMINDER,
        "executable": True,
    },
]
