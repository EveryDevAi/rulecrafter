#!/bin/bash
# Post-tool Hook for RuleCrafter
# Runs after successful Claude Code tool execution to learn from results

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

# Get session information
if [[ -f "$RULECRAFTER_DIR/storage/current_session.tmp" ]]; then
    SESSION_ID=$(cat "$RULECRAFTER_DIR/storage/current_session.tmp")
    TEMP_FILE="$RULECRAFTER_DIR/storage/session_${SESSION_ID}.tmp"
    
    # Log the post-tool event
    echo "$(date -Iseconds): POST-TOOL: SUCCESS" >> "$TEMP_FILE"
    
    # Clean up session files
    rm -f "$RULECRAFTER_DIR/storage/current_tool.tmp"
    rm -f "$RULECRAFTER_DIR/storage/current_session.tmp"
fi

# Check if it's time to run learning (every 10 tool uses)
PATTERNS_FILE="$RULECRAFTER_DIR/storage/patterns.json"
if [[ -f "$PATTERNS_FILE" ]]; then
    # Count total sessions
    TOTAL_SESSIONS=$(python3 -c "
import json
try:
    with open('$PATTERNS_FILE', 'r') as f:
        data = json.load(f)
    print(data.get('total_sessions', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
    
    # Run learning every 10 sessions
    if (( TOTAL_SESSIONS > 0 && TOTAL_SESSIONS % 10 == 0 )); then
        echo "🧠 RuleCrafter: Running pattern analysis (session $TOTAL_SESSIONS)..."
        
        # Run rule generation
        if command -v python3 &> /dev/null; then
            python3 "$RULECRAFTER_DIR/generators/rule_generator.py" \
                "$PROJECT_ROOT" \
                --auto-approve \
                2>/dev/null || true
        fi
        
        # Run command generation
        if command -v python3 &> /dev/null; then
            python3 "$RULECRAFTER_DIR/generators/cmd_builder.py" \
                "$PROJECT_ROOT" \
                2>/dev/null || true
        fi
        
        echo "✅ RuleCrafter: Analysis complete"
    fi
fi

# Clean up old temporary files (older than 1 hour)
find "$RULECRAFTER_DIR/storage" -name "session_*.tmp" -mmin +60 -delete 2>/dev/null || true

exit 0
