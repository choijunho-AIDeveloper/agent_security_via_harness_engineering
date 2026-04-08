"""FastAPI backend for LLM Council Harness Generator."""

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any

from .filesystem import (
    scan_existing_harness,
    diff_against_template,
    compute_dry_run,
    apply_harness_package,
    resolve_root,
)
from .harness_council import run_harness_council
from .default_docs import DEFAULT_DOCS, DEFAULT_SETTINGS_JSON, DEFAULT_HOOK_SCRIPTS

app = FastAPI(title="LLM Council Harness Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    target_path: str


class PreviewRequest(BaseModel):
    project_description: str
    target_path: str
    intent: str = "update"  # "init" | "update" | "patch"
    customization_request: str | None = None  # 커스터마이징 루프에서의 구체적 수정 지시


class FileReadRequest(BaseModel):
    target_path: str
    file_path: str  # 상대경로


class ApplyRequest(BaseModel):
    target_path: str
    guides: list[dict[str, Any]]
    sensors: dict[str, Any]
    claude_md: str | None = None


class TemplatePreviewRequest(BaseModel):
    target_path: str


class TemplateApplyRequest(BaseModel):
    target_path: str
    selected_paths: list[str] | None = None  # None = 전체 적용, 목록 = 선택 적용
    include_sensors: bool = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "ok", "service": "LLM Council Harness Generator"}


@app.post("/api/harness/validate-path")
async def validate_path_endpoint(request: AnalyzeRequest):
    """
    Check if a path exists and is accessible. Resolves ~ and relative paths.
    Returns the resolved absolute path.
    """
    from pathlib import Path

    raw = request.target_path.strip()
    # Expand ~ to home directory
    expanded = Path(raw).expanduser()
    resolved = expanded.resolve()

    exists = resolved.exists()
    is_dir = resolved.is_dir() if exists else False

    return {
        "input": raw,
        "resolved": str(resolved),
        "exists": exists,
        "is_dir": is_dir,
    }


@app.post("/api/harness/analyze")
async def analyze_harness(request: AnalyzeRequest):
    """
    Fast scan of the current project harness state.
    No LLM calls — returns the current file tree and template diff immediately.
    """
    try:
        existing = scan_existing_harness(request.target_path)
        diff = diff_against_template(existing["guides"])
        return {
            "tree": existing["tree"],
            "guides": {k: v[:500] for k, v in existing["guides"].items()},  # truncate for response
            "sensors": existing["sensors"],
            "claude_md": existing["claude_md"],
            "hook_scripts": list(existing["hook_scripts"].keys()),
            "diff": diff,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/harness/preview")
async def preview_harness(request: PreviewRequest):
    """
    Run the 3-stage council and return a dry-run preview.
    Streams SSE events as each stage completes.
    """
    async def event_stream():
        try:
            # Scan current state
            yield _sse({"type": "scan_start"})
            existing = scan_existing_harness(request.target_path)
            diff = diff_against_template(existing["guides"])
            yield _sse({"type": "scan_complete", "data": {
                "tree": existing["tree"],
                "diff": diff,
            }})

            # Stage 1
            yield _sse({"type": "stage1_start"})
            from .harness_council import stage1_propose_harness
            proposals = await stage1_propose_harness(
                request.project_description,
                request.intent,
                existing,
                diff,
                customization_request=request.customization_request,
            )
            yield _sse({"type": "stage1_complete", "data": proposals})

            # Stage 2
            yield _sse({"type": "stage2_start"})
            from .harness_council import stage2_evaluate_proposals, calculate_aggregate_rankings
            rankings, label_to_model = await stage2_evaluate_proposals(
                request.project_description, proposals
            )
            aggregate = calculate_aggregate_rankings(rankings, label_to_model)
            yield _sse({"type": "stage2_complete", "data": rankings, "metadata": {
                "label_to_model": label_to_model,
                "aggregate_rankings": aggregate,
            }})

            # Stage 3
            yield _sse({"type": "stage3_start"})
            from .harness_council import stage3_synthesize_harness
            stage3 = await stage3_synthesize_harness(
                request.project_description, proposals, rankings, label_to_model
            )
            yield _sse({"type": "stage3_complete", "data": stage3})

            # Dry run
            yield _sse({"type": "dryrun_start"})
            dry_run_guides = compute_dry_run(request.target_path, stage3.get("guides", []))

            # Compute dry run for CLAUDE.md
            if stage3.get("claude_md"):
                dry_run_guides += compute_dry_run(request.target_path, [{
                    "action": "create" if not existing.get("claude_md") else "modify",
                    "path": "CLAUDE.md",
                    "content": stage3["claude_md"],
                    "reason": "하네스 진입점 문서",
                }])

            yield _sse({"type": "dryrun_complete", "data": {
                "guides_preview": dry_run_guides,
                "sensors": stage3.get("sensors", {}),
            }})

            yield _sse({"type": "complete"})

        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.post("/api/harness/apply")
async def apply_harness(request: ApplyRequest):
    """
    Apply the approved harness package to the target directory.
    Expects the guides/sensors/claude_md from the /preview response.
    """
    try:
        result = apply_harness_package(
            root_path=request.target_path,
            guides=request.guides,
            sensors=request.sensors,
            claude_md=request.claude_md,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/harness/file")
async def read_file(request: FileReadRequest):
    """Read a single harness file's content for the markdown viewer."""
    from pathlib import Path
    from .filesystem import validate_path

    if not validate_path(request.target_path, request.file_path):
        raise HTTPException(status_code=400, detail="허용되지 않는 경로입니다")

    abs_path = resolve_root(request.target_path) / request.file_path
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

    try:
        content = abs_path.read_text(encoding="utf-8")
        return {"path": request.file_path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/harness/scan-files")
async def scan_files(request: AnalyzeRequest):
    """
    Scan and return the harness file tree with full file list.
    Used by the file tree viewer in customization phase.
    """
    from pathlib import Path

    root = resolve_root(request.target_path)
    harness_dirs = [".agent", "docs", ".claude"]
    harness_root_files = ["CLAUDE.md"]

    files: list[dict] = []

    for hdir in harness_dirs:
        dir_path = root / hdir
        if not dir_path.exists():
            continue
        for fp in sorted(dir_path.rglob("*")):
            if fp.is_file() and fp.suffix in (".md", ".json", ".sh", ".txt"):
                rel = str(fp.relative_to(root))
                files.append({
                    "path": rel,
                    "name": fp.name,
                    "dir": str(fp.parent.relative_to(root)),
                    "size": fp.stat().st_size,
                })

    for rf in harness_root_files:
        fp = root / rf
        if fp.exists():
            files.append({
                "path": rf,
                "name": rf,
                "dir": "",
                "size": fp.stat().st_size,
            })

    return {"files": files, "root": str(root)}


@app.post("/api/harness/template/preview")
async def template_preview(request: TemplatePreviewRequest):
    """
    Return the full default template content as a dry-run preview.
    No LLM calls — instant response from pre-written defaults.
    """
    try:
        from pathlib import Path
        root = resolve_root(request.target_path)

        previews = []
        for path, content in DEFAULT_DOCS.items():
            abs_path = root / path
            exists = abs_path.exists()
            content_before = None
            if exists:
                try:
                    content_before = abs_path.read_text(encoding="utf-8")
                except Exception:
                    content_before = "(읽기 실패)"

            previews.append({
                "action": "modify" if exists else "create",
                "path": path,
                "exists_before": exists,
                "content_before": content_before,
                "content_after": content,
                "reason": "기본 하네스 템플릿",
            })

        return {
            "guides_preview": previews,
            "sensors": {
                "settings_json": DEFAULT_SETTINGS_JSON,
                "hook_scripts": DEFAULT_HOOK_SCRIPTS,
            },
            "total_files": len(DEFAULT_DOCS),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/harness/template/apply")
async def template_apply(request: TemplateApplyRequest):
    """
    Apply the default template to the target directory.
    Instantly writes all pre-written files without LLM calls.
    """
    try:
        from .filesystem import validate_path
        from pathlib import Path

        root = resolve_root(request.target_path)
        selected = set(request.selected_paths) if request.selected_paths is not None else None

        # Build guide operations
        guides = []
        for path, content in DEFAULT_DOCS.items():
            if path == "CLAUDE.md":
                continue  # handled separately
            if selected is not None and path not in selected:
                continue
            guides.append({
                "action": "create",
                "path": path,
                "content": content,
                "reason": "기본 하네스 템플릿",
            })

        # CLAUDE.md
        claude_md = DEFAULT_DOCS.get("CLAUDE.md") if (
            selected is None or "CLAUDE.md" in selected
        ) else None

        # Sensors
        sensors = {}
        if request.include_sensors:
            sensors = {
                "settings_json": DEFAULT_SETTINGS_JSON,
                "hook_scripts": DEFAULT_HOOK_SCRIPTS,
            }

        result = apply_harness_package(
            root_path=request.target_path,
            guides=guides,
            sensors=sensors,
            claude_md=claude_md,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
