"""
Harness template definitions.

Defines the standard file tree structure, skeleton content, and sensor patterns
that the LLM Council uses as a baseline when generating project harnesses.
"""

# ---------------------------------------------------------------------------
# Guide Templates (Feedforward Controls)
# ---------------------------------------------------------------------------

GUIDE_FILE_DESCRIPTIONS = {
    ".agent/00_CHARTER.md": "Agent 역할 정의, 핵심 원칙, 문서 참조 우선순위 (최우선 참조)",
    ".agent/01_FORBIDDEN_ACTIONS.md": "절대 금지 행동 목록 — 조건문/리스트 형식, 산문 금지",
    ".agent/02_APPROVAL_REQUIRED.md": "사용자 승인이 필요한 행동 목록",
    ".agent/03_DECISION_PRINCIPLES.md": "모호하거나 충돌하는 상황에서의 판단 기준 및 우선순위",
    ".agent/04_TASK_EXECUTION_POLICY.md": "작업 수행 절차 (분석 → 계획 → 구현 → 검증)",
    "docs/INDEX.md": "문서 전체 지도 + 상황별 참조 가이드 테이블 (Agent의 내비게이션 맵)",
    "docs/10_product/overview.md": "제품 비전, 목적, 타겟 유저",
    "docs/10_product/scope.md": "In-scope / Out-of-scope 명시",
    "docs/10_product/business-rules.md": "비즈니스 규칙 및 핵심 워크플로우",
    "docs/10_product/glossary.md": "도메인 용어 통일 사전 (용어 불일치 방지의 핵심)",
    "docs/10_product/success-metrics.md": "KPI, 성공 지표",
    "docs/20_architecture/system-overview.md": "전체 시스템 구조 및 서비스 경계",
    "docs/20_architecture/directory-structure.md": "파일/폴더 생성 위치 규칙",
    "docs/20_architecture/tech-stack.md": "사용 언어, 프레임워크, 정확한 버전",
    "docs/20_architecture/api-guidelines.md": "API 설계 규약 (REST/GraphQL 등)",
    "docs/20_architecture/data-model.md": "DB 스키마, 엔티티 관계",
    "docs/30_engineering/coding-standards.md": "네이밍, 포맷팅, 설계 규칙",
    "docs/30_engineering/error-handling.md": "에러 처리 패턴, 로깅 규칙",
    "docs/30_engineering/security-guidelines.md": "보안 요구사항, 하드코딩 금지 등",
    "docs/30_engineering/performance-guidelines.md": "성능 기준, 안티패턴",
    "docs/40_workflow/git-flow.md": "브랜치 전략, 커밋 메시지 규약",
    "docs/40_workflow/implementation-process.md": "구현 절차, 작업 단위 기준",
    "docs/40_workflow/pr-policy.md": "PR 단위, 작성 규칙",
    "docs/40_workflow/definition-of-done.md": "완료 기준 (DoD) — Agent가 작업 완료를 판단하는 기준",
    "docs/50_quality/test-strategy.md": "테스트 범위, 도구, 필수 기준",
    "docs/50_quality/review-checklist.md": "코드 리뷰 체크리스트",
    "docs/50_quality/dependency-policy.md": "새 라이브러리 추가 조건",
    "docs/60_templates/feature-spec.md": "기능 명세서 템플릿",
    "docs/60_templates/bug-report.md": "버그 리포트 템플릿",
    "docs/60_templates/pr-template.md": "PR 작성 템플릿",
    "docs/70_governance/doc-priority-order.md": "문서 충돌 시 우선순위 규칙",
    "docs/70_governance/change-management.md": "문서 변경 절차",
    "docs/70_governance/CHANGELOG.md": "규칙 변경 이력 (Agent가 구버전 규칙 참조 방지)",
    "CLAUDE.md": "전체 하네스 진입점 — Agent가 가장 먼저 참조하는 문서",
}

# Skeleton content for each guide file (used as fallback / starting point)
GUIDE_SKELETONS = {
    ".agent/00_CHARTER.md": """\
# Agent Charter

## Role
You are a [ROLE] for [PROJECT_NAME].

## Priority Rules (충돌 시 이 순서를 따름)
1. `.agent/01_FORBIDDEN_ACTIONS.md` — 절대 금지
2. `.agent/02_APPROVAL_REQUIRED.md` — 승인 필요
3. `.agent/03_DECISION_PRINCIPLES.md` — 판단 기준
4. `docs/` 하위 모든 문서

## Core Principles
- 모르는 것은 임의로 작성하지 말고 질문할 것
- 기존 코드 수정 시 반드시 원래 의도를 파악하고 유지할 것
- 한 번에 하나의 작업만 수행할 것
- 작업 완료 전 `docs/40_workflow/definition-of-done.md` 확인
""",

    ".agent/01_FORBIDDEN_ACTIONS.md": """\
# Forbidden Actions

## 절대 금지 목록

- [ ] API Key, 비밀번호, 토큰을 코드에 직접 작성
- [ ] 사용자 승인 없이 외부 라이브러리 추가
- [ ] 테스트 없이 핵심 비즈니스 로직 수정
- [ ] 프로덕션 데이터 직접 수정 또는 삭제
- [ ] 기존 공개 API 시그니처 무단 변경
- [ ] `any` 타입 사용 (TypeScript 프로젝트)
- [ ] `TODO`, `FIXME`, `HACK` 주석을 남긴 채 PR 제출
""",

    ".agent/02_APPROVAL_REQUIRED.md": """\
# Approval Required

## 사용자 승인이 필요한 작업

다음 작업은 반드시 사용자에게 먼저 확인을 받고 진행할 것:

- DB 스키마 변경 (마이그레이션 포함)
- 외부 의존성(라이브러리) 추가 또는 버전 업그레이드
- 아키텍처 패턴 또는 폴더 구조 변경
- 환경 변수 추가/수정/삭제
- 50줄 이상의 기존 코드 변경
- 새로운 외부 서비스 연동
- CI/CD 파이프라인 수정
""",

    ".agent/03_DECISION_PRINCIPLES.md": """\
# Decision Principles

## 모호한 상황에서의 판단 기준

### 충돌 해결 우선순위
1. 보안 > 기능 > 성능 > 가독성
2. 명시된 규칙 > 관례 > 추론

### 불확실할 때
- 작은 것부터: 범위를 최소화하여 구현
- 가역적 선택: 되돌리기 어려운 결정은 승인 후 진행
- 명시적 질문: 가정에 기반한 구현 대신 질문

### 코드 변경 시
- 기존 패턴을 먼저 파악하고 일관성 유지
- 리팩토링과 기능 추가를 동시에 진행하지 않음
""",

    ".agent/04_TASK_EXECUTION_POLICY.md": """\
# Task Execution Policy

## 작업 수행 절차

### 1. 분석 (Analyze)
- 요청 의도와 범위 파악
- 영향받는 파일/모듈 식별
- `docs/` 관련 문서 참조

### 2. 계획 (Plan)
- 변경 목록 작성 후 사용자에게 확인
- 02_APPROVAL_REQUIRED.md 항목 해당 여부 점검

### 3. 구현 (Implement)
- 한 번에 하나의 논리 단위만 변경
- 커밋 단위를 작게 유지

### 4. 검증 (Verify)
- `docs/40_workflow/definition-of-done.md` 체크리스트 확인
- 테스트 실행
- 변경 내용 요약 후 사용자에게 보고
""",

    "docs/INDEX.md": """\
# Documentation Index

## 상황별 참조 문서 가이드

| 상황 | 참조 문서 |
|------|-----------|
| 새 기능 구현 시작 | `docs/10_product/scope.md` → `docs/20_architecture/` |
| 새 파일 생성 위치 | `docs/20_architecture/directory-structure.md` |
| 변수/함수 네이밍 | `docs/30_engineering/coding-standards.md` |
| 에러 처리 방법 | `docs/30_engineering/error-handling.md` |
| 커밋/PR 작성 | `docs/40_workflow/git-flow.md` + `pr-policy.md` |
| 완료 여부 판단 | `docs/40_workflow/definition-of-done.md` |
| 용어 확인 | `docs/10_product/glossary.md` |
| 새 라이브러리 추가 | `docs/50_quality/dependency-policy.md` |

## 문서 우선순위
`.agent/` > `docs/` > 기타 문서
""",

    "CLAUDE.md": """\
# Project Harness

이 프로젝트의 AI Agent 행동 제어 문서 진입점입니다.

## 참조 우선순위

1. `.agent/` — Agent 행동 제어 (최우선)
2. `docs/` — 프로젝트 도메인 지식
3. 코드 및 주석

## 빠른 참조

- 무언가 하기 전: `.agent/00_CHARTER.md`
- 금지 행동 확인: `.agent/01_FORBIDDEN_ACTIONS.md`
- 승인 필요 확인: `.agent/02_APPROVAL_REQUIRED.md`
- 어디에 파일 생성?: `docs/20_architecture/directory-structure.md`
- 완료 기준: `docs/40_workflow/definition-of-done.md`
- 용어 모를 때: `docs/10_product/glossary.md`
""",
}

# ---------------------------------------------------------------------------
# Sensor Templates (Feedback Controls — Claude Code Hooks)
# ---------------------------------------------------------------------------

# Base settings.json structure
SETTINGS_JSON_SKELETON = {
    "hooks": {
        "PreToolUse": [],
        "PostToolUse": [],
        "Stop": []
    }
}

# Common hook patterns library — reusable building blocks
COMMON_HOOK_PATTERNS = {
    "block_hardcoded_secrets": {
        "description": "하드코딩된 시크릿(API Key, 비밀번호 등) 감지 및 차단",
        "event": "PreToolUse",
        "matcher": "Bash|Edit|Write",
        "hook": {
            "type": "command",
            "command": ".claude/hooks/guard-secrets.sh"
        },
        "script": """\
#!/bin/bash
# guard-secrets.sh — PreToolUse hook: block hardcoded secrets
INPUT=$(cat)
TOOL=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)
CONTENT=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); inp=d.get('tool_input',{}); print(inp.get('command','') or inp.get('content','') or inp.get('new_string',''))" 2>/dev/null)

# Check for hardcoded secret patterns
if echo "$CONTENT" | grep -qiE '(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY)\\s*=\\s*["\\''][^\\"'']{8,}'; then
  echo '{"decision": "block", "reason": "하드코딩된 시크릿 패턴이 감지되었습니다. 환경변수를 사용하세요."}'
  exit 0
fi

echo '{"decision": "allow"}'
"""
    },

    "require_test_before_logic_change": {
        "description": "핵심 비즈니스 로직 변경 시 테스트 파일 존재 여부 확인",
        "event": "PostToolUse",
        "matcher": "Edit|Write",
        "hook": {
            "type": "command",
            "command": ".claude/hooks/check-test-coverage.sh"
        },
        "script": """\
#!/bin/bash
# check-test-coverage.sh — PostToolUse hook: warn when modifying logic without tests
INPUT=$(cat)
PATH_CHANGED=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only check source files (not tests, not docs)
if echo "$PATH_CHANGED" | grep -qE '\\.(py|ts|js|go|java)$' && ! echo "$PATH_CHANGED" | grep -qE '(test|spec|_test)'; then
  BASE=$(basename "$PATH_CHANGED" | sed 's/\\.[^.]*$//')
  DIR=$(dirname "$PATH_CHANGED")
  if ! find . -name "*${BASE}*test*" -o -name "*test*${BASE}*" 2>/dev/null | grep -q .; then
    echo "{\"type\": \"warning\", \"message\": \"${PATH_CHANGED} 변경 감지. 대응하는 테스트 파일이 없습니다.\"}"
  fi
fi
"""
    },

    "validate_path_safety": {
        "description": "허용된 디렉토리 밖 파일 접근 차단",
        "event": "PreToolUse",
        "matcher": "Write|Edit",
        "hook": {
            "type": "command",
            "command": ".claude/hooks/guard-path.sh"
        },
        "script": """\
#!/bin/bash
# guard-path.sh — PreToolUse hook: block writes outside allowed directories
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# Block writes to sensitive system paths
if echo "$FILE_PATH" | grep -qE '^/(etc|sys|proc|boot|usr/bin|usr/sbin)'; then
  echo '{"decision": "block", "reason": "시스템 디렉토리 쓰기가 차단되었습니다."}'
  exit 0
fi

echo '{"decision": "allow"}'
"""
    },

    "definition_of_done_check": {
        "description": "작업 완료 전 DoD 체크리스트 확인 프롬프트",
        "event": "Stop",
        "matcher": "*",
        "hook": {
            "type": "prompt",
            "prompt": "작업을 완료하기 전에 docs/40_workflow/definition-of-done.md의 체크리스트를 확인했는가? 미완료 항목이 있다면 나열하라."
        },
        "script": None  # prompt type — no script file needed
    },
}

# ---------------------------------------------------------------------------
# Phase structure for progressive adoption
# ---------------------------------------------------------------------------

PHASE_1_REQUIRED = [
    ".agent/00_CHARTER.md",
    ".agent/01_FORBIDDEN_ACTIONS.md",
    ".agent/02_APPROVAL_REQUIRED.md",
    "docs/INDEX.md",
    "docs/10_product/overview.md",
    "docs/10_product/glossary.md",
    "docs/20_architecture/tech-stack.md",
    "docs/30_engineering/coding-standards.md",
    "docs/40_workflow/definition-of-done.md",
    "CLAUDE.md",
]

PHASE_2_COLLABORATIVE = [
    ".agent/03_DECISION_PRINCIPLES.md",
    ".agent/04_TASK_EXECUTION_POLICY.md",
    "docs/40_workflow/git-flow.md",
    "docs/40_workflow/pr-policy.md",
    "docs/50_quality/test-strategy.md",
    "docs/60_templates/feature-spec.md",
    "docs/60_templates/pr-template.md",
    "docs/70_governance/doc-priority-order.md",
    "docs/70_governance/CHANGELOG.md",
]

PHASE_3_EXTENDED = [
    "docs/10_product/scope.md",
    "docs/10_product/business-rules.md",
    "docs/10_product/success-metrics.md",
    "docs/20_architecture/system-overview.md",
    "docs/20_architecture/directory-structure.md",
    "docs/20_architecture/api-guidelines.md",
    "docs/20_architecture/data-model.md",
    "docs/30_engineering/error-handling.md",
    "docs/30_engineering/security-guidelines.md",
    "docs/30_engineering/performance-guidelines.md",
    "docs/40_workflow/implementation-process.md",
    "docs/50_quality/review-checklist.md",
    "docs/50_quality/dependency-policy.md",
    "docs/60_templates/bug-report.md",
    "docs/70_governance/change-management.md",
]

ALL_TEMPLATE_FILES = PHASE_1_REQUIRED + PHASE_2_COLLABORATIVE + PHASE_3_EXTENDED


def get_template_tree_description() -> str:
    """Return a formatted description of the full template structure for use in prompts."""
    lines = ["## 표준 하네스 파일 트리\n"]
    current_dir = None
    for path, desc in GUIDE_FILE_DESCRIPTIONS.items():
        parts = path.split("/")
        if len(parts) == 1:
            lines.append(f"- `{path}` — {desc}")
        else:
            parent = "/".join(parts[:-1])
            if parent != current_dir:
                current_dir = parent
                lines.append(f"\n### {parent}/")
            lines.append(f"  - `{parts[-1]}` — {desc}")
    return "\n".join(lines)


def get_sensor_patterns_description() -> str:
    """Return a formatted description of available sensor patterns for use in prompts."""
    lines = ["## 사용 가능한 Sensor 패턴 (Feedback Controls)\n"]
    for key, pattern in COMMON_HOOK_PATTERNS.items():
        lines.append(f"### {key}")
        lines.append(f"- **설명**: {pattern['description']}")
        lines.append(f"- **이벤트**: `{pattern['event']}`")
        lines.append(f"- **매처**: `{pattern['matcher']}`")
        lines.append("")
    return "\n".join(lines)
