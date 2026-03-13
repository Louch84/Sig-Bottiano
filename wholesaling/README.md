# Motivated Seller Lead Tracker

## Add Lead
```
python3 tracker.py add "123 Main St" --owner "John Smith" --phone "555-1234" --price 150000
```

## Update Status
```
python3 tracker.py update LEAD001 --status "Made Offer" --offer 120000
```

## Commands
- add
- update
- list
- stats

## Status Flow
Lead → Contacted → Made Offer → Under Contract → Sold/Expired
