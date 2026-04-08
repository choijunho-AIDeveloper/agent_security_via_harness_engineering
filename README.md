# LLM Council — Harness Generator

[karpathy/llm-council](https://github.com/karpathy/llm-council)를 기반으로 제작되었습니다.

---

## 프로젝트 소개

여러 LLM이 서로 토론하고 평가한 뒤 최종 답을 합성하는 **3단계 심의(Council) 구조**를 활용해, AI 에이전트 하네스 문서를 자동 생성하는 로컬 웹앱입니다.

원본 프로젝트는 채팅 질문에 답하는 용도였지만, 이를 **AI 에이전트 행동 제어 문서(Harness)** 생성 도구로 전환했습니다.

### 하네스란?

> **Agent = Model + Harness**

모델 외부에서 에이전트의 행동을 제어하는 모든 구성 요소를 하네스라고 합니다.

- **가이드 (Feedforward)** — `.agent/`, `docs/` 마크다운 문서. 에이전트가 행동하기 *전에* 방향을 잡아줍니다.
- **센서 (Feedback)** — `.claude/settings.json` 훅 스크립트. 에이전트가 행동한 *후에* 감지하고 교정합니다.

---

## 3단계 심의 과정

1. **Stage 1 — 독립 설계안 제출**: 여러 LLM이 프로젝트 설명을 바탕으로 각자 하네스를 설계합니다.
2. **Stage 2 — 익명 동료 평가**: 각 LLM이 다른 LLM의 설계안을 **익명**으로 평가·순위를 매깁니다 (편애 방지).
3. **Stage 3 — Chairman 합성**: Chairman LLM이 모든 설계안과 평가를 종합해 최종 하네스를 생성합니다.

생성 후에는 **커스터마이징 루프**로 진입해, 파일 트리와 마크다운 뷰어를 보면서 Council에게 특정 문서 수정을 요청할 수 있습니다.

---

## 두 가지 모드

| 모드 | 설명 |
|------|------|
| **AI Council** | 3단계 심의를 통해 프로젝트 맞춤 하네스 생성. 약 30~60초 소요 |
| **기본 템플릿** | 미리 작성된 34개 파일을 LLM 없이 즉시 적용 |

두 모드 모두 동일한 파일 구조를 생성하며, 이후 커스터마이징 루프로 연결됩니다.

---

## 생성되는 파일 구조

```
project/
├── CLAUDE.md                          # 에이전트 진입점
├── .agent/
│   ├── 00_AGENT_CHARTER.md            # 핵심 정체성 및 경계
│   ├── 01_SAFETY_CONSTRAINTS.md       # 하드 스탑 및 금지 행동
│   ├── 02_COLLABORATION_PROTOCOL.md   # 인간과의 협업 프로토콜
│   ├── 03_QUALITY_STANDARDS.md        # 코드 품질 기준
│   └── 04_TASK_EXECUTION_POLICY.md    # 작업 실행 정책
├── docs/
│   ├── 10_product/                    # 목표, 페르소나, 로드맵
│   ├── 20_architecture/               # 기술 스택, ADR, 데이터 모델
│   ├── 30_engineering/                # 컨벤션, 환경 설정
│   ├── 40_workflow/                   # Git 흐름, CI/CD
│   ├── 50_quality/                    # 테스트 전략, 리뷰 체크리스트
│   ├── 60_templates/                  # PR/이슈/커밋 템플릿
│   └── 70_governance/                 # 변경 이력, 용어 사전
└── .claude/
    ├── settings.json                  # 훅 등록 설정
    └── hooks/
        ├── guard_secrets.sh           # 하드코딩된 자격증명 차단
        └── check_test_reminder.sh     # 테스트 누락 경고
```

---

## 설치 및 실행

### 1. 의존성 설치

**백엔드** ([uv](https://docs.astral.sh/uv/) 필요):
```bash
uv sync
```

**프론트엔드:**
```bash
cd frontend
npm install
```

### 2. API 키 설정

프로젝트 루트에 `.env` 파일 생성:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

API 키는 [openrouter.ai](https://openrouter.ai/)에서 발급받으세요.

### 3. 모델 설정 (선택)

`backend/config.py`에서 Council 구성을 변경할 수 있습니다:
```python
COUNCIL_MODELS = [
    "openai/gpt-4.1",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4-5",
]

CHAIRMAN_MODEL = "google/gemini-2.5-pro"
```

### 4. 실행

**터미널 1 — 백엔드:**
```bash
uv run python -m backend.main
# http://localhost:8001
```

**터미널 2 — 프론트엔드:**
```bash
cd frontend
npm run dev
# http://localhost:5173
```

---

## 기술 스택

- **백엔드:** FastAPI, async httpx, OpenRouter API (Python 3.10+)
- **프론트엔드:** React + Vite, ReactMarkdown
- **패키지 관리:** uv (Python), npm (JS)

---

## 감사의 말

이 프로젝트는 [karpathy/llm-council](https://github.com/karpathy/llm-council)을 fork하여 목적에 맞게 커스터마이징한 것입니다. 병렬 제안 → 익명 동료 평가 → Chairman 합성으로 이어지는 3단계 심의 구조는 원본 프로젝트의 아이디어에서 비롯되었습니다.
