# In your agent's main.py or equivalent

from core.creative_loop import CreativeAutonomyEngine
from core.suggestion_handler import SuggestionLearningEngine

class YourAgent:
    def __init__(self):
        # Existing setup...
        
        # Initialize creative autonomy
        self.creative_engine = CreativeAutonomyEngine()
        self.learning_engine = SuggestionLearningEngine()
        
        # Start autonomy loop in background thread
        import threading
        autonomy_thread = threading.Thread(
            target=self.creative_engine.run_loop,
            daemon=True
        )
        autonomy_thread.start()
    
    def handle_message(self, user_message):
        # Check if it's a suggestion response
        if self.is_suggestion_response(user_message):
            self.learning_engine.process_response(
                suggestion_id=self.extract_id(user_message),
                response=user_message
            )
        else:
            # Normal processing
            self.process_user_request(user_message)
