
"""
Skills Registry System
Modular capabilities that can be added/removed dynamically
"""

import importlib
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Skill:
    """Represents a capability/skill"""
    name: str
    description: str
    version: str
    dependencies: List[str]
    enabled: bool = True
    
    # The actual implementation
    module_path: str = ""
    functions: Dict[str, Callable] = None

class SkillsRegistry:
    """
    Central registry for agent skills.
    Enables dynamic capability loading.
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._load_builtin_skills()
    
    def _load_builtin_skills(self):
        """Load core skills"""
        
        # Market Analysis Skill
        self.register(Skill(
            name="market_analysis",
            description="Analyze market data, trends, and indicators",
            version="1.0",
            dependencies=["yfinance", "numpy"],
            module_path="skills.market_analysis"
        ))
        
        # Code Intelligence Skill
        self.register(Skill(
            name="code_intelligence",
            description="Parse and understand code structure",
            version="1.0",
            dependencies=[],
            module_path="skills.code_intelligence"
        ))
        
        # Vector Memory Skill
        self.register(Skill(
            name="vector_memory",
            description="Semantic memory with similarity search",
            version="1.0",
            dependencies=["numpy", "sqlite3"],
            module_path="skills.vector_memory"
        ))
        
        # Batch Processing Skill
        self.register(Skill(
            name="batch_processing",
            description="Parallel processing with structured concurrency",
            version="1.0",
            dependencies=["asyncio"],
            module_path="skills.batch_processor"
        ))
    
    def register(self, skill: Skill):
        """Register a new skill"""
        self.skills[skill.name] = skill
    
    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)
    
    def list_enabled(self) -> List[Skill]:
        """List all enabled skills"""
        return [s for s in self.skills.values() if s.enabled]
    
    def enable(self, name: str):
        """Enable a skill"""
        if name in self.skills:
            self.skills[name].enabled = True
    
    def disable(self, name: str):
        """Disable a skill"""
        if name in self.skills:
            self.skills[name].enabled = False
    
    def check_dependencies(self, skill_name: str) -> List[str]:
        """Check if all dependencies are available"""
        skill = self.get(skill_name)
        if not skill:
            return []
        
        missing = []
        for dep in skill.dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing.append(dep)
        
        return missing

# Global registry
skills = SkillsRegistry()
