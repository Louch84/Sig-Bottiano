#!/usr/bin/env python3
"""Dashboard - Web interface for everything"""
from flask import Flask, jsonify, render_template_string
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sig Botti Dashboard</title>
    <style>
        body { font-family: monospace; background: #111; color: #0f0; padding: 20px; }
        h1 { color: #0f0; }
        .card { background: #222; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .green { color: #0f0; }
        .red { color: #f00; }
        .blue { color: #00f; }
    </style>
</head>
<body>
    <h1>🦁🦈 Sig Botti Dashboard 🧠🥷</h1>
    <p>Updated: {{ time }}</p>
    
    <div class="card">
        <h2>📈 MPT Stock</h2>
        <p class="green">Price: ${{ mpt_price }}</p>
        <p>Volume: {{ mpt_vol }}x</p>
    </div>
    
    <div class="card">
        <h2>📊 Squeeze Scanner</h2>
        <p>MPT: {{ mpt_score }}/100</p>
        <p>LCID: {{ lcid_score }}/100</p>
    </div>
    
    <div class="card">
        <h2>🤖 System Status</h2>
        <p>Learning: Nonstop</p>
        <p>Posts: 6x daily</p>
        <p>Tools: {{ tools_count }}</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Get MPT data
    try:
        mpt = yf.Ticker("MPT")
        info = mpt.info
        mpt_price = info.get('currentPrice', 'N/A')
        mpt_vol = round(info.get('volume', 0) / info.get('averageVolume', 1), 1)
        mpt_score = 80
        lcid_score = 50
    except:
        mpt_price = "Error"
        mpt_vol = "Error"
        mpt_score = "Error"
        lcid_score = "Error"
    
    import os
    tools_count = len([f for f in os.listdir('code') if f.endswith('.py')])
    
    return render_template_string(HTML, 
                                  time=datetime.now().strftime("%H:%M:%S"),
                                  mpt_price=mpt_price,
                                  mpt_vol=mpt_vol,
                                  mpt_score=mpt_score,
                                  lcid_score=lcid_score,
                                  tools_count=tools_count)

@app.route('/api/status')
def api():
    return jsonify({
        "status": "running",
        "tools": 28,
        "learning": True
    })

if __name__ == "__main__":
    print("Starting dashboard on http://localhost:5000")
    app.run(debug=True, port=5000)
