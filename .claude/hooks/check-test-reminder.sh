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
if ! echo "$FILE_PATH" | grep -qE '\.(py|ts|js|go|java|rb|rs)$'; then
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
BASE=$(basename "$FILE_PATH" | sed 's/\.[^.]*$//')
DIR=$(dirname "$FILE_PATH")

FOUND=false
for pattern in     "${DIR}/${BASE}.test.*"     "${DIR}/${BASE}.spec.*"     "${DIR}/__tests__/${BASE}*"     "tests/${BASE}*"     "test/${BASE}*"     "**/test_${BASE}.*"     "**/${BASE}_test.*"; do
    if compgen -G "$pattern" > /dev/null 2>&1; then
        FOUND=true
        break
    fi
done

if [ "$FOUND" = false ]; then
    # Output as a warning message to Claude (not a block)
    echo "{"type": "warning", "message": "⚠️  ${FILE_PATH} 변경 감지 — 대응하는 테스트 파일을 찾을 수 없습니다. 비즈니스 로직 변경이라면 테스트 추가를 검토하세요. (.agent/04_TASK_EXECUTION_POLICY.md 4단계 검증 참조)"}"
fi
