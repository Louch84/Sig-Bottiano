#!/usr/bin/env python3
"""
Master Enhancement Interface
Simple access to all new capabilities
"""

try:
    from vector_memory import VectorMemory
    from code_intelligence import CodeIntelligence
    from batch_processor import BatchProcessor
    from skills_registry import skills
    
    # Initialize global instances
    memory = VectorMemory()
    code_intel = CodeIntelligence()
    processor = BatchProcessor()
    
    print("✅ All enhancements loaded successfully")
    print()
    print("Available capabilities:")
    print("  - memory: VectorMemory() - Semantic search")
    print("  - code_intel: CodeIntelligence() - AST parsing")
    print("  - processor: BatchProcessor() - Parallel processing")
    print("  - skills: SkillsRegistry - Capability management")
    print()
    print("Usage: from enhance_master import memory, code_intel, processor")
    
except ImportError as e:
    print(f"⚠️  Could not load enhancements: {e}")
    print("   Run: python3 enhance_capabilities.py")
