# rulecrafter-setup

Helper command to streamline RuleCrafter hook configuration.

## Usage

```
/rulecrafter-setup
```

## Description

This command provides step-by-step guidance for setting up RuleCrafter hooks in Claude Code.

## Implementation

```bash
#!/bin/bash

# RuleCrafter Setup Helper
echo "🚀 RuleCrafter Hook Setup Helper"
echo "================================"
echo ""

# Get current directory
PROJECT_DIR=$(pwd)
HOOKS_DIR="$PROJECT_DIR/.claude/rulecrafter/hooks"

# Check if RuleCrafter is initialized
if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ RuleCrafter not found in this project"
    echo "   Run: rulecrafter init"
    exit 1
fi

echo "📋 Copy these paths for Claude Code hook configuration:"
echo ""
echo "1. Type '/hooks' in Claude Code"
echo "2. Add these three hooks:"
echo ""
echo "Hook 1 - PreToolUse:"
echo "   Name: RuleCrafter Pre-Tool Analyzer"
echo "   Path: $HOOKS_DIR/pre_tool_analyzer.sh"
echo ""
echo "Hook 2 - PostToolUse:"
echo "   Name: RuleCrafter Post-Tool Learner"  
echo "   Path: $HOOKS_DIR/post_tool_learner.sh"
echo ""
echo "Hook 3 - Stop:"
echo "   Name: RuleCrafter Session Compact"
echo "   Path: $HOOKS_DIR/session_compact.sh"
echo ""
echo "✅ After adding all three hooks, RuleCrafter will begin learning!"
echo ""
echo "🔍 Use 'rulecrafter verify-hooks' to check configuration"
```
