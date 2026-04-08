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
if echo "$CONTENT" | grep -qiE '(API_KEY|SECRET_KEY|PASSWORD|PRIVATE_KEY|AUTH_TOKEN|ACCESS_TOKEN)\s*=\s*["'][^"']{8,}'; then
    echo '{"decision": "block", "reason": "하드코딩된 시크릿이 감지되었습니다. 환경변수(.env 파일)를 사용하세요. 예: API_KEY = os.getenv("API_KEY")"}'
    exit 0
fi

# Detect .env file being committed (git add .env)
if echo "$CONTENT" | grep -qE 'git (add|stage).*\.env[^.ex]'; then
    echo '{"decision": "block", "reason": ".env 파일을 git에 추가하려 합니다. .gitignore를 확인하고 .env.example을 사용하세요."}'
    exit 0
fi

echo '{"decision": "allow"}'
