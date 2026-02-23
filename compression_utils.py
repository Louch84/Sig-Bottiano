#!/usr/bin/env python3
"""
Response Compression & Efficiency Utilities
Reduces token usage without losing information
"""

import re
from typing import List, Dict, Any

class ResponseCompressor:
    """Compress responses to minimize token burn"""
    
    @staticmethod
    def compress_table(data: List[Dict], columns: List[str] = None) -> str:
        """Compress tabular data into minimal format"""
        if not data:
            return "No data"
        
        if not columns:
            columns = list(data[0].keys())[:4]  # Limit to 4 columns
        
        lines = []
        # Header
        lines.append(" | ".join(columns))
        lines.append("-" * 40)
        
        # Rows
        for row in data[:10]:  # Max 10 rows
            values = [str(row.get(col, ''))[:12] for col in columns]  # Truncate
            lines.append(" | ".join(values))
        
        if len(data) > 10:
            lines.append(f"... and {len(data) - 10} more")
        
        return "\n".join(lines)
    
    @staticmethod
    def bullet_points(items: List[str], max_items: int = 5) -> str:
        """Create concise bullet list"""
        result = []
        for item in items[:max_items]:
            # Remove fluff words
            item = re.sub(r'^(Here is|This is|There are|We have)\s+', '', item, flags=re.I)
            result.append(f"• {item}")
        
        if len(items) > max_items:
            result.append(f"• ... {len(items) - max_items} more")
        
        return "\n".join(result)
    
    @staticmethod
    def summarize_file_content(content: str, max_lines: int = 20) -> str:
        """Summarize long file contents"""
        lines = content.split('\n')
        
        if len(lines) <= max_lines:
            return content
        
        # Get first 10 and last 10 lines
        first = lines[:10]
        last = lines[-10:]
        
        return '\n'.join(first) + '\n...\n' + '\n'.join(last)
    
    @staticmethod
    def one_line_summary(text: str) -> str:
        """Create one-line summary"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Limit to 100 chars
        if len(text) > 100:
            text = text[:97] + "..."
        return text
    
    @staticmethod
    def code_only(response: str) -> str:
        """Extract only code blocks from response"""
        # Find code blocks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
        if code_blocks:
            return '\n\n'.join(code_blocks)
        return response

class EfficiencyHints:
    """Hints for cost-effective operations"""
    
    SCANNER_OPTIMIZATIONS = """
COST-SAVING SCANNER MODES:

1. QUICK SCAN (10s, ~500 tokens)
   - 5 stocks only
   - Basic signals only
   - No SMC, no Greeks

2. STANDARD SCAN (30s, ~1500 tokens) [DEFAULT]
   - 15 stocks
   - Full analysis
   - Current mode

3. DEEP SCAN (60s, ~3000 tokens)
   - 30 stocks
   - Full backtesting
   - Historical correlation

Use: python3 optimized_scanner.py --mode quick
"""
    
    API_USAGE_GUIDE = """
API COST OPTIMIZATION:

Web Search: ~800 tokens per query
- Cache results for 1 hour
- Batch multiple queries
- Use only when necessary

File Operations: ~300-500 tokens
- Read once, cache content
- Batch edits when possible
- Use grep/extract, not full read

Code Generation: ~1500 tokens
- Reuse existing code
- Template-based generation
- Incremental updates only
"""

compressor = ResponseCompressor()
