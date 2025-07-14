## rulecrafter-mine
Trigger immediate pattern analysis and rule generation.

**Usage:** `/rulecrafter-mine [--force]`

**Arguments:**
- `--force` (optional): Force analysis even if insufficient data

**Description:**
Manually triggers RuleCrafter's pattern analysis and rule generation process without waiting for the automatic threshold.

**What this command does:**
1. Analyzes collected patterns
2. Generates new rules based on current data
3. Creates new slash commands if patterns are detected
4. Shows summary of generated content

```bash
#!/bin/bash
PROJECT_ROOT=$(pwd)
while [[ "$PROJECT_ROOT" != "/" && ! -d "$PROJECT_ROOT/.claude" ]]; do
    PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

if [[ "$PROJECT_ROOT" == "/" ]]; then
    echo "❌ RuleCrafter not found in this project"
    exit 1
fi

RULECRAFTER_DIR="$PROJECT_ROOT/.claude/rulecrafter"

if [[ ! -d "$RULECRAFTER_DIR" ]]; then
    echo "❌ RuleCrafter is not initialized in this project"
    exit 1
fi

echo "🧠 RuleCrafter: Starting pattern analysis..."

# Check if we have enough data (unless --force is used)
if [[ "$1" != "--force" ]]; then
    PATTERNS_FILE="$RULECRAFTER_DIR/storage/patterns.json"
    if [[ -f "$PATTERNS_FILE" ]]; then
        TOTAL_SESSIONS=$(python3 -c "
import json
try:
    with open('$PATTERNS_FILE', 'r') as f:
        data = json.load(f)
    print(data.get('total_sessions', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
        
        if (( TOTAL_SESSIONS < 5 )); then
            echo "⚠️  Limited data available ($TOTAL_SESSIONS sessions)"
            echo "   Consider using --force or collect more data"
            echo "   RuleCrafter works best after 10+ tool uses"
        fi
    else
        echo "⚠️  No patterns file found"
        if [[ "$1" != "--force" ]]; then
            echo "   Use --force to run analysis anyway"
            exit 1
        fi
    fi
fi

echo "📊 Analyzing patterns..."

# Run rule generation
if command -v python3 &> /dev/null; then
    echo "🔍 Generating rules..."
    RULE_RESULT=$(python3 "$RULECRAFTER_DIR/generators/rule_generator.py" \
        "$PROJECT_ROOT" \
        --auto-approve \
        2>/dev/null || echo '{"generated_rules": 0, "approved_rules": 0}')
    
    echo "🛠️  Building commands..."
    CMD_RESULT=$(python3 "$RULECRAFTER_DIR/generators/cmd_builder.py" \
        "$PROJECT_ROOT" \
        2>/dev/null || echo '{"created_commands": []}')
    
    # Parse and display results
    echo ""
    echo "📈 Analysis Results:"
    echo "==================="
    
    # Parse rule results
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
    
    PENDING_RULES=$((GENERATED_RULES - APPROVED_RULES))
    
    # Parse command results
    CREATED_COMMANDS=$(echo "$CMD_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    commands = data.get('created_commands', [])
    if commands:
        print(f'{len(commands)}')
        for cmd in commands:
            print(f'   - /{cmd}')
    else:
        print('0')
except:
    print('0')
" 2>/dev/null)
    
    # Display summary
    if [[ "$GENERATED_RULES" -gt 0 ]]; then
        echo "📝 Rules:"
        echo "   Generated: $GENERATED_RULES"
        echo "   Auto-approved: $APPROVED_RULES"
        if [[ $PENDING_RULES -gt 0 ]]; then
            echo "   Pending approval: $PENDING_RULES"
            echo "   💡 Use /rulecrafter-review to approve pending rules"
        fi
    else
        echo "📝 Rules: No new rules generated"
    fi
    
    if [[ "$CREATED_COMMANDS" =~ ^[0-9]+$ ]] && [[ $CREATED_COMMANDS -gt 0 ]]; then
        echo ""
        echo "🤖 Commands: $CREATED_COMMANDS new commands created"
        echo "$CMD_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    commands = data.get('created_commands', [])
    for cmd in commands:
        print(f'   - /{cmd}')
except:
    pass
" 2>/dev/null
    else
        echo ""
        echo "🤖 Commands: No new commands created"
    fi
    
    echo ""
    
    # Show next steps
    if [[ $PENDING_RULES -gt 0 ]] || [[ $CREATED_COMMANDS -gt 0 ]]; then
        echo "✅ Analysis complete! New content generated."
        echo ""
        echo "📋 Next steps:"
        if [[ $PENDING_RULES -gt 0 ]]; then
            echo "   • Review pending rules: /rulecrafter-review"
        fi
        if [[ $CREATED_COMMANDS -gt 0 ]]; then
            echo "   • Try new commands with tab completion"
        fi
        echo "   • Check status anytime: /rulecrafter-status"
    else
        echo "✅ Analysis complete! No new patterns detected."
        echo "   💡 RuleCrafter needs more usage data to generate meaningful suggestions."
    fi
    
else
    echo "❌ Python 3 not found - required for analysis"
    exit 1
fi
```

*This command is part of RuleCrafter's management interface*
