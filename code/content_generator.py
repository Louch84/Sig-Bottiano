#!/usr/bin/env python3
"""Content Ideas Generator"""
import random

topics = {
    "phone_repair": [
        "5 Signs Your Phone Needs Repair ASAP",
        "DIY Phone Repair Mistakes That Cost You Money",
        "How Long Should a Phone Last?",
        "Phone Repair vs Replacement: What's Worth It?",
        "Hidden Phone Damage You Can't See"
    ],
    "philly": [
        "Best Phone Repair in West Philly",
        "Philadelphia Phone Store Reviews",
        "South Street Phone Deals",
        "Philly Small Business Spotlight"
    ],
    "trading": [
        "Short Squeeze 101: What Retail Investors Need to Know",
        "How to Spot a Squeeze Before It Happens",
        "Risk Management for Small Accounts",
        "Trading Under $50: High Risk, High Reward"
    ],
    "tech": [
        "AI for Small Business: What's Actually Useful",
        "Automation Tips for Small Business Owners",
        "The Future of Phone Technology"
    ]
}

def get_ideas(category=None, count=3):
    if category and category in topics:
        return random.sample(topics[category], min(count, len(topics[category])))
    
    all_ideas = []
    for cat in topics:
        all_ideas.extend(topics[cat])
    return random.sample(all_ideas, min(count, len(all_ideas)))

print("=== CONTENT IDEAS ===")
print("\n📱 Phone Repair:")
for idea in get_ideas("phone_repair", 3):
    print(f"  • {idea}")

print("\n🏛️ Philly:")
for idea in get_ideas("philly", 2):
    print(f"  • {idea}")

print("\n📈 Trading:")
for idea in get_ideas("trading", 3):
    print(f"  • {idea}")
