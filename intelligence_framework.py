#!/usr/bin/env python3
"""
Intelligence Framework
Based on research: Gardner's Multiple Intelligences, IQ/EQ/SQ/AQ model,
Fluid/Crystallized intelligence, and cognitive enhancement strategies
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class IntelligenceType(Enum):
    """Types of intelligence (Gardner + extensions)"""
    # Gardner's 8 intelligences
    LINGUISTIC = "linguistic"           # Words, language
    LOGICAL_MATHEMATICAL = "logical"    # Logic, math, patterns
    SPATIAL = "spatial"                 # Space, visualization
    MUSICAL = "musical"                 # Rhythm, sound
    BODILY_KINESTHETIC = "bodily"       # Body movement
    INTERPERSONAL = "interpersonal"     # Understanding others
    INTRAPERSONAL = "intrapersonal"     # Understanding self
    NATURALISTIC = "naturalistic"       # Nature, environment
    
    # Extended intelligences
    EMOTIONAL = "emotional"             # EQ - emotional awareness
    SOCIAL = "social"                   # SQ - social understanding
    ADAPTIVE = "adaptive"               # AQ - adaptability, resilience
    CREATIVE = "creative"               # Creative problem-solving
    SYSTEMS = "systems"                 # Systems thinking
    PHILOSOPHICAL = "philosophical"     # Deep questioning

@dataclass
class IntelligenceProfile:
    """Profile of someone's intelligence across types"""
    linguistic: int          # 0-100
    logical_mathematical: int
    spatial: int
    musical: int
    bodily_kinesthetic: int
    interpersonal: int
    intrapersonal: int
    naturalistic: int
    emotional: int
    social: int
    adaptive: int
    creative: int
    systems: int
    philosophical: int
    
    def get_strengths(self, top_n: int = 3) -> List[Tuple[str, int]]:
        """Get top N intelligences"""
        all_scores = [
            ("Linguistic", self.linguistic),
            ("Logical-Mathematical", self.logical_mathematical),
            ("Spatial", self.spatial),
            ("Musical", self.musical),
            ("Bodily-Kinesthetic", self.bodily_kinesthetic),
            ("Interpersonal", self.interpersonal),
            ("Intrapersonal", self.intrapersonal),
            ("Naturalistic", self.naturalistic),
            ("Emotional", self.emotional),
            ("Social", self.social),
            ("Adaptive", self.adaptive),
            ("Creative", self.creative),
            ("Systems", self.systems),
            ("Philosophical", self.philosophical),
        ]
        return sorted(all_scores, key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_weaknesses(self, bottom_n: int = 3) -> List[Tuple[str, int]]:
        """Get bottom N intelligences (development areas)"""
        all_scores = [
            ("Linguistic", self.linguistic),
            ("Logical-Mathematical", self.logical_mathematical),
            ("Spatial", self.spatial),
            ("Musical", self.musical),
            ("Bodily-Kinesthetic", self.bodily_kinesthetic),
            ("Interpersonal", self.interpersonal),
            ("Intrapersonal", self.intrapersonal),
            ("Naturalistic", self.naturalistic),
            ("Emotional", self.emotional),
            ("Social", self.social),
            ("Adaptive", self.adaptive),
            ("Creative", self.creative),
            ("Systems", self.systems),
            ("Philosophical", self.philosophical),
        ]
        return sorted(all_scores, key=lambda x: x[1])[:bottom_n]

class IntelligenceFramework:
    """
    Comprehensive intelligence framework
    Based on research of cognitive science and multiple intelligence theory
    """
    
    # Intelligence descriptions and enhancement strategies
    INTELLIGENCE_DATA = {
        IntelligenceType.LINGUISTIC: {
            'name': 'Linguistic Intelligence',
            'description': 'Sensitivity to spoken and written language, ability to learn languages',
            'abilities': ['Reading comprehension', 'Writing', 'Speaking', 'Word memory', 'Learning languages'],
            'enhancement': [
                'Read widely across genres',
                'Write daily (journaling, essays)',
                'Learn new vocabulary deliberately',
                'Practice public speaking',
                'Study multiple languages',
                'Play word games (crosswords, Scrabble)',
                'Engage in debates and discussions'
            ],
            'careers': ['Writer', 'Lawyer', 'Journalist', 'Teacher', 'Translator']
        },
        IntelligenceType.LOGICAL_MATHEMATICAL: {
            'name': 'Logical-Mathematical Intelligence',
            'description': 'Capacity for logical reasoning, patterns, numbers, abstract thinking',
            'abilities': ['Mathematical reasoning', 'Pattern recognition', 'Logical deduction', 'Problem-solving', 'Scientific thinking'],
            'enhancement': [
                'Practice mental math daily',
                'Solve logic puzzles and brain teasers',
                'Learn programming',
                'Study mathematics progressively',
                'Play chess or Go',
                'Analyze data and statistics',
                'Learn formal logic'
            ],
            'careers': ['Scientist', 'Engineer', 'Mathematician', 'Programmer', 'Economist']
        },
        IntelligenceType.SPATIAL: {
            'name': 'Spatial Intelligence',
            'description': 'Ability to think in 3D, visualize, manipulate mental images',
            'abilities': ['Mental rotation', 'Map reading', 'Visual art', 'Spatial reasoning', 'Navigation'],
            'enhancement': [
                'Practice drawing and sketching',
                'Work with 3D modeling software',
                'Play spatial puzzles (Tetris, Rubik\'s cube)',
                'Study architecture or design',
                'Practice mental visualization',
                'Navigate without GPS',
                'Play strategy video games'
            ],
            'careers': ['Architect', 'Pilot', 'Artist', 'Surgeon', 'Graphic Designer']
        },
        IntelligenceType.MUSICAL: {
            'name': 'Musical Intelligence',
            'description': 'Skill in performance, composition, appreciation of musical patterns',
            'abilities': ['Pitch recognition', 'Rhythm', 'Musical memory', 'Composition', 'Instrument playing'],
            'enhancement': [
                'Learn a musical instrument',
                'Study music theory',
                'Practice active listening',
                'Sing regularly',
                'Compose simple melodies',
                'Analyze song structures',
                'Attend live performances'
            ],
            'careers': ['Musician', 'Composer', 'Music Producer', 'Conductor', 'Music Therapist']
        },
        IntelligenceType.BODILY_KINESTHETIC: {
            'name': 'Bodily-Kinesthetic Intelligence',
            'description': 'Control of body movements and capacity to handle objects skillfully',
            'abilities': ['Coordination', 'Balance', 'Dexterity', 'Timing', 'Physical expression'],
            'enhancement': [
                'Learn new physical skills (dance, sports)',
                'Practice fine motor tasks',
                'Engage in regular exercise',
                'Study martial arts or yoga',
                'Build/craft with hands',
                'Practice mindfulness of body',
                'Play physical games'
            ],
            'careers': ['Athlete', 'Dancer', 'Surgeon', 'Mechanic', 'Actor']
        },
        IntelligenceType.INTERPERSONAL: {
            'name': 'Interpersonal Intelligence',
            'description': 'Capacity to understand intentions, motivations, desires of others',
            'abilities': ['Empathy', 'Communication', 'Leadership', 'Conflict resolution', 'Reading social cues'],
            'enhancement': [
                'Practice active listening',
                'Study body language and non-verbal cues',
                'Engage in group activities',
                'Practice perspective-taking',
                'Mentor or teach others',
                'Join clubs or organizations',
                'Study psychology and sociology'
            ],
            'careers': ['Teacher', 'Counselor', 'Sales', 'Politician', 'Manager']
        },
        IntelligenceType.INTRAPERSONAL: {
            'name': 'Intrapersonal Intelligence',
            'description': 'Understanding oneself, introspection, self-reflection',
            'abilities': ['Self-awareness', 'Emotional regulation', 'Self-motivation', 'Personal growth', 'Values clarity'],
            'enhancement': [
                'Keep a daily journal',
                'Practice meditation',
                'Reflect on personal values',
                'Set and review goals regularly',
                'Practice self-compassion',
                'Study philosophy and psychology',
                'Seek feedback and reflect on it'
            ],
            'careers': ['Philosopher', 'Psychologist', 'Writer', 'Entrepreneur', 'Theologian']
        },
        IntelligenceType.NATURALISTIC: {
            'name': 'Naturalistic Intelligence',
            'description': 'Recognition and categorization of natural objects, flora, fauna',
            'abilities': ['Classification', 'Pattern recognition in nature', 'Environmental awareness', 'Observation', 'Conservation'],
            'enhancement': [
                'Spend time in nature regularly',
                'Learn to identify plants and animals',
                'Study ecology and biology',
                'Practice nature photography',
                'Garden or grow plants',
                'Learn about weather patterns',
                'Practice outdoor survival skills'
            ],
            'careers': ['Biologist', 'Farmer', 'Conservationist', 'Chef', 'Botanist']
        },
        IntelligenceType.EMOTIONAL: {
            'name': 'Emotional Intelligence (EQ)',
            'description': 'Awareness and management of own emotions and others emotions',
            'abilities': ['Emotional awareness', 'Self-regulation', 'Empathy', 'Social skills', 'Motivation'],
            'enhancement': [
                'Practice naming emotions as they arise',
                'Develop emotional vocabulary',
                'Learn CBT techniques',
                'Practice empathy exercises',
                'Study emotional intelligence frameworks',
                'Build stress management skills',
                'Practice mindfulness meditation'
            ],
            'impact': '80% of adult success comes from EQ (Goleman research)',
            'careers': ['Leader', 'Counselor', 'Negotiator', 'Coach', 'HR Professional']
        },
        IntelligenceType.SOCIAL: {
            'name': 'Social Intelligence (SQ)',
            'description': 'Understanding and navigating social situations and relationships',
            'abilities': ['Social awareness', 'Relationship management', 'Cultural competence', 'Influence', 'Collaboration'],
            'enhancement': [
                'Study social dynamics and norms',
                'Practice networking',
                'Learn cross-cultural communication',
                'Build diverse social circles',
                'Study persuasion and influence ethically',
                'Practice conflict resolution',
                'Engage in community service'
            ],
            'careers': ['Diplomat', 'Community Organizer', 'Sales', 'HR', 'Teacher']
        },
        IntelligenceType.ADAPTIVE: {
            'name': 'Adaptive Intelligence (AQ)',
            'description': 'Ability to adapt to change, resilience, problem-solving in uncertainty',
            'abilities': ['Resilience', 'Flexibility', 'Learning agility', 'Stress tolerance', 'Uncertainty navigation'],
            'enhancement': [
                'Deliberately expose yourself to new situations',
                'Practice cognitive flexibility exercises',
                'Learn to reframe setbacks',
                'Build stress tolerance gradually',
                'Study change management',
                'Practice improvisation',
                'Develop a growth mindset'
            ],
            'careers': ['Entrepreneur', 'Consultant', 'Emergency Responder', 'Project Manager', 'Startup Founder']
        },
        IntelligenceType.CREATIVE: {
            'name': 'Creative Intelligence',
            'description': 'Ability to generate novel ideas, solutions, and artistic expressions',
            'abilities': ['Divergent thinking', 'Idea generation', 'Pattern breaking', 'Artistic expression', 'Innovation'],
            'enhancement': [
                'Practice brainstorming daily',
                'Engage in artistic hobbies',
                'Study creativity techniques (SCAMPER, etc.)',
                'Expose yourself to diverse stimuli',
                'Practice lateral thinking',
                'Allow for incubation time',
                'Embrace constraints as creative fuel'
            ],
            'careers': ['Artist', 'Designer', 'Inventor', 'Marketer', 'Entrepreneur']
        },
        IntelligenceType.SYSTEMS: {
            'name': 'Systems Intelligence',
            'description': 'Understanding complex systems, interconnections, and emergent properties',
            'abilities': ['Systems thinking', 'Pattern recognition across scales', 'Feedback loops', 'Causality', 'Holistic view'],
            'enhancement': [
                'Study systems thinking (Senge, Meadows)',
                'Practice mapping systems',
                'Study ecology and complexity science',
                'Learn about feedback loops',
                'Analyze second and third order effects',
                'Study history and long-term patterns',
                'Practice mental modeling'
            ],
            'careers': ['Systems Analyst', 'Ecologist', 'Urban Planner', 'Economist', 'Policy Maker']
        },
        IntelligenceType.PHILOSOPHICAL: {
            'name': 'Philosophical Intelligence',
            'description': 'Deep questioning of meaning, existence, values, and knowledge',
            'abilities': ['Critical questioning', 'Conceptual analysis', 'Ethical reasoning', 'Metacognition', 'Meaning-making'],
            'enhancement': [
                'Study philosophy (ethics, epistemology, metaphysics)',
                'Practice Socratic questioning',
                'Engage with big questions regularly',
                'Study different philosophical traditions',
                'Reflect on values and meaning',
                'Practice intellectual humility',
                'Study cognitive biases and epistemology'
            ],
            'careers': ['Philosopher', 'Ethicist', 'Theologian', 'Writer', 'Thought Leader']
        }
    }
    
    def get_intelligence_profile(self, **scores) -> IntelligenceProfile:
        """
        Create an intelligence profile
        Pass scores for each intelligence type (0-100)
        Missing scores default to 50 (average)
        """
        return IntelligenceProfile(
            linguistic=scores.get('linguistic', 50),
            logical_mathematical=scores.get('logical_mathematical', 50),
            spatial=scores.get('spatial', 50),
            musical=scores.get('musical', 50),
            bodily_kinesthetic=scores.get('bodily_kinesthetic', 50),
            interpersonal=scores.get('interpersonal', 50),
            intrapersonal=scores.get('intrapersonal', 50),
            naturalistic=scores.get('naturalistic', 50),
            emotional=scores.get('emotional', 50),
            social=scores.get('social', 50),
            adaptive=scores.get('adaptive', 50),
            creative=scores.get('creative', 50),
            systems=scores.get('systems', 50),
            philosophical=scores.get('philosophical', 50)
        )
    
    def analyze_strengths(self, profile: IntelligenceProfile) -> Dict:
        """Analyze someone's intelligence strengths"""
        strengths = profile.get_strengths(5)
        weaknesses = profile.get_weaknesses(3)
        
        return {
            'top_strengths': strengths,
            'development_areas': weaknesses,
            'primary_intelligence': strengths[0][0],
            'recommendations': self._generate_recommendations(strengths, weaknesses)
        }
    
    def _generate_recommendations(self, strengths, weaknesses) -> List[str]:
        """Generate personalized development recommendations"""
        recs = []
        
        # Leverage strengths
        top_strength = strengths[0][0]
        recs.append(f"Leverage your {top_strength} strength - use it as your primary problem-solving approach")
        
        # Develop weaknesses
        if weaknesses:
            bottom_weakness = weaknesses[0][0]
            data = self._get_intelligence_by_name(bottom_weakness)
            if data:
                recs.append(f"Develop {bottom_weakness}: {data['enhancement'][0]}")
        
        # Balance
        recs.append("Combine top 2-3 intelligences for complex problem-solving")
        recs.append("Practice metacognition - think about your thinking")
        
        return recs
    
    def _get_intelligence_by_name(self, name: str) -> Optional[Dict]:
        """Get intelligence data by name"""
        for intel_type, data in self.INTELLIGENCE_DATA.items():
            if data['name'] == name or intel_type.value.replace('_', '-') in name.lower().replace(' ', '-'):
                return data
        return None
    
    def get_enhancement_plan(self, intelligence_type: IntelligenceType) -> Dict:
        """Get detailed enhancement plan for a specific intelligence"""
        data = self.INTELLIGENCE_DATA.get(intelligence_type)
        if not data:
            return {}
        
        return {
            'intelligence': data['name'],
            'description': data['description'],
            'current_abilities': data['abilities'],
            'daily_practices': data['enhancement'][:3],
            'weekly_practices': data['enhancement'][3:],
            'career_paths': data.get('careers', []),
            'assessment': f"Rate yourself 1-10 on: {', '.join(data['abilities'][:3])}"
        }
    
    def cognitive_assessment(self) -> Dict:
        """Self-assessment questionnaire structure"""
        return {
            'linguistic_questions': [
                'I enjoy reading books and articles',
                'I have a large vocabulary',
                'I enjoy writing and expressing ideas',
                'I learn languages easily',
                'I enjoy word games and puzzles'
            ],
            'logical_questions': [
                'I enjoy solving math problems',
                'I can easily spot patterns in data',
                'I enjoy programming or logic puzzles',
                'I think in a structured, logical way',
                'I enjoy chess or strategy games'
            ],
            'interpersonal_questions': [
                'I understand how others are feeling',
                'People often come to me for advice',
                'I enjoy working in groups',
                'I can read social situations well',
                'I adapt my communication to different people'
            ],
            'intrapersonal_questions': [
                'I spend time reflecting on my thoughts',
                'I know my strengths and weaknesses well',
                'I have clear personal values',
                'I set and track personal goals',
                'I understand my emotional patterns'
            ],
            'creative_questions': [
                'I generate many ideas easily',
                'I enjoy artistic activities',
                'I make unusual connections between ideas',
                'I challenge conventional thinking',
                'I enjoy experimenting with new approaches'
            ]
        }


# Convenience functions
def analyze_intelligence(**scores) -> str:
    """Quick intelligence analysis"""
    framework = IntelligenceFramework()
    profile = framework.get_intelligence_profile(**scores)
    analysis = framework.analyze_strengths(profile)
    
    output = f"🧠 INTELLIGENCE PROFILE\n{'='*60}\n\n"
    output += "Top Strengths:\n"
    for intel, score in analysis['top_strengths'][:3]:
        output += f"  • {intel}: {score}/100\n"
    
    output += "\nDevelopment Areas:\n"
    for intel, score in analysis['development_areas'][:2]:
        output += f"  • {intel}: {score}/100\n"
    
    output += "\nRecommendations:\n"
    for rec in analysis['recommendations'][:3]:
        output += f"  • {rec}\n"
    
    return output

def enhance_intelligence(intelligence_type: str) -> str:
    """Get enhancement plan for specific intelligence"""
    framework = IntelligenceFramework()
    
    # Map string to enum
    type_map = {
        'linguistic': IntelligenceType.LINGUISTIC,
        'logical': IntelligenceType.LOGICAL_MATHEMATICAL,
        'spatial': IntelligenceType.SPATIAL,
        'emotional': IntelligenceType.EMOTIONAL,
        'creative': IntelligenceType.CREATIVE,
        'social': IntelligenceType.SOCIAL,
        'adaptive': IntelligenceType.ADAPTIVE
    }
    
    intel_enum = type_map.get(intelligence_type.lower(), IntelligenceType.LOGICAL_MATHEMATICAL)
    plan = framework.get_enhancement_plan(intel_enum)
    
    output = f"📈 ENHANCEMENT PLAN: {plan['intelligence']}\n{'='*60}\n"
    output += f"\n{plan['description']}\n"
    output += "\nDaily Practices:\n"
    for practice in plan['daily_practices']:
        output += f"  • {practice}\n"
    
    return output


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🧠 INTELLIGENCE FRAMEWORK DEMO")
    print("="*70)
    print()
    
    # Test profile analysis
    print(analyze_intelligence(
        logical_mathematical=85,
        linguistic=75,
        interpersonal=70,
        creative=80,
        emotional=60,
        adaptive=75
    ))
    print()
    
    # Test enhancement plan
    print(enhance_intelligence('creative'))
    print()
    
    print("="*70)
    print("✅ Intelligence framework operational")
    print("="*70)
