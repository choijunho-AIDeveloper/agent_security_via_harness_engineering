"""
Harness Council — 3-stage LLM orchestration for generating project harnesses.

Stage 1: Each council model independently proposes a harness design
         (guide documents + sensor/hook configuration).
Stage 2: Each model evaluates the anonymized proposals and ranks them.
Stage 3: The Chairman synthesizes the best design into a structured JSON
         harness package ready for filesystem application.
"""

import re
import json
import asyncio
from typing import Any

from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL
from .template import (
    get_template_tree_description,
    get_sensor_patterns_description,
    GUIDE_SKELETONS,
    PHASE_1_REQUIRED,
)


# ---------------------------------------------------------------------------
# Stage 1 — Propose
# ---------------------------------------------------------------------------

async def stage1_propose_harness(
    project_description: str,
    intent: str,
    existing_harness: dict[str, Any],
    template_diff: dict[str, list],
    customization_request: str | None = None,
) -> list[dict[str, Any]]:
    """
    Each council model produces an independent harness design proposal.

    Returns list of:
        {"model": str, "proposal": str}
    """
    existing_guides_summary = _summarize_existing_guides(existing_harness["guides"])
    existing_sensors_summary = _summarize_existing_sensors(
        existing_harness.get("sensors"), existing_harness.get("hook_scripts", {})
    )

    customization_section = ""
    if customization_request:
        customization_section = f"""
## ⚡ 커스터마이징 요청 (최우선 반영)
{customization_request}

위 요청을 최우선으로 반영하여 관련 파일을 수정하세요.
변경이 필요없는 파일은 포함하지 마세요.
"""

    prompt = f"""당신은 AI Agent 하네스 설계 전문가입니다.{customization_section}
하네스(Harness)란 Agent = Model + Harness 공식에서 Model을 제외한 모든 인프라입니다.
두 가지 제어 메커니즘을 설계해야 합니다:
- **Guides (Feedforward)**: 행동 전에 예방하는 문서 (.agent/, docs/, CLAUDE.md)
- **Sensors (Feedback)**: 행동 후에 감지·교정하는 훅 (.claude/settings.json, hook scripts)

---

## 프로젝트 정보
{project_description}

## 작업 의도
{intent}

## 현재 디렉토리 구조
{existing_harness.get("tree", "(스캔 결과 없음)")}

## 기존 Guide 문서 현황
{existing_guides_summary}

## 기존 Sensor 설정 현황
{existing_sensors_summary}

## 템플릿 기준 비교
- 누락된 파일: {", ".join(template_diff.get("missing", [])) or "없음"}
- 이미 존재하는 파일: {", ".join(template_diff.get("existing", [])) or "없음"}
- 템플릿 외 추가 파일: {", ".join(template_diff.get("extra", [])) or "없음"}

{get_template_tree_description()}

{get_sensor_patterns_description()}

---

## 당신의 임무

이 프로젝트에 맞는 완전한 하네스를 설계하세요.

### 출력 형식 (반드시 이 구조를 따를 것)

#### ANALYSIS
(현재 하네스 상태 분석 — 무엇이 부족하고 무엇이 잘 되어 있는지)

#### GUIDES
각 파일에 대해 아래 형식으로 작성:

##### ACTION: create|modify|delete
##### PATH: 상대경로 (예: .agent/00_CHARTER.md)
##### REASON: 이 연산이 필요한 이유
##### CONTENT:
(파일 전체 내용 — create/modify 시 필수, delete 시 생략)
---

#### SENSORS
설치해야 할 훅과 그 이유를 설명하고, 아래 형식으로 작성:

##### HOOK: hook_pattern_key (template.py의 COMMON_HOOK_PATTERNS 키 또는 custom)
##### EVENT: PreToolUse|PostToolUse|Stop
##### MATCHER: 대상 툴 패턴
##### REASON: 왜 이 프로젝트에 필요한가
##### SCRIPT (custom인 경우):
(bash 스크립트 내용)
---

#### CLAUDE_MD
(CLAUDE.md 전체 내용)

---

규칙:
- 각 파일은 2,000 토큰 이내로 작성
- 산문이 아닌 조건문/리스트 형식 사용
- 프로젝트 특성에 맞지 않는 불필요한 파일은 포함하지 말 것
- Phase 1 필수 파일은 반드시 포함: {", ".join(PHASE_1_REQUIRED)}
"""

    messages = [{"role": "user", "content": prompt}]
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    results = []
    for model, response in responses.items():
        if response is not None:
            results.append({
                "model": model,
                "proposal": response.get("content", ""),
            })

    return results


# ---------------------------------------------------------------------------
# Stage 2 — Evaluate
# ---------------------------------------------------------------------------

async def stage2_evaluate_proposals(
    project_description: str,
    proposals: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """
    Each council model evaluates the anonymized proposals.

    Returns:
        (rankings_list, label_to_model)
    """
    labels = [chr(65 + i) for i in range(len(proposals))]  # A, B, C ...
    label_to_model = {
        f"Proposal {label}": proposal["model"]
        for label, proposal in zip(labels, proposals)
    }

    proposals_text = "\n\n".join([
        f"Proposal {label}:\n{proposal['proposal']}"
        for label, proposal in zip(labels, proposals)
    ])

    prompt = f"""당신은 AI Agent 하네스 설계를 평가하는 심사자입니다.

## 프로젝트 맥락
{project_description}

## 평가할 하네스 설계안 (익명)
{proposals_text}

---

## 평가 기준

각 설계안을 다음 5가지 기준으로 평가하세요:

1. **Guide 완전성** — Phase 1 필수 파일이 모두 포함되어 있는가? 내용이 구체적이고 조건문/리스트 형식인가?
2. **Sensor 실효성** — 훅이 단순 문서 경고가 아닌 구조적 제약을 제공하는가? 실제로 위험 행동을 차단할 수 있는가?
3. **프로젝트 적합성** — 이 특정 프로젝트의 기술 스택/도메인에 맞춤화되어 있는가?
4. **일관성** — Guide와 Sensor 간 충돌하거나 모순되는 규칙이 없는가?
5. **간결성** — 불필요한 내용 없이 핵심에 집중하는가?

## 출력 형식

각 설계안 개별 평가 후 반드시 아래 형식으로 최종 순위를 작성하세요:

FINAL RANKING:
1. Proposal X
2. Proposal Y
3. Proposal Z
"""

    messages = [{"role": "user", "content": prompt}]
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    results = []
    for model, response in responses.items():
        if response is not None:
            full_text = response.get("content", "")
            parsed = _parse_ranking(full_text)
            results.append({
                "model": model,
                "ranking": full_text,
                "parsed_ranking": parsed,
            })

    return results, label_to_model


# ---------------------------------------------------------------------------
# Stage 3 — Synthesize
# ---------------------------------------------------------------------------

async def stage3_synthesize_harness(
    project_description: str,
    proposals: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    label_to_model: dict[str, str],
) -> dict[str, Any]:
    """
    The Chairman synthesizes the best harness design into a structured JSON package.

    Returns:
        {
          "model": str,
          "reasoning": str,
          "guides": [{"action", "path", "content", "reason"}, ...],
          "sensors": {
              "settings_json": {...},
              "hook_scripts": [{"path", "content", "executable"}, ...]
          },
          "claude_md": str,
          "raw": str   # Chairman's full response (for display)
        }
    """
    proposals_text = "\n\n---\n\n".join([
        f"[{p['model']}]\n{p['proposal']}" for p in proposals
    ])
    rankings_text = "\n\n".join([
        f"[평가자: {r['model']}]\n순위: {r['parsed_ranking']}\n{r['ranking'][:800]}..."
        for r in rankings
    ])

    prompt = f"""당신은 AI Agent 하네스 설계의 최종 의사결정자(Chairman)입니다.
아래 설계안들과 동료 평가 결과를 바탕으로, 이 프로젝트에 최적화된 하네스를 합성하세요.

## 프로젝트 맥락
{project_description}

## 제출된 설계안
{proposals_text}

## 동료 평가 결과
{rankings_text}

---

## 출력 지시

반드시 아래 JSON 형식을 ```json ... ``` 코드블록 안에 작성하세요.
JSON 외의 설명은 reasoning 필드 안에만 포함하세요.

```json
{{
  "reasoning": "어떤 설계안의 어떤 부분을 채택했고 왜 그 결정을 내렸는지 (3-5문장)",
  "guides": [
    {{
      "action": "create",
      "path": ".agent/00_CHARTER.md",
      "content": "파일 전체 내용",
      "reason": "이 파일이 필요한 이유"
    }}
  ],
  "sensors": {{
    "settings_json": {{
      "hooks": {{
        "PreToolUse": [
          {{
            "matcher": "Bash|Edit|Write",
            "hooks": [
              {{
                "type": "command",
                "command": ".claude/hooks/guard-secrets.sh"
              }}
            ]
          }}
        ],
        "PostToolUse": [],
        "Stop": []
      }}
    }},
    "hook_scripts": [
      {{
        "path": ".claude/hooks/guard-secrets.sh",
        "content": "#!/bin/bash\\n...",
        "executable": true
      }}
    ]
  }},
  "claude_md": "CLAUDE.md 전체 내용"
}}
```

## 규칙
- action은 "create", "modify", "delete" 중 하나
- path는 반드시 .agent/, docs/, CLAUDE.md, .claude/ 중 하나의 하위 경로
- 절대경로 사용 금지
- 훅 스크립트는 반드시 #!/bin/bash 로 시작
- 각 파일 content는 실제로 사용 가능한 완성된 내용이어야 함
- 불필요한 파일은 포함하지 말 것 — 적을수록 좋음
"""

    messages = [{"role": "user", "content": prompt}]
    response = await query_model(CHAIRMAN_MODEL, messages, timeout=180.0)

    if response is None:
        return {
            "model": CHAIRMAN_MODEL,
            "reasoning": "Chairman 응답 실패",
            "guides": [],
            "sensors": {"settings_json": {}, "hook_scripts": []},
            "claude_md": None,
            "raw": "",
            "error": True,
        }

    raw = response.get("content", "")
    parsed = _parse_chairman_json(raw)

    return {
        "model": CHAIRMAN_MODEL,
        "reasoning": parsed.get("reasoning", ""),
        "guides": parsed.get("guides", []),
        "sensors": parsed.get("sensors", {"settings_json": {}, "hook_scripts": []}),
        "claude_md": parsed.get("claude_md"),
        "raw": raw,
    }


# ---------------------------------------------------------------------------
# Aggregate Rankings
# ---------------------------------------------------------------------------

def calculate_aggregate_rankings(
    rankings: list[dict[str, Any]],
    label_to_model: dict[str, str],
) -> list[dict[str, Any]]:
    """Compute average rank position across all peer evaluations."""
    from collections import defaultdict

    model_positions: dict[str, list[int]] = defaultdict(list)

    for ranking in rankings:
        for position, label in enumerate(ranking["parsed_ranking"], start=1):
            if label in label_to_model:
                model_positions[label_to_model[label]].append(position)

    aggregate = [
        {
            "model": model,
            "average_rank": round(sum(pos) / len(pos), 2),
            "rankings_count": len(pos),
        }
        for model, pos in model_positions.items()
        if pos
    ]
    aggregate.sort(key=lambda x: x["average_rank"])
    return aggregate


# ---------------------------------------------------------------------------
# Full Orchestration
# ---------------------------------------------------------------------------

async def run_harness_council(
    project_description: str,
    intent: str,
    existing_harness: dict[str, Any],
    template_diff: dict[str, list],
) -> dict[str, Any]:
    """
    Run the complete 3-stage harness council process.

    Returns:
        {
          "stage1": [...],
          "stage2": [...],
          "stage3": {...},
          "metadata": {
              "label_to_model": {...},
              "aggregate_rankings": [...]
          }
        }
    """
    # Stage 1
    proposals = await stage1_propose_harness(
        project_description, intent, existing_harness, template_diff
    )

    if not proposals:
        return {
            "stage1": [],
            "stage2": [],
            "stage3": {"error": True, "reasoning": "모든 모델이 응답하지 않았습니다."},
            "metadata": {},
        }

    # Stage 2
    rankings, label_to_model = await stage2_evaluate_proposals(project_description, proposals)
    aggregate = calculate_aggregate_rankings(rankings, label_to_model)

    # Stage 3
    stage3 = await stage3_synthesize_harness(
        project_description, proposals, rankings, label_to_model
    )

    return {
        "stage1": proposals,
        "stage2": rankings,
        "stage3": stage3,
        "metadata": {
            "label_to_model": label_to_model,
            "aggregate_rankings": aggregate,
        },
    }


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_ranking(text: str) -> list[str]:
    """Extract FINAL RANKING section from evaluation text."""
    if "FINAL RANKING:" in text:
        section = text.split("FINAL RANKING:", 1)[1]
        numbered = re.findall(r"\d+\.\s*Proposal\s+[A-Z]", section)
        if numbered:
            return [re.search(r"Proposal\s+[A-Z]", m).group() for m in numbered]
        return re.findall(r"Proposal\s+[A-Z]", section)
    return re.findall(r"Proposal\s+[A-Z]", text)


def _parse_chairman_json(raw: str) -> dict[str, Any]:
    """
    Extract and parse the JSON block from Chairman's response.
    Falls back to empty structure on failure.
    """
    # Try ```json ... ``` block first
    match = re.search(r"```json\s*([\s\S]+?)\s*```", raw)
    if match:
        json_str = match.group(1)
    else:
        # Try bare JSON object
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            json_str = match.group(0)
        else:
            return {}

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Attempt to repair common issues (trailing commas, etc.)
        repaired = re.sub(r",\s*([}\]])", r"\1", json_str)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            return {}


# ---------------------------------------------------------------------------
# Prompt Helpers
# ---------------------------------------------------------------------------

def _summarize_existing_guides(guides: dict[str, str]) -> str:
    if not guides:
        return "없음 (하네스가 설정되지 않은 프로젝트)"
    lines = []
    for path, content in sorted(guides.items()):
        preview = content[:120].replace("\n", " ") if content else "(빈 파일)"
        lines.append(f"- `{path}` ({len(content)}자): {preview}...")
    return "\n".join(lines)


def _summarize_existing_sensors(sensors: dict | None, hook_scripts: dict[str, str]) -> str:
    parts = []
    if sensors:
        hooks = sensors.get("hooks", {})
        for event, entries in hooks.items():
            parts.append(f"- {event}: {len(entries)}개 훅 등록됨")
    else:
        parts.append("- .claude/settings.json 없음")

    if hook_scripts:
        for path in hook_scripts:
            parts.append(f"- 스크립트: `{path}`")
    else:
        parts.append("- 훅 스크립트 없음")

    return "\n".join(parts) if parts else "없음"
