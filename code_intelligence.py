
"""
Code Intelligence System
Uses AST parsing for better code understanding
"""

import ast
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class CodeIntelligence:
    """
    Parse and understand code structure.
    Better than regex for code operations.
    """
    
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'typescript']
    
    def parse_python(self, code: str) -> Dict:
        """
        Parse Python code into structured representation.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {'error': 'Invalid Python syntax'}
        
        result = {
            'imports': [],
            'functions': [],
            'classes': [],
            'variables': [],
            'complexity': 0
        }
        
        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result['imports'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                result['imports'].append(module)
            
            # Functions
            elif isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node)
                }
                result['functions'].append(func_info)
            
            # Classes
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'line': node.lineno
                }
                result['classes'].append(class_info)
            
            # Complexity (simple counter)
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                result['complexity'] += 1
        
        return result
    
    def find_function_boundaries(self, code: str, func_name: str) -> Optional[Tuple[int, int]]:
        """
        Find exact line numbers of a function.
        More reliable than text search.
        """
        try:
            tree = ast.parse(code)
        except:
            return None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                # Get end line (last line of function)
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                
                # Find actual end (handle decorators)
                start_line = node.lineno
                if node.decorator_list:
                    start_line = node.decorator_list[0].lineno
                
                return (start_line, end_line)
        
        return None
    
    def suggest_refactoring(self, code: str) -> List[Dict]:
        """
        Suggest code improvements based on AST analysis.
        """
        suggestions = []
        
        try:
            tree = ast.parse(code)
        except:
            return suggestions
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if lines > 50:
                    suggestions.append({
                        'type': 'long_function',
                        'message': f"Function '{node.name}' is {lines} lines. Consider breaking into smaller functions.",
                        'line': node.lineno
                    })
                
                # Check for too many arguments
                arg_count = len(node.args.args) + len(node.args.kwonlyargs)
                if arg_count > 5:
                    suggestions.append({
                        'type': 'too_many_args',
                        'message': f"Function '{node.name}' has {arg_count} arguments. Consider using a config object.",
                        'line': node.lineno
                    })
        
        return suggestions
    
    def extract_dependencies(self, code: str) -> List[str]:
        """Extract all imported modules"""
        try:
            tree = ast.parse(code)
        except:
            return []
        
        deps = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    deps.append(node.module)
        
        return list(set(deps))

# Usage
intel = CodeIntelligence()
