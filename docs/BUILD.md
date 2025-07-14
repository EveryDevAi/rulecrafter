# RuleCrafter - Build Guide

## Project Overview

**What we're building:**
RuleCrafter is an intelligent automation system that plugs into any codebase to **automatically learn from developer behavior** and **generate adaptive rules and custom slash commands** for Claude Code. It's essentially a "self-improving project assistant" that:

1. **Observes** - Uses Claude Code hooks to monitor every tool usage, command, error, and pattern
2. **Learns** - Mines patterns from usage history to identify repeated behaviors and common issues  
3. **Adapts** - Auto-generates project rules for `CLAUDE.md` and custom slash commands in `.claude/commands/`
4. **Governs** - Provides user approval workflows for all generated content

**Key Innovation:** Zero-maintenance project guidance that evolves with your team's actual workflow, not static documentation that gets outdated.

## Current Project Status

We're at **Week 1** of the implementation plan - the scaffolding phase. You've already:
- ✅ Created the NPM project with `package.json`
- ✅ Written the comprehensive design document (`PLAN.md`)

## Architecture Overview

### Core Components
```
.claude/
├─ rulecrafter/                  # Main system directory
│  ├─ analyzers/
│  │   ├─ context_analyzer.py    # Scans codebase & git diff
│  │   └─ convo_analyzer.py      # Parses session JSON logs
│  ├─ generators/
│  │   ├─ rule_generator.py      # Writes/upserts Markdown blocks
│  │   └─ cmd_builder.py         # Emits *.md command templates
│  ├─ storage/
│  │   └─ patterns.json          # Learned stats (freq, confidence)
│  ├─ hooks/
│  │   ├─ pre_tool_analyzer.sh   # Run before every Claude tool call
│  │   ├─ post_tool_learner.sh   # Run after tool success
│  │   └─ session_compact.sh     # Run on /stop to summarise convo
│  └─ config/
│      └─ settings.json          # System configuration
├─ commands/auto-generated/      # Emergent slash commands
└─ memory/adaptive_rules.md      # Machine-authored rule section
```

### Execution Flow
1. **Hook trigger** – `pre_tool_analyzer.sh` pipes recent diff/prompt to `context_analyzer.py`
2. **Pattern mining** – Scripts update `patterns.json` (command usage counts, error regexes, review phrases)
3. **Periodic learner** – `post_tool_learner.sh` invokes Claude Code non-interactive for analysis
4. **Generators** parse results and write/patch adaptive rules and commands
5. **User notification** – System notifies user of suggestions; user can accept or revert

## Technical Stack

### Languages & Tools
- **Python** - Core analyzers and generators (pattern mining, rule generation)
- **Shell Scripts** - Hook integration points with Claude Code
- **JSON** - Pattern storage and configuration
- **Markdown** - Rule templates and slash command definitions

### Claude Code Features Leveraged
- **Hooks System** - Entry point for automation (PreToolUse, PostToolUse, Stop, Notification)
- **Slash Commands** - Auto-generated workflow shortcuts
- **Memory System** - Dynamic updates to `CLAUDE.md` with learned rules
- **SDK/CLI** - Non-interactive analysis and generation
- **Extended Thinking** - Deep reasoning for better rule generation

## Implementation Plan

### Phase 1: Scaffolding (Current)
- [x] Project structure creation
- [ ] Core directory hierarchy
- [ ] Basic Python modules (analyzers, generators)
- [ ] Hook shell scripts
- [ ] Initial configuration system
- [ ] Bootstrap slash commands

### Phase 2: Integration (Next)
- [ ] Hook registration with Claude Code
- [ ] Basic pattern mining algorithms
- [ ] Rule generation logic
- [ ] Command template system
- [ ] User approval workflows

### Phase 3: Intelligence (Future)
- [ ] Advanced pattern recognition
- [ ] Confidence scoring
- [ ] Conflict resolution
- [ ] Cross-project learning (MCP integration)

## Installation Approach

**Target User Experience:**
```bash
# Install globally
npm install -g rulecrafter

# Initialize in any project
cd /path/to/project
rulecrafter init

# System is now active and learning
# Claude reports: "Adaptive system active; first analysis in 10 runs."
```

## Safety & Governance

- **Confidence Thresholds** - Draft rules in `adaptive_rules_pending.md` until approved
- **User Approval** - All suggestions require explicit user acceptance
- **Conflict Resolution** - Merges auto-generated content with hand-written rules
- **Opt-in Scopes** - User vs project level configuration via environment variables

## Development Workflow

### Local Development
1. **Module Linking** - Use `pnpm link --global` for local development
2. **Build Process** - TypeScript compilation and Python packaging
3. **Testing** - Integration tests with actual Claude Code workflows
4. **Documentation** - Auto-generated API docs and user guides

### Key Milestones
1. **Week 1** - Complete scaffolding and basic structure
2. **Week 2** - Hook integration and basic logging
3. **Week 3-4** - Pattern mining and rule generation prototype
4. **Week 5** - Auto slash-command builder
5. **Week 6** - User approval workflows
6. **Week 7** - Optional MCP integration
7. **Week 8** - Polish, documentation, and distribution

## Success Metrics

### Technical Goals
- [ ] Hooks successfully intercept 100% of Claude Code tool usage
- [ ] Pattern mining accurately identifies repeated behaviors (>90% precision)
- [ ] Rule generation creates actionable, relevant guidance
- [ ] User approval workflow has <30s interaction time

### User Experience Goals
- [ ] Zero-friction installation (`npx rulecrafter-init` and done)
- [ ] Invisible operation (no performance impact on Claude Code)
- [ ] Valuable suggestions (users accept >60% of generated rules)
- [ ] Self-improving guidance (rules become more relevant over time)

## Questions for Implementation

1. **Language Preference**: Confirmed Python for analyzers/generators - good for text processing and ML-like pattern recognition
2. **Installation Approach**: Global NPM tool with per-project initialization - aligns with the plan
3. **Scope**: Starting with full architecture but building incrementally - allows for early testing and feedback

## Next Steps

1. Create the complete directory structure
2. Implement core Python modules with basic functionality
3. Set up hook shell scripts for Claude Code integration
4. Create initial configuration and settings system
5. Build bootstrap slash commands for system management
6. Test hook registration and basic pattern collection

Let's build this! 🚀
