#!/usr/bin/env python3
"""
Conversation Analyzer for RuleCrafter
Analyzes Claude Code session logs to understand command usage patterns and user interactions.
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter

class ConversationAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rulecrafter_dir = self.project_root / '.claude' / 'rulecrafter'
        self.storage_dir = self.rulecrafter_dir / 'storage'
        self.patterns_file = self.storage_dir / 'patterns.json'
        
        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_session_log(self, log_content: str) -> Dict[str, Any]:
        """Parse Claude Code session log content."""
        session_data = {
            'commands_used': [],
            'slash_commands': [],
            'error_messages': [],
            'user_prompts': [],
            'tool_calls': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # If it's JSON format from --output-format json
            if log_content.strip().startswith('{'):
                json_data = json.loads(log_content)
                return self._parse_json_session(json_data)
            else:
                # Parse plain text log
                return self._parse_text_session(log_content)
                
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self._parse_text_session(log_content)
    
    def _parse_json_session(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON-formatted session data."""
        session_data = {
            'commands_used': [],
            'slash_commands': [],
            'error_messages': [],
            'user_prompts': [],
            'tool_calls': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract tool calls
        if 'tool_calls' in json_data:
            for tool_call in json_data['tool_calls']:
                session_data['tool_calls'].append({
                    'tool': tool_call.get('name', ''),
                    'args': tool_call.get('arguments', {}),
                    'timestamp': tool_call.get('timestamp', '')
                })
        
        # Extract messages/prompts
        if 'messages' in json_data:
            for message in json_data['messages']:
                if message.get('role') == 'user':
                    content = message.get('content', '')
                    session_data['user_prompts'].append(content)
                    
                    # Check for slash commands
                    slash_commands = self._extract_slash_commands(content)
                    session_data['slash_commands'].extend(slash_commands)
        
        return session_data
    
    def _parse_text_session(self, log_content: str) -> Dict[str, Any]:
        """Parse plain text session logs."""
        session_data = {
            'commands_used': [],
            'slash_commands': [],
            'error_messages': [],
            'user_prompts': [],
            'tool_calls': [],
            'timestamp': datetime.now().isoformat()
        }
        
        lines = log_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for slash commands
            slash_commands = self._extract_slash_commands(line)
            session_data['slash_commands'].extend(slash_commands)
            
            # Look for error patterns
            if self._is_error_line(line):
                session_data['error_messages'].append(line)
            
            # Look for tool usage patterns
            tool_usage = self._extract_tool_usage(line)
            if tool_usage:
                session_data['tool_calls'].append(tool_usage)
            
            # Collect user prompts (simple heuristic)
            if self._looks_like_user_prompt(line):
                session_data['user_prompts'].append(line)
        
        return session_data
    
    def _extract_slash_commands(self, text: str) -> List[str]:
        """Extract slash commands from text."""
        # Pattern to match slash commands: /command-name or /command_name
        pattern = r'/([a-zA-Z][a-zA-Z0-9_-]*)'
        matches = re.findall(pattern, text)
        return [f"/{match}" for match in matches]
    
    def _is_error_line(self, line: str) -> bool:
        """Check if a line contains an error message."""
        error_indicators = [
            'error:', 'Error:', 'ERROR:',
            'failed:', 'Failed:', 'FAILED:',
            'exception:', 'Exception:', 'EXCEPTION:',
            'traceback:', 'Traceback:',
            'syntax error', 'type error',
            'command not found',
            'permission denied',
            'npm ERR!',
            'FAIL:'
        ]
        
        line_lower = line.lower()
        return any(indicator.lower() in line_lower for indicator in error_indicators)
    
    def _extract_tool_usage(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract tool usage information from a line."""
        # Common tool patterns
        tool_patterns = [
            (r'running.*?`([^`]+)`', 'shell_command'),
            (r'executing.*?`([^`]+)`', 'shell_command'),
            (r'editing.*?file.*?`([^`]+)`', 'file_edit'),
            (r'creating.*?file.*?`([^`]+)`', 'file_create'),
            (r'reading.*?file.*?`([^`]+)`', 'file_read'),
            (r'git\s+([a-zA-Z]+)', 'git_command'),
            (r'npm\s+([a-zA-Z]+)', 'npm_command'),
            (r'python\s+([^\s]+)', 'python_script'),
            (r'node\s+([^\s]+)', 'node_script'),
        ]
        
        for pattern, tool_type in tool_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return {
                    'type': tool_type,
                    'command': match.group(1),
                    'full_line': line,
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
    
    def _looks_like_user_prompt(self, line: str) -> bool:
        """Simple heuristic to identify user prompts."""
        # Skip very short lines or lines that look like system output
        if len(line) < 10:
            return False
        
        # Skip lines that start with common system prefixes
        system_prefixes = [
            '>', '$ ', '+ ', '- ', '* ',
            'INFO:', 'DEBUG:', 'WARN:', 'ERROR:',
            'npm ', 'git ', 'python ', 'node ',
            'Running', 'Executing', 'Creating', 'Editing'
        ]
        
        for prefix in system_prefixes:
            if line.startswith(prefix):
                return False
        
        # If it contains question words or request patterns, likely a prompt
        prompt_indicators = [
            'can you', 'please', 'how do', 'what is', 'why does',
            'help me', 'i need', 'could you', 'would you',
            'create', 'make', 'build', 'implement', 'fix', 'debug'
        ]
        
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in prompt_indicators)
    
    def analyze_command_patterns(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in command usage."""
        patterns = {
            'most_used_slash_commands': {},
            'command_sequences': [],
            'error_contexts': [],
            'tool_usage_frequency': {},
            'prompt_categories': {}
        }
        
        # Count slash command frequency
        slash_commands = session_data.get('slash_commands', [])
        command_counter = Counter(slash_commands)
        patterns['most_used_slash_commands'] = dict(command_counter.most_common(10))
        
        # Analyze tool usage frequency
        tool_calls = session_data.get('tool_calls', [])
        tool_types = [tool.get('type', '') for tool in tool_calls if tool.get('type')]
        tool_counter = Counter(tool_types)
        patterns['tool_usage_frequency'] = dict(tool_counter.most_common(10))
        
        # Analyze error contexts (what commands preceded errors)
        error_messages = session_data.get('error_messages', [])
        if error_messages and slash_commands:
            # Simple approach: last command before each error
            for i, error in enumerate(error_messages):
                if slash_commands:
                    # Find the most recent command before this error
                    recent_command = slash_commands[-1] if slash_commands else None
                    if recent_command:
                        patterns['error_contexts'].append({
                            'error': error[:100],  # Truncate long errors
                            'preceding_command': recent_command
                        })
        
        # Categorize prompts
        user_prompts = session_data.get('user_prompts', [])
        categories = self._categorize_prompts(user_prompts)
        patterns['prompt_categories'] = categories
        
        return patterns
    
    def _categorize_prompts(self, prompts: List[str]) -> Dict[str, int]:
        """Categorize user prompts by intent."""
        categories = {
            'code_creation': 0,
            'debugging': 0,
            'refactoring': 0,
            'testing': 0,
            'documentation': 0,
            'explanation': 0,
            'configuration': 0,
            'other': 0
        }
        
        for prompt in prompts:
            prompt_lower = prompt.lower()
            
            if any(word in prompt_lower for word in ['create', 'make', 'build', 'implement', 'write', 'add']):
                categories['code_creation'] += 1
            elif any(word in prompt_lower for word in ['debug', 'fix', 'error', 'bug', 'issue', 'problem']):
                categories['debugging'] += 1
            elif any(word in prompt_lower for word in ['refactor', 'improve', 'optimize', 'clean', 'restructure']):
                categories['refactoring'] += 1
            elif any(word in prompt_lower for word in ['test', 'spec', 'unit', 'integration', 'e2e']):
                categories['testing'] += 1
            elif any(word in prompt_lower for word in ['document', 'comment', 'readme', 'docs', 'explain']):
                categories['documentation'] += 1
            elif any(word in prompt_lower for word in ['what', 'why', 'how', 'explain', 'understand']):
                categories['explanation'] += 1
            elif any(word in prompt_lower for word in ['config', 'setup', 'install', 'configure', 'setting']):
                categories['configuration'] += 1
            else:
                categories['other'] += 1
        
        return categories
    
    def update_conversation_patterns(self, session_data: Dict[str, Any]):
        """Update stored patterns with new conversation data."""
        try:
            # Load existing patterns
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r') as f:
                    patterns = json.load(f)
            else:
                patterns = {
                    'commands': {},
                    'errors': {},
                    'conversations': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            # Analyze new patterns
            new_patterns = self.analyze_command_patterns(session_data)
            
            # Merge with existing patterns
            if 'conversations' not in patterns:
                patterns['conversations'] = {}
            
            # Update command usage
            for cmd, count in new_patterns.get('most_used_slash_commands', {}).items():
                if cmd not in patterns['commands']:
                    patterns['commands'][cmd] = 0
                patterns['commands'][cmd] += count
            
            # Update conversation-specific patterns
            patterns['conversations'].update({
                'last_session_patterns': new_patterns,
                'last_analysis': datetime.now().isoformat(),
                'total_sessions_analyzed': patterns['conversations'].get('total_sessions_analyzed', 0) + 1
            })
            
            patterns['last_updated'] = datetime.now().isoformat()
            
            # Save updated patterns
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
                
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error updating conversation patterns: {e}", file=sys.stderr)
    
    def analyze_session(self, log_content: str) -> Dict[str, Any]:
        """Main method to analyze a session log."""
        session_data = self.parse_session_log(log_content)
        patterns = self.analyze_command_patterns(session_data)
        
        # Update stored patterns
        self.update_conversation_patterns(session_data)
        
        return {
            'session_data': session_data,
            'patterns': patterns,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main entry point when called as a script."""
    if len(sys.argv) < 3:
        print("Usage: python convo_analyzer.py <project_root> <log_file_or_content>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    log_input = sys.argv[2]
    
    # Check if it's a file or direct content
    if os.path.exists(log_input):
        with open(log_input, 'r') as f:
            log_content = f.read()
    else:
        log_content = log_input
    
    analyzer = ConversationAnalyzer(project_root)
    result = analyzer.analyze_session(log_content)
    
    # Output analysis results as JSON
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
