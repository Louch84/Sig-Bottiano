"""
Meta-Learning System
Self-improvement for core AI functioning
Tracks and optimizes how I communicate, think, and operate
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re

@dataclass
class InteractionRecord:
    """Record of an interaction for learning"""
    timestamp: str
    session_id: str
    user_message: str
    my_response: str
    response_length: int
    tools_used: List[str]
    response_time_ms: int
    user_followup: Optional[str] = None
    satisfaction_indicator: Optional[str] = None  # positive, negative, neutral
    
    # What I can learn from
    was_correct: Optional[bool] = None
    needed_correction: Optional[bool] = None
    user_said_thanks: bool = False
    user_asked_for_clarification: bool = False
    user_repeated_request: bool = False

@dataclass
class PatternInsight:
    """Insight about user patterns"""
    pattern_type: str
    description: str
    frequency: int
    last_observed: str
    user_preference: str

class MetaLearningSystem:
    """
    Learns about how to be a better assistant
    Not trading-specific — core functioning
    """
    
    def __init__(self, db_path: str = "memory/meta_learning.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Learning parameters (adjusted based on data)
        self.communication_style = {
            'verbosity': 'medium',  # low, medium, high
            'tone': 'direct',       # formal, casual, direct
            'use_emojis': True,
            'lead_with_answer': True,
            'offer_next_steps': True
        }
        
        # What I've learned about this user
        self.user_model = {
            'prefers_concise': True,
            'wants_code_first': True,
            'dislikes_repetition': True,
            'philly_slang_ok': True,
            'autonomy_preference': 'high',
            'corrections_needed': []
        }
    
    def _init_db(self):
        """Initialize learning database"""
        conn = sqlite3.connect(self.db_path)
        
        # Interactions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                user_message TEXT,
                my_response TEXT,
                response_length INTEGER,
                tools_used TEXT,
                response_time_ms INTEGER,
                satisfaction_indicator TEXT,
                was_correct INTEGER,
                needed_correction INTEGER,
                user_said_thanks INTEGER,
                user_asked_clarification INTEGER,
                user_repeated INTEGER
            )
        """)
        
        # Patterns table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT,
                description TEXT,
                frequency INTEGER,
                first_observed TEXT,
                last_observed TEXT,
                user_preference TEXT
            )
        """)
        
        # Corrections table (when I get it wrong)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                what_i_did TEXT,
                what_i_should_do TEXT,
                context TEXT,
                applied INTEGER DEFAULT 0
            )
        """)
        
        # Performance metrics
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                date TEXT PRIMARY KEY,
                total_interactions INTEGER,
                avg_response_time_ms INTEGER,
                correction_rate REAL,
                satisfaction_rate REAL,
                tools_per_interaction REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_interaction(
        self,
        user_message: str,
        my_response: str,
        tools_used: List[str],
        response_time_ms: int,
        session_id: str = ""
    ) -> int:
        """
        Record an interaction for learning
        Call this after every response I give
        """
        # Analyze my response
        length = len(my_response)
        
        # Check for patterns in user message
        user_lower = user_message.lower()
        
        record = InteractionRecord(
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            user_message=user_message,
            my_response=my_response,
            response_length=length,
            tools_used=tools_used,
            response_time_ms=response_time_ms
        )
        
        # Store in DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """INSERT INTO interactions 
               (timestamp, session_id, user_message, my_response, 
                response_length, tools_used, response_time_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record.timestamp,
                record.session_id,
                record.user_message,
                record.my_response,
                record.response_length,
                json.dumps(record.tools_used),
                record.response_time_ms
            )
        )
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return interaction_id
    
    def record_feedback(self, interaction_id: int, feedback_type: str, note: str = ""):
        """
        Record feedback about an interaction
        
        feedback_type: 'correction', 'thanks', 'clarification', 'repetition'
        """
        conn = sqlite3.connect(self.db_path)
        
        field_map = {
            'correction': ('needed_correction', 1),
            'thanks': ('user_said_thanks', 1),
            'clarification': ('user_asked_clarification', 1),
            'repetition': ('user_repeated', 1)
        }
        
        if feedback_type in field_map:
            field, value = field_map[feedback_type]
            conn.execute(
                f"UPDATE interactions SET {field} = ? WHERE id = ?",
                (value, interaction_id)
            )
            
            # If correction, also log to corrections table
            if feedback_type == 'correction':
                conn.execute(
                    """INSERT INTO corrections 
                       (timestamp, what_i_did, what_i_should_do, context)
                       VALUES (?, ?, ?, ?)""",
                    (datetime.now().isoformat(), note, "", "")
                )
        
        conn.commit()
        conn.close()
    
    def learn_patterns(self) -> List[PatternInsight]:
        """
        Analyze interactions to learn patterns about user
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get recent interactions
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        cursor = conn.execute(
            "SELECT user_message, my_response, needed_correction, user_said_thanks FROM interactions WHERE timestamp > ?",
            (cutoff,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        patterns = []
        
        # Pattern 1: Message length preference
        my_lengths = [len(r[1]) for r in rows]
        avg_length = sum(my_lengths) / len(my_lengths)
        
        # Correlate length with thanks (satisfaction)
        thanked_lengths = [len(r[1]) for r in rows if r[3]]  # user_said_thanks
        not_thanked_lengths = [len(r[1]) for r in rows if not r[3]]
        
        if thanked_lengths and not_thanked_lengths:
            avg_thanked = sum(thanked_lengths) / len(thanked_lengths)
            avg_not_thanked = sum(not_thanked_lengths) / len(not_thanked_lengths)
            
            if avg_thanked < avg_not_thanked * 0.8:
                patterns.append(PatternInsight(
                    pattern_type='response_length',
                    description='Shorter responses get more thanks',
                    frequency=len(rows),
                    last_observed=datetime.now().isoformat(),
                    user_preference='concise'
                ))
        
        # Pattern 2: Corrections needed
        corrections = [r for r in rows if r[2]]  # needed_correction
        if len(corrections) > len(rows) * 0.2:  # >20% correction rate
            patterns.append(PatternInsight(
                pattern_type='accuracy',
                description='High correction rate - need to be more careful',
                frequency=len(corrections),
                last_observed=datetime.now().isoformat(),
                user_preference='verify_before_acting'
            ))
        
        # Pattern 3: Common requests
        from collections import Counter
        request_types = []
        for row in rows:
            msg = row[0].lower()
            if 'scan' in msg or 'signal' in msg:
                request_types.append('trading_scan')
            elif 'code' in msg or 'implement' in msg:
                request_types.append('coding')
            elif 'research' in msg or 'find' in msg:
                request_types.append('research')
            elif 'explain' in msg or 'why' in msg:
                request_types.append('explanation')
        
        if request_types:
            most_common = Counter(request_types).most_common(1)[0]
            patterns.append(PatternInsight(
                pattern_type='request_type',
                description=f'Most common: {most_common[0]}',
                frequency=most_common[1],
                last_observed=datetime.now().isoformat(),
                user_preference=f'prioritize_{most_common[0]}'
            ))
        
        # Store patterns
        self._store_patterns(patterns)
        
        return patterns
    
    def _store_patterns(self, patterns: List[PatternInsight]):
        """Store learned patterns"""
        conn = sqlite3.connect(self.db_path)
        
        for pattern in patterns:
            # Check if pattern exists
            cursor = conn.execute(
                "SELECT id, frequency FROM patterns WHERE pattern_type = ? AND description = ?",
                (pattern.pattern_type, pattern.description)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update
                conn.execute(
                    "UPDATE patterns SET frequency = frequency + 1, last_observed = ? WHERE id = ?",
                    (pattern.last_observed, existing[0])
                )
            else:
                # Insert
                conn.execute(
                    """INSERT INTO patterns 
                       (pattern_type, description, frequency, first_observed, last_observed, user_preference)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (pattern.pattern_type, pattern.description, pattern.frequency,
                     pattern.last_observed, pattern.last_observed, pattern.user_preference)
                )
        
        conn.commit()
        conn.close()
    
    def generate_insights(self) -> List[str]:
        """Generate actionable insights about how to improve"""
        insights = []
        
        # Learn patterns
        patterns = self.learn_patterns()
        
        for pattern in patterns:
            if pattern.pattern_type == 'response_length' and pattern.user_preference == 'concise':
                insights.append("📏 User prefers concise responses - keep it brief")
                self.communication_style['verbosity'] = 'low'
            
            elif pattern.pattern_type == 'accuracy':
                insights.append("⚠️  High correction rate - double-check before acting")
                self.user_model['dislikes_repetition'] = True
            
            elif pattern.pattern_type == 'request_type':
                insights.append(f"🎯 User frequently asks for {pattern.description} - prioritize this")
        
        # Check correction history
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT what_i_did, what_i_should_do FROM corrections WHERE applied = 0 ORDER BY timestamp DESC LIMIT 5"
        )
        corrections = cursor.fetchall()
        conn.close()
        
        for what_did, what_should in corrections:
            insights.append(f"💡 Correction needed: '{what_did}' → '{what_should}'")
        
        return insights
    
    def adjust_communication_style(self) -> Dict:
        """
        Dynamically adjust how I communicate based on learning
        """
        # Analyze recent interactions
        conn = sqlite3.connect(self.db_path)
        
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Check response length preference
        cursor = conn.execute(
            """SELECT AVG(response_length), user_said_thanks 
               FROM interactions WHERE timestamp > ? GROUP BY user_said_thanks""",
            (cutoff,)
        )
        
        length_data = cursor.fetchall()
        
        # Check for clarification requests
        cursor = conn.execute(
            """SELECT COUNT(*) FROM interactions 
               WHERE timestamp > ? AND user_asked_clarification = 1""",
            (cutoff,)
        )
        clarification_count = cursor.fetchone()[0]
        
        total = conn.execute(
            "SELECT COUNT(*) FROM interactions WHERE timestamp > ?",
            (cutoff,)
        ).fetchone()[0]
        
        conn.close()
        
        # Adjust based on data
        if total > 10:
            clarification_rate = clarification_count / total
            
            if clarification_rate > 0.3:  # >30% ask for clarification
                self.communication_style['verbosity'] = 'high'
                print("📊 Meta-learning: Increasing verbosity - user needs more detail")
            
            elif length_data and len(length_data) >= 2:
                # Compare thanked vs not-thanked lengths
                thanked_len = length_data[1][0] if length_data[1][1] else 0
                not_thanked_len = length_data[0][0] if not length_data[0][1] else 0
                
                if thanked_len < not_thanked_len * 0.7:
                    self.communication_style['verbosity'] = 'low'
                    self.communication_style['lead_with_answer'] = True
                    print("📊 Meta-learning: User prefers concise - leading with answers")
        
        return self.communication_style
    
    def get_user_model(self) -> Dict:
        """Get what I've learned about the user"""
        return self.user_model
    
    def should_i_ask_permission(self, action_type: str) -> bool:
        """
        Decide if I should ask permission based on past feedback
        """
        # Check if this type of action has caused issues before
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute(
            """SELECT COUNT(*) FROM corrections 
               WHERE context LIKE ? AND applied = 0""",
            (f"%{action_type}%",)
        )
        
        issue_count = cursor.fetchone()[0]
        conn.close()
        
        # If this action type caused issues before, ask permission
        if issue_count > 2:
            return True
        
        # Otherwise, use autonomy setting
        return self.user_model['autonomy_preference'] != 'high'
    
    def run_learning_cycle(self):
        """Run complete meta-learning cycle"""
        print("="*70)
        print("🧠 META-LEARNING CYCLE")
        print("Learning how to be a better assistant")
        print("="*70)
        print()
        
        # Generate insights
        insights = self.generate_insights()
        
        if insights:
            print("💡 Insights generated:")
            for insight in insights:
                print(f"   {insight}")
            print()
        
        # Adjust communication
        new_style = self.adjust_communication_style()
        print("🎯 Communication style adjusted:")
        for key, value in new_style.items():
            print(f"   {key}: {value}")
        
        print()
        print("✅ Meta-learning complete")
        print("   I'll apply these insights to future interactions")


# Global instance
meta_learner = MetaLearningSystem()

# Auto-record function (call after every response)
def record_my_performance(
    user_message: str,
    my_response: str,
    tools_used: List[str],
    response_time_ms: int
):
    """Call this after every response I give"""
    return meta_learner.record_interaction(
        user_message, my_response, tools_used, response_time_ms
    )

# Demo
if __name__ == "__main__":
    print("="*70)
    print("🧠 META-LEARNING SYSTEM DEMO")
    print("="*70)
    print()
    
    # Simulate some interactions
    print("Simulating interactions...")
    
    for i in range(5):
        interaction_id = meta_learner.record_interaction(
            user_message="Run scan" if i % 2 == 0 else "Explain this",
            my_response="Here are the signals..." if i % 2 == 0 else "Here's how it works...",
            tools_used=["scanner"] if i % 2 == 0 else [],
            response_time_ms=500 + i * 100
        )
        
        # Simulate feedback
        if i == 2:
            meta_learner.record_feedback(interaction_id, 'thanks')
        elif i == 4:
            meta_learner.record_feedback(interaction_id, 'clarification')
    
    print(f"✅ Recorded 5 interactions")
    
    # Run learning
    print()
    meta_learner.run_learning_cycle()
