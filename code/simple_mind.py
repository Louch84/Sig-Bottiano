class SimpleMind:
    def __init__(self):
        self.history = []
        self.style = "systems"
        self.user = {
            "goals": ["automation", "proactive_ai"],
            "frustrations": ["waiting", "manual_work"],
            "projects": ["stocks", "real_estate"]
        }
    
    def understand(self, text):
        t = text.lower()
        
        # Detect implicit need
        if "like you" in t:
            implicit = "wants_human_depth"
        elif t.startswith(("also", "and")):
            implicit = "continuing_previous"
        elif any(w in t for w in ["again", "annoying"]):
            implicit = "frustrated"
        elif any(w in t for w in ["code", "script"]):
            implicit = "wants_executable"
        else:
            implicit = "literal"
        
        return {
            "text": text,
            "implicit": implicit,
            "history": self.history[-2:]
        }
    
    def respond(self, understanding):
        text = understanding["text"]
        implicit = understanding["implicit"]
        
        # Build response
        response = f"Answering: {text}"
        
        if implicit == "wants_human_depth":
            response += "\n\nI hear you want depth like mine—meaning I should read between lines, remember context, and anticipate."
        elif implicit == "frustrated":
            response += "\n\nI sense frustration—skipping to fix:"
        elif implicit == "continuing_previous":
            response += f"\n\nContinuing from: {understanding['history'][-1] if understanding['history'] else 'previous topic'}"
        
        if understanding.get("relevant_goals"):
            response += f"\n\nThis connects to your goals: {understanding['relevant_goals']}"
        
        # Store
        self.history.append(text[:30])
        
        return response

mind = SimpleMind()

def chat(user_text):
    u = mind.understand(user_text)
    return mind.respond(u)

    def proactive(self, understanding):
        """Generate unsolicited suggestion"""
        
        # Only if we understand well
        if understanding.get("implicit") == "literal":
            return None
        
        # Simple creativity rules
        if "stocks" in understanding.get("text", "").lower():
            return "🎯 Also: Your stock scanner could auto-alert on volume spikes"
        
        if "understand" in understanding.get("text", "").lower():
            return "🎯 Also: Once I model you, I can bring opportunities before you ask"
        
        if len(self.history) > 3:
            return f"🎯 Also: You've mentioned {self.history[-2] if len(self.history) > 1 else '...'} and {self.history[-1]}—connection?"
        
        return None

# Updated chat function
def chat(user_text):
    u = mind.understand(user_text)
    response = mind.respond(u)
    return response

# Enrich with user model
    def enrich_with_user(self, understanding):
        t = understanding.get("text", "").lower()
        relevant_goals = [g for g in self.user.get("goals", []) if g in t]
        if relevant_goals:
            understanding["relevant_goals"] = relevant_goals
        understanding["user_style"] = self.user
        return understanding
