#!/usr/bin/env python3
"""
SHORT SQUEEZE SCANNER v7 - FULL
Includes: Price, Volume, Short Interest, News, Options Flow
Auto-posts to Discord
"""
import yfinance as yf
import time
import requests

FINNHUB_KEY = "d6ds1upr01qm89pkopa0d6ds1upr01qm89pkopag"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1482118210957607047/JEm-gRn06K2TGrC4V7WB-aVdJZww7wd2xz3wkrFDc6x2vmPgjpPKy2MMT-teLailo_E9"

def get_options(ticker):
    """Get options flow data"""
    try:
        s = yf.Ticker(ticker)
        dates = s.options
        if not dates:
            return None
        
        opt = s.option_chain(dates[0])
        call_vol = opt.calls['volume'].sum() if len(opt.calls) > 0 else 0
        put_vol = opt.puts['volume'].sum() if len(opt.puts) > 0 else 0
        pcr = put_vol / call_vol if call_vol > 0 else 1
        
        return {
            'call_vol': int(call_vol),
            'put_vol': int(put_vol),
            'pcr': round(pcr, 2),
            'exp': dates[0]
        }
    except:
        return None

def analyze(ticker):
    """Full analysis"""
    try:
        s = yf.Ticker(ticker)
        hist = s.history(period="10d")
        info = s.info
        
        if len(hist) < 2:
            return None
            
        price = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        day_chg = ((price - prev) / prev) * 100
        
        week_chg = 0
        if len(hist) > 5:
            week_chg = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
        
        vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].mean()
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1
        
        # Short Interest
        shares_short = info.get('sharesShort', 0)
        short_ratio = info.get('shortRatio', 0)
        short_float = info.get('shortPercentOfFloat', 0)
        
        # Options
        opt = get_options(ticker)
        
        # Scoring
        squeeze_score = 0
        if short_float and short_float > 0.20: squeeze_score += 30
        elif short_float and short_float > 0.10: squeeze_score += 20
        if short_ratio and short_ratio > 5: squeeze_score += 25
        elif short_ratio and short_ratio > 3: squeeze_score += 15
        
        score = 0
        if price < 5: score += 20
        elif price < 10: score += 15
        elif price < 50: score += 10
        
        if vol_ratio > 2: score += 25
        elif vol_ratio > 1.5: score += 15
        
        if day_chg > 5: score += 20
        elif day_chg > 2: score += 15
        elif day_chg > 0: score += 10
        elif day_chg < -10: score -= 30
        
        if week_chg > 10: score += 15
        elif week_chg > 5: score += 10
        elif week_chg < -20: score -= 30
        
        # Options scoring
        if opt:
            if opt['pcr'] < 0.5: score += 25  # Bullish
            elif opt['pcr'] < 0.7: score += 15
            if opt['call_vol'] > 50000: score += 20
            elif opt['call_vol'] > 20000: score += 10
        
        total = score + squeeze_score
        
        return {
            'ticker': ticker,
            'price': round(price, 2),
            'day_chg': round(day_chg, 1),
            'week_chg': round(week_chg, 1),
            'vol_ratio': round(vol_ratio, 1),
            'short_float': short_float,
            'short_ratio': short_ratio,
            'squeeze_score': squeeze_score,
            'options': opt,
            'total': total,
            'status': 'REJECT' if day_chg < -10 or week_chg < -20 else 'OK'
        }
    except Exception as e:
        return None

def run_scanner(post=True):
    """Run full scanner"""
    TICKERS = [
        "MPT","OCGN","CTXR","NIO","MARA","BCTX","DNA","GNPX","NAUT","ABSI",
        "BCAB","ENPH","MUR","XPEV","OPK","NERV","SOUN","PLTR","RIVN","AI",
        "SOFI","UPST","RBLX","BBIG","MSTR","COIN","RIOT","NVAX","LCID"
    ]
    
    results = []
    for t in TICKERS:
        r = analyze(t)
        if r and r['total'] > 30 and r['status'] == 'OK':
            results.append(r)
        time.sleep(0.2)
    
    results.sort(key=lambda x: x['total'], reverse=True)
    
    # Build output
    print("=" * 80)
    print("SHORT SQUEEZE SCANNER v7 - WITH OPTIONS FLOW")
    print("=" * 80)
    print(f"{'TICKER':<8} {'PRICE':<8} {'SCORE':<6} {'DAY':<8} {'WEEK':<8} {'SHORT%':<8} {'PCR':<6}")
    print("-" * 80)
    
    for r in results[:12]:
        si = f"{r['short_float']*100:.1f}%" if r['short_float'] else "N/A"
        pcr = r['options']['pcr'] if r['options'] else "N/A"
        print(f"{r['ticker']:<8} ${r['price']:<7} {r['total']:<6} {r['day_chg']:+7.1f}% {r['week_chg']:+7.1f}% {si:<8} {pcr}")
    
    print("\n=== TOP WITH OPTIONS ===")
    for r in results[:5]:
        opt = r['options']
        print(f"\n{r['ticker']}: ${r['price']} | Score: {r['total']}")
        if opt:
            print(f"  Options: {opt['call_vol']:,} calls | {opt['put_vol']:,} puts | PCR: {opt['pcr']}")
            print(f"  Signal: {'🟢 BULLISH' if opt['pcr'] < 0.5 else '🔴 BEARISH' if opt['pcr'] > 1.3 else '⚪ NEUTRAL'}")
        print(f"  Short: {r['short_float']*100:.1f}% float | {r['short_ratio']:.1f} DTC")
    
    print(f"\nTotal: {len(results)} candidates")
    
    # Post to Discord
    if post:
        msg = "**🔍 SHORT SQUEEZE + OPTIONS SCAN**\n```\n"
        msg += f"{'TICKER':<8} {'PRICE':<8} {'SCORE':<6} {'DAY':<8} {'PCR':<6}\n"
        for r in results[:8]:
            pcr = r['options']['pcr'] if r['options'] else "-"
            msg += f"{r['ticker']:<8} ${r['price']:<7} {r['total']:<6} {r['day_chg']:+7.1f}% {pcr}\n"
        msg += "```"
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=10)
        except:
            pass
    
    return results

if __name__ == "__main__":
    run_scanner(post=True)
