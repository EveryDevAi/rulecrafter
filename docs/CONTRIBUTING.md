# Contributing to RuleCrafter

Welcome to RuleCrafter development! This guide will help you set up a local development environment, test changes, and contribute to the project.

## 🛠️ Development Setup

### Prerequisites

- **Node.js** 14+ (we recommend using [nvm](https://github.com/nvm-sh/nvm))
- **Python** 3.6+ (for the analysis scripts)
- **pnpm** (preferred) or npm
- **Git**
- **Claude Code** for testing integration

### Clone and Setup

```bash
# Clone the repository (or if you already have it, just cd into it)
cd /Users/joe/web/packages/rulecrafter

# Install dependencies
pnpm install

# Make the CLI available globally for development
pnpm link --global

# Verify installation works
rulecrafter --version
# Should output: 1.0.0
```

**Note:** If you get a "Cannot find module" error, the issue is likely with the relative path in the CLI script. This should be fixed now.

## 🧪 Local Testing Workflow

### 1. Test the CLI Installation

```bash
# Create a test project directory (NOT in the RuleCrafter repo)
mkdir ~/test-rulecrafter
cd ~/test-rulecrafter

# Initialize a git repo (recommended for pattern detection)
git init
echo "# Test Project" > README.md
git add . && git commit -m "Initial commit"

# Initialize RuleCrafter (this uses the globally linked version)
rulecrafter init

# Verify the structure was created
ls -la .claude/rulecrafter/
```

**Important:** The `rulecrafter` command is now globally available because we linked it from your development directory. When you run `rulecrafter init` in the test project, it copies the template files from your development repo.

You should see:
```
.claude/
├── rulecrafter/
│   ├── analyzers/
│   ├── generators/
│   ├── storage/
│   ├── hooks/
│   └── config/
└── commands/
    ├── rulecrafter-status.md
    ├── rulecrafter-mine.md
    └── rulecrafter-review.md
```

### 2. Test Python Scripts Directly

```bash
cd ~/test-rulecrafter/.claude/rulecrafter

# Test context analyzer
python3 analyzers/context_analyzer.py

# Test conversation analyzer
python3 analyzers/convo_analyzer.py

# Test rule generator
python3 generators/rule_generator.py

# Test command builder
python3 generators/cmd_builder.py
```

### 3. Test Shell Hooks

```bash
cd ~/test-rulecrafter/.claude/rulecrafter

# Make hooks executable
chmod +x hooks/*.sh

# Test pre-tool hook
./hooks/pre_tool_analyzer.sh

# Test post-tool hook
./hooks/post_tool_learner.sh

# Test session compact hook
./hooks/session_compact.sh
```

### 4. Test with Claude Code Integration

1. **Open your test project in Claude Code:**
   ```bash
   cd ~/test-rulecrafter
   code .  # or open with Claude Code directly
   ```

2. **Register the hooks in Claude Code:**
   ```
   /hooks
   ```

3. **Add these hook paths:**
   - **PreToolUse**: `~/test-rulecrafter/.claude/rulecrafter/hooks/pre_tool_analyzer.sh`
   - **PostToolUse**: `~/test-rulecrafter/.claude/rulecrafter/hooks/post_tool_learner.sh`
   - **Stop**: `~/test-rulecrafter/.claude/rulecrafter/hooks/session_compact.sh`

4. **Test the management commands:**
   ```
   /rulecrafter-status
   /rulecrafter-mine --force
   /rulecrafter-review
   ```

## 🔄 Development Workflow

### Making Changes

1. **Edit source files** in the RuleCrafter repository (`/Users/joe/web/packages/rulecrafter/`)
2. **Test locally** using the linked CLI in your test projects
3. **If you change the CLI script** (`src/cli.js`), you may need to re-link:
   ```bash
   cd /Users/joe/web/packages/rulecrafter
   pnpm unlink --global
   pnpm link --global
   ```
4. **If you change template files**, re-initialize your test project:
   ```bash
   cd ~/test-rulecrafter
   rulecrafter clean
   rulecrafter init
   ```

### Testing Changes in Templates

When you modify files in the `templates/` directory, you need to re-initialize in your test project:

```bash
cd ~/test-rulecrafter

# Clean up existing installation
rulecrafter clean

# Re-initialize with updated templates
rulecrafter init
```

### Creating Multiple Test Projects

For testing different scenarios:

```bash
# TypeScript project
mkdir ~/test-ts-project && cd ~/test-ts-project
npm init -y && npm install typescript
rulecrafter init

# Python project
mkdir ~/test-py-project && cd ~/test-py-project
python3 -m venv venv && echo "flask" > requirements.txt
rulecrafter init

# React project
npx create-react-app ~/test-react-project
cd ~/test-react-project
rulecrafter init
```

## 🐛 Debugging

### CLI Linking Issues

```bash
# Check if CLI is properly linked
which rulecrafter
# Should show: /Users/joe/Library/pnpm/global/5/node_modules/.bin/rulecrafter

# If you get "command not found"
cd /Users/joe/web/packages/rulecrafter
pnpm unlink --global
pnpm link --global

# If you get "Cannot find module" errors
# Make sure the package.json path in cli.js is correct (should be '../package.json')

# If you get "no such file or directory, scandir templates" error
# Make sure the templateDir path in cli.js points to '../templates/.claude'

# Test the CLI directly
node /Users/joe/web/packages/rulecrafter/src/cli.js --version
```

### pnpm Link Troubleshooting

If you get symlink errors when linking in other projects:
```bash
# DON'T run this in other projects - the global link is enough
# pnpm link --global rulecrafter  # ❌ Don't do this

# The workflow is:
# 1. Link FROM the development repo (already done)
# 2. Use 'rulecrafter' command anywhere (globally available)
```

### Python Script Issues

```bash
# Test Python environment
python3 --version
python3 -c "import json, os, sys; print('Python environment OK')"

# Check script permissions
ls -la .claude/rulecrafter/hooks/
chmod +x .claude/rulecrafter/hooks/*.sh  # If needed
```

### Hook Integration Issues

```bash
# Test hooks manually
cd .claude/rulecrafter
./hooks/pre_tool_analyzer.sh
echo $?  # Should return 0 for success

# Check Claude Code can execute hooks
# (Run a tool in Claude Code and check for pattern files)
ls -la storage/
cat storage/patterns.json  # Should contain data after tool usage
```

## 📁 Project Structure for Contributors

```
rulecrafter/
├── src/
│   └── cli.js                 # Main CLI entry point
├── templates/                 # Files copied to user projects
│   └── .claude/
│       ├── rulecrafter/       # Core system
│       └── commands/          # Management slash commands
├── package.json              # NPM package configuration
├── README.md                 # User documentation
├── BUILD.md                  # Architecture documentation
├── PLAN.md                   # Original planning document
└── CONTRIBUTING.md           # This file
```

### Key Files to Understand

1. **`src/cli.js`** - Main CLI logic, handles `init`, `status`, `clean` commands
2. **`templates/.claude/rulecrafter/analyzers/`** - Python scripts for pattern analysis
3. **`templates/.claude/rulecrafter/generators/`** - Python scripts for rule/command generation
4. **`templates/.claude/rulecrafter/hooks/`** - Shell scripts for Claude Code integration

## 🧪 Testing Scenarios

### Scenario 1: Error Pattern Learning
1. Create a TypeScript file with intentional errors
2. Use Claude Code to fix them multiple times
3. Check if RuleCrafter generates relevant rules

### Scenario 2: Command Usage Learning
1. Use `/test` command multiple times
2. Run `/rulecrafter-mine --force`
3. Check if a custom test command is generated

### Scenario 3: File Pattern Recognition
1. Work with specific file types (e.g., `.tsx`, `.py`)
2. Make git commits with changes
3. Verify technology-specific rules are generated

## 🚀 Publishing Changes

### Testing Before Release
```bash
# Run all tests in different project types
./scripts/test-all-scenarios.sh  # (You can create this)

# Verify package.json is correct
npm pack --dry-run

# Test installation from tarball
npm pack
cd ~/test-install
npm install ../rulecrafter/rulecrafter-*.tgz
```

### Release Process
1. Update version in `package.json`
2. Update `CHANGELOG.md` (if exists)
3. Tag the release: `git tag v1.0.0`
4. Push: `git push origin main --tags`
5. Publish: `npm publish` (when ready)

## 🤝 Contributing Guidelines

### Code Style
- Use consistent indentation (2 spaces for JS, 4 for Python)
- Add comments for complex logic
- Follow existing patterns in the codebase

### Pull Request Process
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Test your changes thoroughly
4. Update documentation if needed
5. Submit a pull request with clear description

### Issue Reporting
When reporting bugs, include:
- OS and Node.js version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output

## 💡 Development Tips

### Quick Iteration
```bash
# Watch for changes and re-link automatically
# (You can set up nodemon or similar)
nodemon --watch src --exec "pnpm unlink --global && pnpm link --global"
```

### Debugging Python Scripts
```bash
# Add debug prints to Python scripts
echo "DEBUG: Analyzing patterns..." >> analyzers/context_analyzer.py

# Check Python script output
python3 -u analyzers/context_analyzer.py 2>&1 | tee debug.log
```

### Testing Without Claude Code
```bash
# Simulate tool usage for testing
echo '{"tool": "read_file", "args": {"filePath": "test.js"}}' > storage/session_log.txt
python3 generators/rule_generator.py
```

## 📚 Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)
- [Node.js CLI Best Practices](https://github.com/lirantal/nodejs-cli-apps-best-practices)
- [Python JSON Module](https://docs.python.org/3/library/json.html)

---

Happy contributing! 🎉 If you have questions, feel free to open an issue or reach out to the maintainers.
