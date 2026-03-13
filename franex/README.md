# Franex Referral Commission Tracker

## Quick Commands

### Add New Lead
```bash
python3 franex_tracker.py add "John Smith" --profile A --visa E2 --phone "+1234567890"
```

### Update Status
```bash
python3 franex_tracker.py update REF001 --status Application
```

### Show All
```bash
python3 franex_tracker.py list
```

### Show Stats
```bash
python3 franex_tracker.py stats
```

---

## Profiles
- A = E2 Investor ($150K+, treaty countries)
- B = EB3 Caregiver (healthcare workers)
- C = Franchise Buyer ($25K-$500K)
- D = Portugal Seeker (retirees)

## Status Flow
Lead → Contacted → Registered → Application → Approved → Paid

## Commission Estimates
- E2 Visa: $5,000 - $25,000
- EB3 Visa: $3,000 - $10,000
- Franchise: 5-10% of franchise fee
- D7 Visa: $2,000 - $5,000
