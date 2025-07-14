#!/bin/bash
# Pre-tool Hook for RuleCrafter
# Runs before every Claude Code tool execution to capture context

# Get the project root (where .claude directory is)
PROJECT_ROOT=$(pwd)
while [[ "$PROJECT_ROOT" != "/" && ! -d "$PROJECT_ROOT/.claude" ]]; do
    PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

if [[ "$PROJECT_ROOT" == "/" ]]; then
    # Not in a Claude project, exit silently
    exit 0
fi

RULECRAFTER_DIR="$PROJECT_ROOT/.claude/rulecrafter"

# Check if RuleCrafter is installed
if [[ ! -d "$RULECRAFTER_DIR" ]]; then
    exit 0
fi

# Get tool information from environment variables (set by Claude Code)
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_ARGS="${CLAUDE_TOOL_ARGS:-}"

# Create a temporary file for this session
SESSION_ID=$(date +%s)
TEMP_FILE="$RULECRAFTER_DIR/storage/session_${SESSION_ID}.tmp"

# Log the pre-tool event
echo "$(date -Iseconds): PRE-TOOL: $TOOL_NAME $TOOL_ARGS" >> "$TEMP_FILE"

# Run the context analyzer
if command -v python3 &> /dev/null; then
    python3 "$RULECRAFTER_DIR/analyzers/context_analyzer.py" \
        "$PROJECT_ROOT" \
        "$TOOL_NAME" \
        2>/dev/null || true
fi

# Store tool information for post-tool hook
echo "$TOOL_NAME" > "$RULECRAFTER_DIR/storage/current_tool.tmp"
echo "$SESSION_ID" > "$RULECRAFTER_DIR/storage/current_session.tmp"

exit 0
