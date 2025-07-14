#!/bin/bash
# Session Compact Hook for RuleCrafter
# Runs when Claude session ends (/stop) to summarize conversation

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

# Log session end
SESSION_ID=$(date +%s)
TEMP_FILE="$RULECRAFTER_DIR/storage/session_${SESSION_ID}.tmp"
echo "$(date -Iseconds): SESSION-END" >> "$TEMP_FILE"

# If there's session output available from Claude (via stdin or environment)
# parse it with the conversation analyzer
if [[ -n "$CLAUDE_SESSION_OUTPUT" ]]; then
    echo "$CLAUDE_SESSION_OUTPUT" | python3 "$RULECRAFTER_DIR/analyzers/convo_analyzer.py" \
        "$PROJECT_ROOT" \
        2>/dev/null || true
elif [[ ! -t 0 ]]; then
    # Read from stdin if available
    TEMP_SESSION_FILE="/tmp/rulecrafter_session_$$.log"
    cat > "$TEMP_SESSION_FILE"
    
    if [[ -s "$TEMP_SESSION_FILE" ]]; then
        python3 "$RULECRAFTER_DIR/analyzers/convo_analyzer.py" \
            "$PROJECT_ROOT" \
            "$TEMP_SESSION_FILE" \
            2>/dev/null || true
    fi
    
    rm -f "$TEMP_SESSION_FILE"
fi

# Run a comprehensive analysis on session end
echo "🧠 RuleCrafter: Session ended, running analysis..."

# Generate rules and commands
if command -v python3 &> /dev/null; then
    # Generate rules with auto-approval for high-confidence items
    RULE_RESULT=$(python3 "$RULECRAFTER_DIR/generators/rule_generator.py" \
        "$PROJECT_ROOT" \
        --auto-approve \
        2>/dev/null || echo '{"generated_rules": 0, "approved_rules": 0}')
    
    # Generate commands
    CMD_RESULT=$(python3 "$RULECRAFTER_DIR/generators/cmd_builder.py" \
        "$PROJECT_ROOT" \
        2>/dev/null || echo '{"created_commands": []}')
    
    # Parse results and show summary
    GENERATED_RULES=$(echo "$RULE_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('generated_rules', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
    
    APPROVED_RULES=$(echo "$RULE_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('approved_rules', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
    
    CREATED_COMMANDS=$(echo "$CMD_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(len(data.get('created_commands', [])))
except:
    print(0)
" 2>/dev/null || echo "0")
    
    # Show summary
    if (( GENERATED_RULES > 0 || CREATED_COMMANDS > 0 )); then
        echo "📊 RuleCrafter Summary:"
        if (( GENERATED_RULES > 0 )); then
            echo "   📝 Generated $GENERATED_RULES rules ($APPROVED_RULES auto-approved)"
        fi
        if (( CREATED_COMMANDS > 0 )); then
            echo "   🤖 Created $CREATED_COMMANDS new commands"
        fi
        echo "   💡 Use /rulecrafter-review to see pending suggestions"
    else
        echo "✅ RuleCrafter: No new patterns detected this session"
    fi
fi

exit 0
