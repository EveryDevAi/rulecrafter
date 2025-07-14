#!/usr/bin/env python3
"""
Command Builder for RuleCrafter
Generates custom slash commands based on learned usage patterns.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class CommandBuilder:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rulecrafter_dir = self.project_root / '.claude' / 'rulecrafter'
        self.storage_dir = self.rulecrafter_dir / 'storage'
        self.patterns_file = self.storage_dir / 'patterns.json'
        self.commands_dir = self.project_root / '.claude' / 'commands' / 'auto-generated'
        
        # Ensure commands directory exists
        self.commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Command generation thresholds
        self.usage_threshold = 10  # Generate command after 10+ similar usages
        self.confidence_threshold = 0.7
    
    def load_patterns(self) -> Dict[str, Any]:
        """Load patterns from storage."""
        if not self.patterns_file.exists():
            return {}
        
        try:
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    
    def analyze_command_opportunities(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns to identify opportunities for new commands."""
        opportunities = []
        
        # Analyze conversation patterns for repeated requests
        conversations = patterns.get('conversations', {})
        if conversations:
            opportunities.extend(self._analyze_conversation_patterns(conversations))
        
        # Analyze tool usage patterns
        file_types = patterns.get('file_types', {})
        if file_types:
            opportunities.extend(self._analyze_file_type_patterns(file_types))
        
        # Analyze error patterns for debugging commands
        errors = patterns.get('errors', {})
        if errors:
            opportunities.extend(self._analyze_error_patterns(errors))
        
        # Analyze git patterns for workflow commands
        git_patterns = patterns.get('git_patterns', {})
        files_changed = patterns.get('files_changed', {})
        if files_changed:
            opportunities.extend(self._analyze_git_patterns(files_changed))
        
        return opportunities
    
    def _analyze_conversation_patterns(self, conversations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze conversation patterns for command opportunities."""
        opportunities = []
        
        last_session = conversations.get('last_session_patterns', {})
        prompt_categories = last_session.get('prompt_categories', {})
        
        # Testing patterns
        if prompt_categories.get('testing', 0) >= 5:
            opportunities.append({
                'command_name': 'smart_test',
                'description': 'Run tests with coverage and update snapshots automatically',
                'category': 'testing',
                'template': self._create_test_command_template(),
                'confidence': min(0.9, prompt_categories['testing'] / 10.0),
                'evidence': {'testing_prompts': prompt_categories['testing']}
            })
        
        # Debugging patterns
        if prompt_categories.get('debugging', 0) >= 5:
            opportunities.append({
                'command_name': 'debug_helper',
                'description': 'Systematic debugging workflow with logging and error analysis',
                'category': 'debugging',
                'template': self._create_debug_command_template(),
                'confidence': min(0.9, prompt_categories['debugging'] / 10.0),
                'evidence': {'debugging_prompts': prompt_categories['debugging']}
            })
        
        # Refactoring patterns
        if prompt_categories.get('refactoring', 0) >= 3:
            opportunities.append({
                'command_name': 'safe_refactor',
                'description': 'Refactor code with tests and safety checks',
                'category': 'refactoring',
                'template': self._create_refactor_command_template(),
                'confidence': min(0.8, prompt_categories['refactoring'] / 5.0),
                'evidence': {'refactoring_prompts': prompt_categories['refactoring']}
            })
        
        return opportunities
    
    def _analyze_file_type_patterns(self, file_types: Dict[str, int]) -> List[Dict[str, Any]]:
        """Analyze file type patterns for technology-specific commands."""
        opportunities = []
        total_changes = sum(file_types.values())
        
        if total_changes < 5:
            return opportunities
        
        # TypeScript/JavaScript patterns
        js_ts_files = (file_types.get('.ts', 0) + file_types.get('.tsx', 0) + 
                      file_types.get('.js', 0) + file_types.get('.jsx', 0))
        
        if js_ts_files / total_changes > 0.6:
            opportunities.append({
                'command_name': 'ts_check',
                'description': 'Run TypeScript type checking and fix common issues',
                'category': 'typescript',
                'template': self._create_typescript_command_template(),
                'confidence': 0.8,
                'evidence': {'js_ts_ratio': js_ts_files / total_changes}
            })
        
        # Python patterns
        py_files = file_types.get('.py', 0)
        if py_files / total_changes > 0.6:
            opportunities.append({
                'command_name': 'py_lint',
                'description': 'Run Python linting, formatting, and type checking',
                'category': 'python',
                'template': self._create_python_command_template(),
                'confidence': 0.8,
                'evidence': {'python_ratio': py_files / total_changes}
            })
        
        return opportunities
    
    def _analyze_error_patterns(self, errors: Dict[str, int]) -> List[Dict[str, Any]]:
        """Analyze error patterns for debugging commands."""
        opportunities = []
        
        # Count TypeScript errors
        ts_errors = sum(count for error_key, count in errors.items() 
                       if 'typescript_error' in error_key)
        
        if ts_errors >= 5:
            opportunities.append({
                'command_name': 'fix_ts_errors',
                'description': 'Analyze and fix common TypeScript errors',
                'category': 'debugging',
                'template': self._create_ts_fix_command_template(),
                'confidence': min(0.9, ts_errors / 10.0),
                'evidence': {'typescript_errors': ts_errors}
            })
        
        # Count npm/dependency errors
        npm_errors = sum(count for error_key, count in errors.items() 
                        if 'npm_error' in error_key or 'module_not_found' in error_key)
        
        if npm_errors >= 3:
            opportunities.append({
                'command_name': 'fix_deps',
                'description': 'Fix dependency and module resolution issues',
                'category': 'debugging',
                'template': self._create_deps_fix_command_template(),
                'confidence': min(0.8, npm_errors / 5.0),
                'evidence': {'dependency_errors': npm_errors}
            })
        
        return opportunities
    
    def _analyze_git_patterns(self, files_changed: Dict[str, int]) -> List[Dict[str, Any]]:
        """Analyze git patterns for workflow commands."""
        opportunities = []
        
        # If many files are frequently changed, suggest a commit helper
        frequently_changed = [f for f, count in files_changed.items() if count >= 5]
        
        if len(frequently_changed) >= 3:
            opportunities.append({
                'command_name': 'smart_commit',
                'description': 'Analyze changes and generate meaningful commit messages',
                'category': 'git',
                'template': self._create_commit_command_template(),
                'confidence': 0.7,
                'evidence': {'frequently_changed_files': len(frequently_changed)}
            })
        
        return opportunities
    
    def _create_test_command_template(self) -> str:
        """Create a template for smart test command."""
        return """## smart_test
Run comprehensive test suite with coverage and automatic snapshot updates.

**Usage:** `/smart_test [pattern]`

**Arguments:**
- `pattern` (optional): Test file pattern to run specific tests

**Description:**
Runs the project's test suite with coverage reporting and automatically updates any failing snapshots. Provides a summary of test results and coverage metrics.

**What this command does:**
1. Runs tests with coverage enabled
2. Updates snapshots if needed
3. Reports coverage metrics
4. Highlights any failing tests with suggestions

```bash
# Run all tests with coverage
npm run test -- --coverage --updateSnapshot

# If pattern provided, run specific tests
if [ -n "$1" ]; then
    npm run test -- --testPathPattern="$1" --coverage --updateSnapshot
fi

# Generate coverage report
echo "📊 Test Coverage Summary:"
npm run test:coverage
```

*Auto-generated by RuleCrafter based on testing patterns*
"""
    
    def _create_debug_command_template(self) -> str:
        """Create a template for debug helper command."""
        return """## debug_helper
Systematic debugging workflow with logging and error analysis.

**Usage:** `/debug_helper [error_type]`

**Arguments:**
- `error_type` (optional): Type of error to focus on (ts, npm, test, etc.)

**Description:**
Provides a structured approach to debugging issues with built-in logging and error analysis tools.

**What this command does:**
1. Analyzes recent error logs
2. Suggests debugging strategies
3. Runs diagnostic commands
4. Provides troubleshooting steps

```bash
echo "🔍 Starting debugging session..."

# Analyze recent logs
echo "📋 Recent errors:"
git log --oneline -10 | grep -i "fix\|error\|bug" || echo "No recent error-related commits"

# Check for common issues
echo "🔧 Running diagnostics..."
if [ "$1" = "ts" ]; then
    echo "TypeScript diagnostics:"
    npx tsc --noEmit
elif [ "$1" = "npm" ]; then
    echo "NPM diagnostics:"
    npm doctor
    npm audit
else
    echo "General diagnostics:"
    echo "- Checking dependencies..."
    npm ls --depth=0 | grep MISSING || echo "✅ All dependencies found"
    echo "- Checking TypeScript..."
    npx tsc --noEmit --skipLibCheck
fi
```

*Auto-generated by RuleCrafter based on debugging patterns*
"""
    
    def _create_refactor_command_template(self) -> str:
        """Create a template for safe refactor command."""
        return """## safe_refactor
Refactor code with tests and safety checks.

**Usage:** `/safe_refactor <file_or_directory>`

**Arguments:**
- `file_or_directory`: Target file or directory to refactor

**Description:**
Performs refactoring with built-in safety checks including running tests before and after changes.

**What this command does:**
1. Runs tests to establish baseline
2. Creates a backup of current state
3. Guides through refactoring process
4. Validates changes with tests

```bash
if [ -z "$1" ]; then
    echo "❌ Please specify a file or directory to refactor"
    exit 1
fi

echo "🔄 Starting safe refactoring of: $1"

# Run tests first
echo "🧪 Running tests to establish baseline..."
npm test

if [ $? -ne 0 ]; then
    echo "❌ Tests are failing. Fix tests before refactoring."
    exit 1
fi

# Create backup
echo "💾 Creating backup..."
git stash push -m "Pre-refactor backup: $1"

echo "✅ Ready to refactor. After making changes, run tests again to validate."
echo "💡 To restore backup if needed: git stash pop"
```

*Auto-generated by RuleCrafter based on refactoring patterns*
"""
    
    def _create_typescript_command_template(self) -> str:
        """Create a template for TypeScript checking command."""
        return """## ts_check
Run TypeScript type checking and fix common issues.

**Usage:** `/ts_check [--fix]`

**Arguments:**
- `--fix` (optional): Attempt to auto-fix some TypeScript issues

**Description:**
Comprehensive TypeScript type checking with suggestions for common fixes.

```bash
echo "🔍 Running TypeScript checks..."

# Run type checking
npx tsc --noEmit --skipLibCheck

# If --fix flag is provided, try some automatic fixes
if [ "$1" = "--fix" ]; then
    echo "🔧 Attempting automatic fixes..."
    
    # Fix missing imports (basic approach)
    echo "📦 Checking for missing imports..."
    npx tsc --noEmit 2>&1 | grep "Cannot find name" | while read line; do
        echo "💡 Consider importing: $line"
    done
    
    # Run ESLint with auto-fix
    npx eslint . --ext .ts,.tsx --fix
fi

echo "✅ TypeScript check complete"
```

*Auto-generated by RuleCrafter based on TypeScript usage patterns*
"""
    
    def _create_python_command_template(self) -> str:
        """Create a template for Python linting command."""
        return """## py_lint
Run Python linting, formatting, and type checking.

**Usage:** `/py_lint [--fix]`

**Arguments:**
- `--fix` (optional): Auto-fix formatting and some linting issues

**Description:**
Comprehensive Python code quality checks including formatting, linting, and type checking.

```bash
echo "🐍 Running Python quality checks..."

# Check if required tools are installed
if ! command -v black &> /dev/null; then
    echo "⚠️ black not found. Install with: pip install black"
fi

if ! command -v flake8 &> /dev/null; then
    echo "⚠️ flake8 not found. Install with: pip install flake8"
fi

# Run checks
if [ "$1" = "--fix" ]; then
    echo "🔧 Auto-fixing Python code..."
    black .
    isort .
else
    echo "📋 Checking Python code quality..."
    black --check .
    flake8 .
    
    # Type checking if mypy is available
    if command -v mypy &> /dev/null; then
        mypy .
    fi
fi

echo "✅ Python check complete"
```

*Auto-generated by RuleCrafter based on Python usage patterns*
"""
    
    def _create_ts_fix_command_template(self) -> str:
        """Create a template for TypeScript error fixing command."""
        return """## fix_ts_errors
Analyze and fix common TypeScript errors.

**Usage:** `/fix_ts_errors`

**Description:**
Analyzes TypeScript errors and provides specific fixes for common issues.

```bash
echo "🔧 Analyzing TypeScript errors..."

# Run TypeScript compiler and capture errors
TSC_OUTPUT=$(npx tsc --noEmit 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ No TypeScript errors found!"
    exit 0
fi

echo "❌ Found TypeScript errors:"
echo "$TSC_OUTPUT"

echo ""
echo "💡 Common fixes for TypeScript errors:"
echo "• TS2322 (Type assignment): Add explicit type annotations"
echo "• TS2339 (Property doesn't exist): Check spelling or use optional chaining (?.)"
echo "• TS2345 (Argument type): Verify function parameter types"
echo "• TS2304 (Cannot find name): Add proper imports"

# Suggest specific fixes based on error patterns
echo "$TSC_OUTPUT" | grep "TS2322" > /dev/null && echo "🎯 TS2322 found: Consider adding type annotations"
echo "$TSC_OUTPUT" | grep "TS2339" > /dev/null && echo "🎯 TS2339 found: Check property names and use optional chaining"
echo "$TSC_OUTPUT" | grep "TS2304" > /dev/null && echo "🎯 TS2304 found: Add missing imports"
```

*Auto-generated by RuleCrafter based on TypeScript error patterns*
"""
    
    def _create_deps_fix_command_template(self) -> str:
        """Create a template for dependency fixing command."""
        return """## fix_deps
Fix dependency and module resolution issues.

**Usage:** `/fix_deps`

**Description:**
Diagnoses and fixes common dependency and module resolution problems.

```bash
echo "📦 Fixing dependency issues..."

# Clear npm cache
echo "🧹 Clearing npm cache..."
npm cache clean --force

# Remove node_modules and package-lock
echo "🗑️ Removing node_modules and package-lock.json..."
rm -rf node_modules package-lock.json

# Reinstall dependencies
echo "📥 Reinstalling dependencies..."
npm install

# Check for vulnerabilities
echo "🔒 Checking for security vulnerabilities..."
npm audit

# Fix auto-fixable vulnerabilities
npm audit fix

echo "✅ Dependency fix complete"
echo "💡 If issues persist, check:"
echo "   • Import paths are correct"
echo "   • All required dependencies are in package.json"
echo "   • TypeScript paths are configured correctly"
```

*Auto-generated by RuleCrafter based on dependency error patterns*
"""
    
    def _create_commit_command_template(self) -> str:
        """Create a template for smart commit command."""
        return """## smart_commit
Analyze changes and generate meaningful commit messages.

**Usage:** `/smart_commit [type]`

**Arguments:**
- `type` (optional): Commit type (feat, fix, docs, refactor, test, etc.)

**Description:**
Analyzes current changes and helps generate conventional commit messages.

```bash
echo "📝 Analyzing changes for commit..."

# Show current changes
echo "📋 Current changes:"
git status --short

# Analyze changes to suggest commit type and message
CHANGED_FILES=$(git diff --name-only)
STAGED_FILES=$(git diff --cached --name-only)

if [ -z "$STAGED_FILES" ]; then
    echo "⚠️ No files staged for commit. Stage files first with: git add <files>"
    exit 1
fi

echo ""
echo "📁 Files to be committed:"
echo "$STAGED_FILES"

# Suggest commit type based on changes
if echo "$STAGED_FILES" | grep -q "test\|spec"; then
    SUGGESTED_TYPE="test"
elif echo "$STAGED_FILES" | grep -q "README\|\.md"; then
    SUGGESTED_TYPE="docs"
elif echo "$STAGED_FILES" | grep -q "package\.json\|yarn\.lock\|package-lock\.json"; then
    SUGGESTED_TYPE="chore"
else
    SUGGESTED_TYPE="feat"
fi

COMMIT_TYPE=${1:-$SUGGESTED_TYPE}

echo ""
echo "💡 Suggested commit type: $COMMIT_TYPE"
echo "📝 Generate your commit message following conventional commits:"
echo "   $COMMIT_TYPE: <description>"
echo ""
echo "Example: $COMMIT_TYPE: add user authentication feature"
```

*Auto-generated by RuleCrafter based on git usage patterns*
"""
    
    def create_command_file(self, opportunity: Dict[str, Any]) -> bool:
        """Create a command file from an opportunity."""
        try:
            command_name = opportunity['command_name']
            template = opportunity['template']
            
            command_file = self.commands_dir / f"{command_name}.md"
            
            # Add metadata header
            header = f"""---
# Auto-generated by RuleCrafter
# Generated: {datetime.now().isoformat()}
# Category: {opportunity.get('category', 'general')}
# Confidence: {opportunity.get('confidence', 0):.2f}
# Evidence: {opportunity.get('evidence', {})}
---

"""
            
            with open(command_file, 'w') as f:
                f.write(header + template)
            
            return True
            
        except OSError as e:
            print(f"Error creating command file: {e}", file=sys.stderr)
            return False
    
    def generate_commands(self) -> List[Dict[str, Any]]:
        """Generate commands based on current patterns."""
        patterns = self.load_patterns()
        if not patterns:
            return []
        
        opportunities = self.analyze_command_opportunities(patterns)
        
        # Filter by confidence threshold
        high_confidence_opportunities = [
            opp for opp in opportunities 
            if opp.get('confidence', 0) >= self.confidence_threshold
        ]
        
        return high_confidence_opportunities
    
    def build_and_deploy_commands(self) -> Dict[str, Any]:
        """Generate and deploy new commands."""
        opportunities = self.generate_commands()
        
        created_commands = []
        failed_commands = []
        
        for opportunity in opportunities:
            command_name = opportunity['command_name']
            
            # Check if command already exists
            command_file = self.commands_dir / f"{command_name}.md"
            if command_file.exists():
                continue  # Skip existing commands
            
            if self.create_command_file(opportunity):
                created_commands.append(command_name)
            else:
                failed_commands.append(command_name)
        
        return {
            'created_commands': created_commands,
            'failed_commands': failed_commands,
            'total_opportunities': len(opportunities),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main entry point when called as a script."""
    if len(sys.argv) < 2:
        print("Usage: python cmd_builder.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    
    builder = CommandBuilder(project_root)
    result = builder.build_and_deploy_commands()
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
