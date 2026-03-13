#!/usr/bin/env python3
"""
Franex Referral Tracker
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "referrals.json"

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_lead(name, profile, visa, phone="", email=""):
    data = load_data()
    ref_id = f"REF{str(len(data['referrals']) + 1).zfill(3)}"
    
    lead = {
        "id": ref_id,
        "name": name,
        "profile": profile,
        "visa_type": visa,
        "phone": phone,
        "email": email,
        "status": "Lead",
        "referral_code": "",
        "contact_date": datetime.now().strftime("%Y-%m-%d"),
        "registered_date": "",
        "commission_expected": 0,
        "commission_received": 0,
        "notes": ""
    }
    
    data['referrals'].append(lead)
    data['stats']['total_leads'] += 1
    save_data(data)
    
    print(f"✅ Added: {name} ({ref_id})")
    return ref_id

def update_status(ref_id, status):
    data = load_data()
    
    for lead in data['referrals']:
        if lead['id'] == ref_id:
            old_status = lead['status']
            lead['status'] = status
            
            if status == "Registered" and not lead['registered_date']:
                lead['registered_date'] = datetime.now().strftime("%Y-%m-%d")
            
            save_data(data)
            print(f"✅ {ref_id}: {old_status} → {status}")
            return
    
    print(f"❌ Not found: {ref_id}")

def list_leads():
    data = load_data()
    
    print("\n" + "="*70)
    print("FRANEX REFERRALS")
    print("="*70)
    
    for lead in data['referrals']:
        print(f"{lead['id']} | {lead['name'][:20]:<20} | {lead['visa_type']:<10} | {lead['status']:<12}")
    
    print()

def show_stats():
    data = load_data()
    stats = data['stats']
    
    print("\n📊 STATS")
    print("="*40)
    print(f"Total Leads:      {stats['total_leads']}")
    print(f"Registered:       {stats['registered']}")
    print(f"Approved:         {stats['approved']}")
    print(f"Paid:             {stats['paid']}")
    print(f"Total Earned:     ${stats['total_earned']:,.2f}")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 franex_tracker.py <command>")
        print("Commands: add, update, list, stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        name = sys.argv[2] if len(sys.argv) > 2 else input("Name: ")
        profile = sys.argv[3] if len(sys.argv) > 3 else input("Profile (A/B/C/D): ")
        visa = sys.argv[4] if len(sys.argv) > 4 else input("Visa Type: ")
        add_lead(name, profile, visa)
    elif cmd == "update":
        ref_id = sys.argv[2] if len(sys.argv) > 2 else input("Ref ID: ")
        status = sys.argv[3] if len(sys.argv) > 3 else input("Status: ")
        update_status(ref_id, status)
    elif cmd == "list":
        list_leads()
    elif cmd == "stats":
        show_stats()
    else:
        print("Unknown command")
