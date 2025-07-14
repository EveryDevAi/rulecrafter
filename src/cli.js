#!/usr/bin/env node

const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const packageJson = require('../package.json');

program
  .name('rulecrafter')
  .description('RuleCrafter - Adaptive automation system that learns from your development patterns')
  .version(packageJson.version);

program
  .command('init')
  .description('Initialize RuleCrafter in the current project')
  .option('-f, --force', 'Overwrite existing installation')
  .action(async (options) => {
    console.log('🚀 Initializing RuleCrafter...');
    
    const currentDir = process.cwd();
    const claudeDir = path.join(currentDir, '.claude');
    const rulecrafterDir = path.join(claudeDir, 'rulecrafter');
    
    // Check if already initialized
    if (fs.existsSync(rulecrafterDir) && !options.force) {
      console.log('❌ RuleCrafter is already initialized in this project.');
      console.log('   Use --force to overwrite the existing installation.');
      return;
    }
    
    try {
      // Create .claude directory if it doesn't exist
      if (!fs.existsSync(claudeDir)) {
        fs.mkdirSync(claudeDir, { recursive: true });
      }
      
      // Copy template structure
      const templateDir = path.join(__dirname, '..', 'templates', '.claude');
      copyDirectory(templateDir, claudeDir);
      
      // Make hook scripts executable
      const hooksDir = path.join(rulecrafterDir, 'hooks');
      if (fs.existsSync(hooksDir)) {
        const hookFiles = fs.readdirSync(hooksDir);
        hookFiles.forEach(file => {
          if (file.endsWith('.sh')) {
            const filePath = path.join(hooksDir, file);
            fs.chmodSync(filePath, '755');
          }
        });
      }
      
      // Initialize CLAUDE.md if it doesn't exist
      const claudeMdPath = path.join(currentDir, 'CLAUDE.md');
      if (!fs.existsSync(claudeMdPath)) {
        createInitialClaudeMd(claudeMdPath);
      }
      
      // Auto-generate Claude Code hooks configuration
      const settingsPath = path.join(claudeDir, 'settings.local.json');
      
      const claudeSettings = {
        hooks: {
          PreToolUse: [
            {
              matcher: "*",
              hooks: [
                {
                  type: "command",
                  command: path.join(currentDir, '.claude', 'rulecrafter', 'hooks', 'pre_tool_analyzer.sh')
                }
              ]
            }
          ],
          PostToolUse: [
            {
              matcher: "*",
              hooks: [
                {
                  type: "command", 
                  command: path.join(currentDir, '.claude', 'rulecrafter', 'hooks', 'post_tool_learner.sh')
                }
              ]
            }
          ],
          Stop: [
            {
              matcher: "*",
              hooks: [
                {
                  type: "command",
                  command: path.join(currentDir, '.claude', 'rulecrafter', 'hooks', 'session_compact.sh')
                }
              ]
            }
          ]
        }
      };
      
      fs.writeFileSync(settingsPath, JSON.stringify(claudeSettings, null, 2));
      
      console.log('✅ RuleCrafter initialized successfully!');
      console.log('');
      console.log('📁 Created structure:');
      console.log('   .claude/rulecrafter/     - Core system files');
      console.log('   .claude/commands/        - Auto-generated slash commands');
      console.log('   .claude/settings.local.json - Auto-configured hooks');
      console.log('   CLAUDE.md               - Project memory (if not exists)');
      console.log('');
      console.log('🎯 Setup complete! Claude Code hooks are automatically configured.');
      console.log('');
      console.log('🚀 To start using RuleCrafter:');
      console.log('   1. Start Claude Code in this project: claude');
      console.log('   2. Begin coding normally - RuleCrafter learns automatically!');
      console.log('');
      console.log('🔍 Verify hooks: rulecrafter verify-hooks');
      
    } catch (error) {
      console.error('❌ Failed to initialize RuleCrafter:', error.message);
      process.exit(1);
    }
  });

program
  .command('status')
  .description('Show RuleCrafter status for the current project')
  .action(() => {
    const currentDir = process.cwd();
    const rulecrafterDir = path.join(currentDir, '.claude', 'rulecrafter');
    
    if (!fs.existsSync(rulecrafterDir)) {
      console.log('❌ RuleCrafter is not initialized in this project.');
      console.log('   Run: rulecrafter init');
      return;
    }
    
    console.log('📊 RuleCrafter Status');
    console.log('===================');
    
    // Check for patterns file
    const patternsPath = path.join(rulecrafterDir, 'storage', 'patterns.json');
    if (fs.existsSync(patternsPath)) {
      try {
        const patterns = JSON.parse(fs.readFileSync(patternsPath, 'utf8'));
        console.log(`📈 Patterns collected: ${Object.keys(patterns.commands || {}).length} commands`);
        console.log(`🐛 Errors tracked: ${Object.keys(patterns.errors || {}).length} error types`);
      } catch (error) {
        console.log('⚠️  Patterns file exists but is invalid');
      }
    } else {
      console.log('📈 No patterns collected yet');
    }
    
    // Check for auto-generated commands
    const autoGenDir = path.join(currentDir, '.claude', 'commands', 'auto-generated');
    if (fs.existsSync(autoGenDir)) {
      const commands = fs.readdirSync(autoGenDir).filter(f => f.endsWith('.md'));
      console.log(`🤖 Auto-generated commands: ${commands.length}`);
      if (commands.length > 0) {
        commands.forEach(cmd => {
          console.log(`   - /${cmd.replace('.md', '')}`);
        });
      }
    } else {
      console.log('🤖 No auto-generated commands yet');
    }
    
    console.log('');
    
    // Quick hook validation
    const hooksDir = path.join(rulecrafterDir, 'hooks');
    const hookFiles = ['pre_tool_analyzer.sh', 'post_tool_learner.sh', 'session_compact.sh'];
    const validHooks = hookFiles.filter(file => {
      const hookPath = path.join(hooksDir, file);
      try {
        fs.accessSync(hookPath, fs.constants.X_OK);
        return true;
      } catch {
        return false;
      }
    });
    
    if (validHooks.length === hookFiles.length) {
      console.log('🪝 Hooks: Ready (run "rulecrafter verify-hooks" for details)');
    } else {
      console.log('⚠️  Hooks: Need configuration (run "rulecrafter verify-hooks")');
    }
    
    console.log('✅ System is ready and learning from your workflow');
  });

program
  .command('clean')
  .description('Remove RuleCrafter from the current project')
  .option('-y, --yes', 'Skip confirmation prompt')
  .action(async (options) => {
    const currentDir = process.cwd();
    const rulecrafterDir = path.join(currentDir, '.claude', 'rulecrafter');
    
    if (!fs.existsSync(rulecrafterDir)) {
      console.log('❌ RuleCrafter is not installed in this project.');
      return;
    }
    
    if (!options.yes) {
      const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
      });
      
      const answer = await new Promise(resolve => {
        readline.question('🗑️  Remove RuleCrafter? This will delete all learned patterns. (y/N): ', resolve);
      });
      readline.close();
      
      if (answer.toLowerCase() !== 'y') {
        console.log('Cancelled.');
        return;
      }
    }
    
    try {
      // Remove rulecrafter directory
      fs.rmSync(rulecrafterDir, { recursive: true, force: true });
      
      // Remove auto-generated commands
      const autoGenDir = path.join(currentDir, '.claude', 'commands', 'auto-generated');
      if (fs.existsSync(autoGenDir)) {
        fs.rmSync(autoGenDir, { recursive: true, force: true });
      }
      
      console.log('✅ RuleCrafter removed successfully');
      console.log('');
      console.log('� Manual cleanup required in Claude Code:');
      console.log('   1. Type "/hooks" in Claude Code');
      console.log('   2. Remove these RuleCrafter hooks:');
      console.log('      - RuleCrafter Pre-Tool Analyzer');
      console.log('      - RuleCrafter Post-Tool Learner');
      console.log('      - RuleCrafter Session Compact');
      console.log('');
      console.log('💡 Or edit .claude/settings.json manually to remove hook entries');
      
    } catch (error) {
      console.error('❌ Failed to remove RuleCrafter:', error.message);
      process.exit(1);
    }
  });

program
  .command('verify-hooks')
  .description('Verify that RuleCrafter hooks are properly configured in Claude Code')
  .action(() => {
    const currentDir = process.cwd();
    const rulecrafterDir = path.join(currentDir, '.claude', 'rulecrafter');
    
    if (!fs.existsSync(rulecrafterDir)) {
      console.log('❌ RuleCrafter is not initialized in this project.');
      console.log('   Run: rulecrafter init');
      return;
    }
    
    console.log('🔍 Verifying RuleCrafter Hook Configuration');
    console.log('==========================================');
    
    // Check if hook scripts exist and are executable
    const hooks = [
      'pre_tool_analyzer.sh',
      'post_tool_learner.sh', 
      'session_compact.sh'
    ];
    
    const hooksDir = path.join(rulecrafterDir, 'hooks');
    let allHooksValid = true;
    
    hooks.forEach(hookFile => {
      const hookPath = path.join(hooksDir, hookFile);
      if (fs.existsSync(hookPath)) {
        try {
          fs.accessSync(hookPath, fs.constants.X_OK);
          console.log(`✅ ${hookFile} - exists and executable`);
        } catch (error) {
          console.log(`⚠️  ${hookFile} - exists but not executable`);
          console.log(`   Fix with: chmod +x "${hookPath}"`);
          allHooksValid = false;
        }
      } else {
        console.log(`❌ ${hookFile} - missing`);
        allHooksValid = false;
      }
    });
    
    console.log('');
    
    // Check Claude Code settings file for hooks
    const settingsPath = path.join(currentDir, '.claude', 'settings.local.json');
    
    let foundSettings = false;
    let hooksConfigured = false;
    
    if (fs.existsSync(settingsPath)) {
      foundSettings = true;
      console.log(`📁 Found Claude Code settings: settings.local.json`);
      
      try {
        const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
        
        if (settings.hooks) {
          let rulecrafterHookCount = 0;
          
          // Check each hook type (PreToolUse, PostToolUse, Stop)
          for (const hookType of ['PreToolUse', 'PostToolUse', 'Stop']) {
            if (settings.hooks[hookType]) {
              for (const matcher of settings.hooks[hookType]) {
                if (matcher.hooks) {
                  for (const hook of matcher.hooks) {
                    if (hook.command && hook.command.includes('rulecrafter')) {
                      rulecrafterHookCount++;
                    }
                  }
                }
              }
            }
          }
          
          if (rulecrafterHookCount > 0) {
            console.log(`✅ Found ${rulecrafterHookCount} RuleCrafter hooks in settings`);
            hooksConfigured = true;
          }
        }
      } catch (error) {
        console.log(`⚠️  Could not parse settings file: ${error.message}`);
      }
    }
    
    if (!foundSettings) {
      console.log('📁 No Claude Code settings file found');
      console.log('   Run "rulecrafter init" to set up automatic hook configuration');
    }
    
    console.log('');
    console.log('📋 Hook Configuration Summary:');
    if (allHooksValid) {
      console.log('✅ All hook scripts are ready');
    } else {
      console.log('❌ Some hook scripts need attention');
    }
    
    if (hooksConfigured) {
      console.log('✅ Hooks are configured in Claude Code');
    } else {
      console.log('⚠️  Hooks may not be configured in Claude Code yet');
      console.log('   Run "rulecrafter init" to set up automatic hook configuration');
    }
    
    console.log('');
    if (allHooksValid && hooksConfigured) {
      console.log('🎉 RuleCrafter hooks are properly configured!');
    } else {
      console.log('🔧 Next steps:');
      if (!allHooksValid) {
        console.log('   1. Fix hook script permissions');
      }
      if (!hooksConfigured) {
        console.log('   2. Run "rulecrafter init" to set up automatic hook configuration');
      }
    }
  });

// Helper functions
function copyDirectory(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const items = fs.readdirSync(src);
  
  for (const item of items) {
    const srcPath = path.join(src, item);
    const destPath = path.join(dest, item);
    
    const stat = fs.statSync(srcPath);
    
    if (stat.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function createInitialClaudeMd(filePath) {
  const content = `# Project Memory

This file contains project-specific information, coding standards, and preferences for Claude Code.

## Project Overview

<!-- Add your project description here -->

## Coding Standards

<!-- Add your coding standards and conventions here -->

## Common Patterns

<!-- Add frequently used patterns and workflows here -->

## RuleCrafter Adaptive Rules

<!-- This section will be automatically updated by RuleCrafter -->
<!-- DO NOT EDIT THIS SECTION MANUALLY -->

*No adaptive rules generated yet. RuleCrafter will populate this section as it learns from your workflow.*

---

*Generated by RuleCrafter - Learn more at: https://github.com/your-username/rulecrafter*
`;

  fs.writeFileSync(filePath, content);
}

// Parse command line arguments
program.parse();
