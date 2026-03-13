#!/usr/bin/env python3
"""Code Generation: Write new modules for self"""

import os

class CodeGenerator:
    def __init__(self):
        self.code_dir = "/Users/sigbotti/.openclaw/workspace/code"
    
    def generate_module(self, name, template):
        filepath = os.path.join(self.code_dir, f"{name}.py")
        
        code = f"""#!/usr/bin/env python3
# Auto-generated module: {name}
# Created: by self-improvement system

{template}

if __name__ == "__main__":
    print("{name} module loaded")
"""
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return filepath

generator = CodeGenerator()
