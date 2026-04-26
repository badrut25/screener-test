import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

def rational_quadratic_kernel(series, h=8, r=8.0, x=25):
    """Menghitung Nadaraya-Watson dengan Rational Quadratic Kernel"""
    weights = np.zeros(x)
    for i in range(x):
        weights[i] = (1 + (i**2) / (2 * r * (h**2))) ** (-r)
    weights = weights / np.sum(weights)
    return series.rolling(window=x).apply(lambda vals: np.dot(vals[::-1], weights), raw=True)

def run_screener(tickers):
    bullish_group = []
    bearish_group = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if df.empty: continue
            
            # Hitung Kernel & Syarat
            df['Kernel'] = rational_quadratic_kernel(df['Close'], h=8, r=8.0, x=25)
            df['Is_Bullish_Rate'] = df['Kernel'] > df['Kernel'].shift(1)
            df['Is_Bearish_Rate'] = df['Kernel'] < df['Kernel'].shift(1)
            
            df['Bullish_Change'] = df['Is_Bullish_Rate'] & df['Is_Bearish_Rate'].shift(1)
            df['Bearish_Change'] = df['Is_Bearish_Rate'] & df['Is_Bullish_Rate'].shift(1)
            
            # Cek hari terakhir
            if df['Bullish_Change'].iloc[-1]:
                bullish_group.append(ticker.replace('.JK', ''))
            elif df['Bearish_Change'].iloc[-1]:
                bearish_group.append(ticker.replace('.JK', ''))
                
        except Exception as e:
            pass
            
    return bullish_group, bearish_group

# Eksekusi (Tambahkan saham lain dengan akhiran .JK)
daftar_saham = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "AMMN.JK", "GOTO.JK", "TLKM.JK", "ASII.JK", "BREN.JK"]
hijau, merah = run_screener(daftar_saham)

# Generate File index.html
waktu_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
html_content = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screener Lorentzian Kernel</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9; }}
        h1 {{ text-align: center; color: #333; }}
        .update-time {{ text-align: center; color: #777; margin-bottom: 30px; }}
        .container {{ display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }}
        .box {{ background: white; border: 1px solid #ddd; padding: 20px; border-radius: 8px; width: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .green-title {{ color: #2e7d32; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; }}
        .red-title {{ color: #c62828; border-bottom: 2px solid #c62828; padding-bottom: 10px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ padding: 8px 0; border-bottom: 1px solid #eee; font-size: 18px; font-weight: bold; text-align: center; }}
    </style>
</head>
<body>
    <h1>Screener Kernel Regression 👑</h1>
    <div class="update-time">Terakhir Diperbarui: {waktu_update} (UTC)</div>
    
    <div class="container">
        <div class="box">
            <h2 class="green-title">🟢 Potensi BUY<br><small>(Merah ke Hijau)</small></h2>
            <ul>
                {''.join([f"<li>{t}</li>" for t in hijau]) if hijau else "<li>Tidak ada sinyal</li>"}
            </ul>
        </div>
        
        <div class="box">
            <h2 class="red-title">🔴 Potensi SELL<br><small>(Hijau ke Merah)</small></h2>
            <ul>
                {''.join([f"<li>{t}</li>" for t in merah]) if merah else "<li>Tidak ada sinyal</li>"}
            </ul>
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)

print("Berhasil! File index.html telah digenerate.")
