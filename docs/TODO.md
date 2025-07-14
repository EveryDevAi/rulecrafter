# RuleCrafter TODO

## Multi-Location Memory System Implementation

### Current Issue
RuleCrafter currently learns from ALL user interactions and puts everything into the project-level `CLAUDE.md` file. This creates two problems:

1. **Too broad learning scope** - We're capturing personal habits that should stay private
2. **Wrong memory location** - Personal preferences end up in team-shared project memory

### Proposed Solution: Three-Location Memory System

Based on Claude Code's official memory locations:

#### 1. Project Memory (`./CLAUDE.md`)
- **Purpose**: Team-shared instructions for the project
- **What should go here**: 
  - Universal development patterns (e.g., "Run tests frequently during development")
  - Project-specific coding standards
  - Architecture decisions
  - Workflow patterns that benefit the whole team

#### 2. User Memory (`~/.claude/CLAUDE.md`)
- **Purpose**: Personal preferences for all projects
- **What should go here**:
  - Personal coding style preferences
  - Individual tool shortcuts
  - Personal debugging approaches
  - Private workflow habits

#### 3. Project Memory Local (`./CLAUDE.local.md`) - *Deprecated but noted*
- Claude Code documentation shows this is deprecated
- We should avoid using this location

### Implementation Tasks

#### Phase 1: Smart Classification
- [ ] Update analyzers to classify patterns as "personal" vs "team-relevant"
- [ ] Add logic to determine which memory location patterns should go to
- [ ] Create classification criteria:
  - **Team patterns**: Error handling, testing workflows, build processes
  - **Personal patterns**: Code formatting preferences, personal shortcuts, debugging style

#### Phase 2: Multi-Location Rule Generation
- [ ] Update `rule_generator.py` to support multiple output locations
- [ ] Modify CLI to initialize both project and user memory files
- [ ] Add user memory file management (`~/.claude/CLAUDE.md`)
- [ ] Update rule confidence scoring based on pattern scope

#### Phase 3: Enhanced Filtering
- [ ] Improve pattern filtering to be more selective about what we learn
- [ ] Add privacy-aware learning (skip sensitive/personal information)
- [ ] Implement pattern categorization (workflow, style, architecture, etc.)
- [ ] Add user controls for what types of patterns to learn

#### Phase 4: CLI Updates
- [ ] Update `rulecrafter init` to set up both memory locations
- [ ] Add `rulecrafter status` support for multi-location reporting
- [ ] Create commands to manage user vs project rules separately
- [ ] Add migration tool for existing single-location installations

### Benefits of Multi-Location System
- **Privacy**: Personal habits stay in user memory
- **Collaboration**: Only universally beneficial patterns in project memory
- **Flexibility**: Users can have different personal preferences while sharing project standards
- **Compliance**: Follows Claude Code's official memory system design

### Research Notes
- Claude Code automatically loads all memory files (project + user)
- User memory is in `~/.claude/CLAUDE.md` (personal across all projects)
- Project memory is in `./CLAUDE.md` (team-shared for this project)
- All memory files are automatically loaded into context when Claude Code launches

### Priority
- **Medium-High**: This addresses core privacy and collaboration concerns
- **Dependencies**: None - can be implemented independently
- **Impact**: Significant improvement to user experience and team adoption

---

## Other TODOs

### Documentation
- [ ] Create comprehensive README with examples
- [ ] Add troubleshooting guide
- [ ] Document pattern classification logic

### Testing
- [ ] Add unit tests for pattern analyzers
- [ ] Create integration tests for multi-location system
- [ ] Test migration scenarios

### Performance
- [ ] Optimize pattern storage and retrieval
- [ ] Add pattern cleanup/archiving for old projects
- [ ] Implement smart caching for frequently accessed patterns
