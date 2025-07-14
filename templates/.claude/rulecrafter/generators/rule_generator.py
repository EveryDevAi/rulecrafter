#!/usr/bin/env python3
"""
Rule Generator for RuleCrafter
Generates and updates rules in CLAUDE.md based on learned patterns.
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class RuleGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rulecrafter_dir = self.project_root / '.claude' / 'rulecrafter'
        self.storage_dir = self.rulecrafter_dir / 'storage'
        self.patterns_file = self.storage_dir / 'patterns.json'
        self.claude_md = self.project_root / 'CLAUDE.md'
        
        # Rule generation thresholds
        self.error_threshold = 3  # Generate rule after 3+ occurrences
        self.command_threshold = 5  # Generate rule after 5+ usages
        self.confidence_threshold = 0.7  # Minimum confidence for auto-generation
    
    def load_patterns(self) -> Dict[str, Any]:
        """Load patterns from storage."""
        if not self.patterns_file.exists():
            return {}
        
        try:
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    
    def analyze_error_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze error patterns and generate rule suggestions."""
        rules = []
        errors = patterns.get('errors', {})
        
        for error_key, count in errors.items():
            if count >= self.error_threshold:
                error_type, message = error_key.split(':', 1)
                rule = self._generate_error_rule(error_type, message, count)
                if rule:
                    rules.append(rule)
        
        return rules
    
    def _generate_error_rule(self, error_type: str, message: str, count: int) -> Optional[Dict[str, Any]]:
        """Generate a specific rule based on error pattern."""
        rule_templates = {
            'typescript_error': {
                'TS2322': "- Always provide explicit type annotations when TypeScript cannot infer types correctly.",
                'TS2345': "- Ensure function arguments match the expected parameter types exactly.",
                'TS2339': "- Verify property names and consider using optional chaining (?.) for potentially undefined objects.",
                'TS2304': "- Import all required types and modules before using them.",
                'TS2571': "- Use type assertions (as Type) only when you're certain about the type.",
            },
            'syntax_error': {
                'default': "- Review syntax carefully and use proper linting tools to catch errors early."
            },
            'type_error': {
                'default': "- Add type checking and validation for function parameters and return values."
            },
            'eslint_error': {
                'default': "- Follow ESLint rules consistently and configure auto-fix for common issues."
            },
            'npm_error': {
                'default': "- Clear npm cache and node_modules when encountering persistent package issues."
            },
            'test_failure': {
                'default': "- Review test assertions and ensure test data matches expected formats."
            },
            'module_not_found': {
                'default': "- Verify import paths are correct and all dependencies are installed."
            },
            'permission_error': {
                'default': "- Check file permissions and ensure the user has appropriate access rights."
            }
        }
        
        # Extract specific error code or use default
        error_code = None
        if error_type == 'typescript_error':
            ts_match = re.search(r'TS(\d+)', message)
            if ts_match:
                error_code = f"TS{ts_match.group(1)}"
        
        # Get rule template
        template_group = rule_templates.get(error_type, {})
        rule_text = template_group.get(error_code) or template_group.get('default')
        
        if rule_text:
            return {
                'type': 'error_prevention',
                'category': error_type.replace('_', ' ').title(),
                'rule': rule_text,
                'evidence': {
                    'error_type': error_type,
                    'message': message[:100],  # Truncate long messages
                    'occurrences': count
                },
                'confidence': min(0.9, count / 10.0),  # Higher confidence with more occurrences
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def analyze_command_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze command usage patterns and generate workflow rules."""
        rules = []
        commands = patterns.get('commands', {})
        conversations = patterns.get('conversations', {})
        
        # Analyze frequent command usage
        for command, count in commands.items():
            if count >= self.command_threshold:
                rule = self._generate_workflow_rule(command, count, conversations)
                if rule:
                    rules.append(rule)
        
        # Analyze file type patterns
        file_types = patterns.get('file_types', {})
        if file_types:
            rule = self._generate_file_pattern_rule(file_types)
            if rule:
                rules.append(rule)
        
        return rules
    
    def _generate_workflow_rule(self, command: str, count: int, conversations: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate workflow rules based on command usage."""
        workflow_templates = {
            '/test': "- Run tests frequently during development to catch issues early.",
            '/review': "- Use code review commands to maintain quality standards.",
            '/build': "- Build the project after significant changes to verify compilation.",
            '/lint': "- Run linting before committing code to maintain consistency.",
            '/format': "- Apply consistent formatting across the codebase.",
            '/docs': "- Keep documentation updated alongside code changes.",
            '/deploy': "- Follow deployment procedures and verify in staging first.",
            '/debug': "- Use systematic debugging approaches to isolate issues.",
            '/optimize': "- Profile before optimizing to identify actual bottlenecks.",
            '/refactor': "- Refactor in small, testable increments.",
        }
        
        rule_text = workflow_templates.get(command)
        if rule_text:
            return {
                'type': 'workflow',
                'category': 'Development Process',
                'rule': rule_text,
                'evidence': {
                    'command': command,
                    'usage_count': count
                },
                'confidence': min(0.8, count / 20.0),
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _generate_file_pattern_rule(self, file_types: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """Generate rules based on file type patterns."""
        total_changes = sum(file_types.values())
        if total_changes < 5:
            return None
        
        # Identify dominant file types
        dominant_types = {k: v for k, v in file_types.items() if v / total_changes > 0.3}
        
        if '.ts' in dominant_types or '.tsx' in dominant_types:
            return {
                'type': 'technology_specific',
                'category': 'TypeScript',
                'rule': "- Use strict TypeScript configuration and enable all recommended compiler options.",
                'evidence': {
                    'file_types': dominant_types,
                    'total_changes': total_changes
                },
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
        elif '.py' in dominant_types:
            return {
                'type': 'technology_specific',
                'category': 'Python',
                'rule': "- Follow PEP 8 style guidelines and use type hints for better code clarity.",
                'evidence': {
                    'file_types': dominant_types,
                    'total_changes': total_changes
                },
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
        elif '.js' in dominant_types or '.jsx' in dominant_types:
            return {
                'type': 'technology_specific',
                'category': 'JavaScript',
                'rule': "- Use ESLint and Prettier for consistent code formatting and quality.",
                'evidence': {
                    'file_types': dominant_types,
                    'total_changes': total_changes
                },
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def generate_rules(self) -> List[Dict[str, Any]]:
        """Generate all rules based on current patterns."""
        patterns = self.load_patterns()
        if not patterns:
            return []
        
        rules = []
        
        # Generate error-based rules
        error_rules = self.analyze_error_patterns(patterns)
        rules.extend(error_rules)
        
        # Generate workflow rules
        workflow_rules = self.analyze_command_patterns(patterns)
        rules.extend(workflow_rules)
        
        # Filter by confidence threshold
        high_confidence_rules = [
            rule for rule in rules 
            if rule.get('confidence', 0) >= self.confidence_threshold
        ]
        
        return high_confidence_rules
    
    def format_rules_for_markdown(self, rules: List[Dict[str, Any]]) -> str:
        """Format rules as markdown for insertion into CLAUDE.md."""
        if not rules:
            return "*No adaptive rules generated yet. RuleCrafter will populate this section as it learns from your workflow.*"
        
        formatted = []
        
        # Group rules by category
        categories = {}
        for rule in rules:
            category = rule.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(rule)
        
        # Format each category
        for category, category_rules in categories.items():
            formatted.append(f"\n### {category}\n")
            
            for rule in category_rules:
                rule_text = rule.get('rule', '')
                confidence = rule.get('confidence', 0)
                occurrences = rule.get('evidence', {}).get('occurrences', 0) or rule.get('evidence', {}).get('usage_count', 0)
                
                formatted.append(rule_text)
                
                if occurrences > 0:
                    formatted.append(f"  *Generated from {occurrences} occurrences (confidence: {confidence:.1%})*")
                else:
                    formatted.append(f"  *Confidence: {confidence:.1%}*")
                
                formatted.append("")  # Empty line
        
        formatted.append(f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        formatted.append(f"*Generated by RuleCrafter - {len(rules)} adaptive rules*")
        
        return "\n".join(formatted)
    
    def update_claude_md(self, rules: List[Dict[str, Any]]) -> bool:
        """Update CLAUDE.md with new rules."""
        try:
            # Read existing CLAUDE.md or create if it doesn't exist
            if self.claude_md.exists():
                with open(self.claude_md, 'r') as f:
                    content = f.read()
            else:
                content = self._create_initial_claude_md()
            
            # Find the RuleCrafter section
            section_start = "## RuleCrafter Adaptive Rules"
            section_end = "---"
            
            start_idx = content.find(section_start)
            if start_idx == -1:
                # Add the section at the end
                content += f"\n\n{section_start}\n\n"
                content += self.format_rules_for_markdown(rules)
                content += f"\n\n{section_end}\n"
            else:
                # Find the end of the section
                end_search_start = start_idx + len(section_start)
                end_idx = content.find(section_end, end_search_start)
                
                if end_idx == -1:
                    # No end marker found, replace to end of file
                    new_content = content[:start_idx] + section_start + "\n\n"
                    new_content += self.format_rules_for_markdown(rules)
                    new_content += f"\n\n{section_end}\n"
                else:
                    # Replace the section content
                    new_content = content[:start_idx] + section_start + "\n\n"
                    new_content += self.format_rules_for_markdown(rules)
                    new_content += f"\n\n{content[end_idx:]}"
                
                content = new_content
            
            # Write updated content
            with open(self.claude_md, 'w') as f:
                f.write(content)
            
            return True
            
        except OSError as e:
            print(f"Error updating CLAUDE.md: {e}", file=sys.stderr)
            return False
    
    def _create_initial_claude_md(self) -> str:
        """Create initial CLAUDE.md content."""
        return """# Project Memory

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

*Generated by RuleCrafter*
"""
    
    def save_pending_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """Save rules that need user approval."""
        try:
            pending_file = self.rulecrafter_dir / 'storage' / 'pending_rules.json'
            
            # Load existing pending rules
            if pending_file.exists():
                with open(pending_file, 'r') as f:
                    existing_rules = json.load(f)
            else:
                existing_rules = []
            
            # Add new rules with approval status
            for rule in rules:
                rule['status'] = 'pending'
                rule['generated_at'] = datetime.now().isoformat()
                existing_rules.append(rule)
            
            # Save updated pending rules
            with open(pending_file, 'w') as f:
                json.dump(existing_rules, f, indent=2)
            
            return True
            
        except OSError as e:
            print(f"Error saving pending rules: {e}", file=sys.stderr)
            return False
    
    def generate_and_update_rules(self, auto_approve: bool = False) -> Tuple[int, int]:
        """Generate rules and update CLAUDE.md. Returns (generated_count, approved_count)."""
        rules = self.generate_rules()
        
        if not rules:
            return 0, 0
        
        if auto_approve:
            # Auto-approve high-confidence rules
            approved_rules = [rule for rule in rules if rule.get('confidence', 0) >= 0.9]
            pending_rules = [rule for rule in rules if rule.get('confidence', 0) < 0.9]
            
            if approved_rules:
                self.update_claude_md(approved_rules)
            
            if pending_rules:
                self.save_pending_rules(pending_rules)
            
            return len(rules), len(approved_rules)
        else:
            # Save all rules as pending
            self.save_pending_rules(rules)
            return len(rules), 0

def main():
    """Main entry point when called as a script."""
    if len(sys.argv) < 2:
        print("Usage: python rule_generator.py <project_root> [--auto-approve]")
        sys.exit(1)
    
    project_root = sys.argv[1]
    auto_approve = '--auto-approve' in sys.argv
    
    generator = RuleGenerator(project_root)
    generated, approved = generator.generate_and_update_rules(auto_approve=auto_approve)
    
    result = {
        'generated_rules': generated,
        'approved_rules': approved,
        'pending_rules': generated - approved,
        'timestamp': datetime.now().isoformat()
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
