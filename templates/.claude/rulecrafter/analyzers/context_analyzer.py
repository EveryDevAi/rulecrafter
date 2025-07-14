#!/usr/bin/env python3
"""
Context Analyzer for RuleCrafter
Analyzes codebase context and git diffs to understand project state and changes.
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class ContextAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rulecrafter_dir = self.project_root / '.claude' / 'rulecrafter'
        self.storage_dir = self.rulecrafter_dir / 'storage'
        self.patterns_file = self.storage_dir / 'patterns.json'
        
        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize patterns file if it doesn't exist
        if not self.patterns_file.exists():
            self._initialize_patterns_file()
    
    def _initialize_patterns_file(self):
        """Initialize the patterns.json file with default structure."""
        initial_patterns = {
            "commands": {},
            "errors": {},
            "files_changed": {},
            "git_patterns": {},
            "review_comments": [],
            "last_updated": datetime.now().isoformat(),
            "total_sessions": 0,
            "confidence_scores": {}
        }
        
        with open(self.patterns_file, 'w') as f:
            json.dump(initial_patterns, f, indent=2)
    
    def analyze_git_diff(self) -> Dict[str, Any]:
        """Analyze recent git changes to understand what's being worked on."""
        try:
            # Get unstaged changes
            unstaged = subprocess.run(
                ['git', 'diff', '--name-only'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Get staged changes
            staged = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Get recent commits (last 5)
            recent_commits = subprocess.run(
                ['git', 'log', '--oneline', '-5'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Get current branch
            current_branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return {
                'unstaged_files': unstaged.stdout.strip().split('\n') if unstaged.stdout.strip() else [],
                'staged_files': staged.stdout.strip().split('\n') if staged.stdout.strip() else [],
                'recent_commits': recent_commits.stdout.strip().split('\n') if recent_commits.stdout.strip() else [],
                'current_branch': current_branch.stdout.strip(),
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'error': f"Git analysis failed: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_file_patterns(self, files: List[str]) -> Dict[str, Any]:
        """Analyze patterns in the files being changed."""
        patterns = {
            'file_types': {},
            'directories': {},
            'naming_patterns': [],
            'size_indicators': {}
        }
        
        for file_path in files:
            if not file_path:
                continue
                
            # File extension analysis
            ext = Path(file_path).suffix.lower()
            patterns['file_types'][ext] = patterns['file_types'].get(ext, 0) + 1
            
            # Directory analysis
            directory = str(Path(file_path).parent)
            patterns['directories'][directory] = patterns['directories'].get(directory, 0) + 1
            
            # Check if file exists and analyze it
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    # File size analysis
                    size = full_path.stat().st_size
                    if size < 1000:
                        patterns['size_indicators']['small'] = patterns['size_indicators'].get('small', 0) + 1
                    elif size < 10000:
                        patterns['size_indicators']['medium'] = patterns['size_indicators'].get('medium', 0) + 1
                    else:
                        patterns['size_indicators']['large'] = patterns['size_indicators'].get('large', 0) + 1
                    
                    # Basic content analysis for common patterns
                    if ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                        self._analyze_code_file(full_path, patterns)
                        
                except (OSError, PermissionError):
                    continue
        
        return patterns
    
    def _analyze_code_file(self, file_path: Path, patterns: Dict[str, Any]):
        """Analyze code file for common patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for common patterns
                if 'import' in content or 'from' in content:
                    patterns['has_imports'] = patterns.get('has_imports', 0) + 1
                
                if 'function' in content or 'def ' in content:
                    patterns['has_functions'] = patterns.get('has_functions', 0) + 1
                
                if 'class ' in content:
                    patterns['has_classes'] = patterns.get('has_classes', 0) + 1
                
                if 'test' in content.lower() or 'spec' in content.lower():
                    patterns['has_tests'] = patterns.get('has_tests', 0) + 1
                    
        except (UnicodeDecodeError, OSError):
            pass
    
    def detect_error_patterns(self, tool_output: str) -> List[Dict[str, Any]]:
        """Detect error patterns from tool output."""
        errors = []
        
        # Common error patterns
        error_patterns = [
            (r'Error: (.+)', 'generic_error'),
            (r'TypeError: (.+)', 'type_error'),
            (r'SyntaxError: (.+)', 'syntax_error'),
            (r'TS\d+: (.+)', 'typescript_error'),
            (r'ESLint: (.+)', 'eslint_error'),
            (r'npm ERR! (.+)', 'npm_error'),
            (r'FAIL (.+)', 'test_failure'),
            (r'Cannot find module (.+)', 'module_not_found'),
            (r'Permission denied (.+)', 'permission_error'),
        ]
        
        for pattern, error_type in error_patterns:
            matches = re.finditer(pattern, tool_output, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                errors.append({
                    'type': error_type,
                    'message': match.group(1).strip(),
                    'full_match': match.group(0),
                    'timestamp': datetime.now().isoformat()
                })
        
        return errors
    
    def update_patterns(self, context_data: Dict[str, Any]):
        """Update the patterns file with new context data."""
        try:
            # Load existing patterns
            with open(self.patterns_file, 'r') as f:
                patterns = json.load(f)
            
            # Update with new data
            patterns['last_updated'] = datetime.now().isoformat()
            patterns['total_sessions'] = patterns.get('total_sessions', 0) + 1
            
            # Update git patterns
            if 'git_diff' in context_data:
                git_data = context_data['git_diff']
                for file in git_data.get('unstaged_files', []) + git_data.get('staged_files', []):
                    if file:
                        patterns['files_changed'][file] = patterns['files_changed'].get(file, 0) + 1
            
            # Update error patterns
            if 'errors' in context_data:
                for error in context_data['errors']:
                    error_key = f"{error['type']}:{error['message'][:50]}"
                    patterns['errors'][error_key] = patterns['errors'].get(error_key, 0) + 1
            
            # Update file patterns
            if 'file_patterns' in context_data:
                file_patterns = context_data['file_patterns']
                for key, value in file_patterns.items():
                    if isinstance(value, dict):
                        if key not in patterns:
                            patterns[key] = {}
                        for sub_key, count in value.items():
                            patterns[key][sub_key] = patterns[key].get(sub_key, 0) + count
            
            # Save updated patterns
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
                
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error updating patterns: {e}", file=sys.stderr)
    
    def analyze_context(self, tool_name: str = None, tool_args: List[str] = None, 
                       tool_output: str = None) -> Dict[str, Any]:
        """Main analysis method - analyzes current context and updates patterns."""
        
        context = {
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'tool_args': tool_args or [],
        }
        
        # Analyze git state
        context['git_diff'] = self.analyze_git_diff()
        
        # Analyze file patterns from git changes
        all_files = []
        if 'unstaged_files' in context['git_diff']:
            all_files.extend(context['git_diff']['unstaged_files'])
        if 'staged_files' in context['git_diff']:
            all_files.extend(context['git_diff']['staged_files'])
        
        if all_files:
            context['file_patterns'] = self.analyze_file_patterns(all_files)
        
        # Analyze errors in tool output
        if tool_output:
            context['errors'] = self.detect_error_patterns(tool_output)
        
        # Update patterns storage
        self.update_patterns(context)
        
        return context

def main():
    """Main entry point when called as a script."""
    if len(sys.argv) < 2:
        print("Usage: python context_analyzer.py <project_root> [tool_name] [tool_output_file]")
        sys.exit(1)
    
    project_root = sys.argv[1]
    tool_name = sys.argv[2] if len(sys.argv) > 2 else None
    tool_output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    tool_output = None
    if tool_output_file and os.path.exists(tool_output_file):
        with open(tool_output_file, 'r') as f:
            tool_output = f.read()
    
    analyzer = ContextAnalyzer(project_root)
    context = analyzer.analyze_context(tool_name=tool_name, tool_output=tool_output)
    
    # Output analysis results as JSON
    print(json.dumps(context, indent=2))

if __name__ == "__main__":
    main()
