## rulecrafter-status
Show the current status of RuleCrafter learning system.

**Usage:** `/rulecrafter-status`

**Description:**
Displays comprehensive information about RuleCrafter's learning progress, including patterns collected, rules generated, and commands created.

**What this command shows:**
- Total patterns collected
- Number of error types tracked
- Generated rules (approved and pending)
- Auto-generated commands
- System health and configuration status

```bash
#!/bin/bash
PROJECT_ROOT=$(pwd)
while [[ "$PROJECT_ROOT" != "/" && ! -d "$PROJECT_ROOT/.claude" ]]; do
    PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

if [[ "$PROJECT_ROOT" == "/" ]]; then
    echo "❌ RuleCrafter not found in this project"
    echo "   Run: rulecrafter init"
    exit 1
fi

RULECRAFTER_DIR="$PROJECT_ROOT/.claude/rulecrafter"

if [[ ! -d "$RULECRAFTER_DIR" ]]; then
    echo "❌ RuleCrafter is not initialized in this project"
    echo "   Run: rulecrafter init"
    exit 1
fi

echo "📊 RuleCrafter Status Report"
echo "============================"
echo ""

# Check patterns file
PATTERNS_FILE="$RULECRAFTER_DIR/storage/patterns.json"
if [[ -f "$PATTERNS_FILE" ]]; then
    echo "📈 Learning Progress:"
    python3 -c "
import json
try:
    with open('$PATTERNS_FILE', 'r') as f:
        data = json.load(f)
    
    print(f'   Sessions analyzed: {data.get(\"total_sessions\", 0)}')
    print(f'   Commands tracked: {len(data.get(\"commands\", {}))}')
    print(f'   Error patterns: {len(data.get(\"errors\", {}))}')
    print(f'   Files monitored: {len(data.get(\"files_changed\", {}))}')
    print(f'   Last updated: {data.get(\"last_updated\", \"Never\")}')
except:
    print('   No patterns collected yet')
"
else
    echo "📈 Learning Progress: No data collected yet"
fi

echo ""

# Check for auto-generated commands
COMMANDS_DIR="$PROJECT_ROOT/.claude/commands/auto-generated"
if [[ -d "$COMMANDS_DIR" ]]; then
    COMMAND_COUNT=$(find "$COMMANDS_DIR" -name "*.md" | wc -l)
    echo "🤖 Auto-generated Commands: $COMMAND_COUNT"
    if [[ $COMMAND_COUNT -gt 0 ]]; then
        echo "   Available commands:"
        find "$COMMANDS_DIR" -name "*.md" -exec basename {} .md \; | sed 's/^/   - \//'
    fi
else
    echo "🤖 Auto-generated Commands: 0"
fi

echo ""

# Check for pending rules
PENDING_FILE="$RULECRAFTER_DIR/storage/pending_rules.json"
if [[ -f "$PENDING_FILE" ]]; then
    PENDING_COUNT=$(python3 -c "
import json
try:
    with open('$PENDING_FILE', 'r') as f:
        data = json.load(f)
    print(len([r for r in data if r.get('status') == 'pending']))
except:
    print(0)
" 2>/dev/null || echo "0")
    echo "⏳ Pending Rules: $PENDING_COUNT"
    if [[ $PENDING_COUNT -gt 0 ]]; then
        echo "   Use /rulecrafter-review to approve or reject"
    fi
else
    echo "⏳ Pending Rules: 0"
fi

echo ""

# Check CLAUDE.md for adaptive rules
CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"
if [[ -f "$CLAUDE_MD" ]] && grep -q "RuleCrafter Adaptive Rules" "$CLAUDE_MD"; then
    RULE_COUNT=$(grep -c "^- " "$CLAUDE_MD" | head -1)
    echo "📝 Active Rules in CLAUDE.md: Rules section present"
else
    echo "📝 Active Rules in CLAUDE.md: Not initialized"
fi

echo ""

# System health checks
echo "🔧 System Health:"

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "   ✅ Python 3 available"
else
    echo "   ❌ Python 3 not found (required for analysis)"
fi

# Check if hooks are executable
if [[ -x "$RULECRAFTER_DIR/hooks/pre_tool_analyzer.sh" ]]; then
    echo "   ✅ Pre-tool hook ready"
else
    echo "   ❌ Pre-tool hook not executable"
fi

if [[ -x "$RULECRAFTER_DIR/hooks/post_tool_learner.sh" ]]; then
    echo "   ✅ Post-tool hook ready"
else
    echo "   ❌ Post-tool hook not executable"
fi

# Check git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "   ✅ Git repository detected"
else
    echo "   ⚠️  Not a git repository (git patterns disabled)"
fi

echo ""
echo "💡 Available Commands:"
echo "   /rulecrafter-status    - Show this status"
echo "   /rulecrafter-mine      - Trigger immediate analysis"
echo "   /rulecrafter-review    - Review pending suggestions"
echo ""
echo "🔗 Hook Registration:"
echo "   Configure hooks in Claude Code with: /hooks"
echo "   Pre-tool: $RULECRAFTER_DIR/hooks/pre_tool_analyzer.sh"
echo "   Post-tool: $RULECRAFTER_DIR/hooks/post_tool_learner.sh"
```

*This command is part of RuleCrafter's management interface*
