import yfinance as yf
import pandas as pd
import requests
import os

# รายชื่อหุ้นในพอร์ตของเจมส์ [cite: 2026-02-04]
STOCKS = ["NVDA", "ASML", "TSMC", "GOOGL", "QQQM", "JEPQ"]
LINE_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_rsi_report():
    report = "💹 James's RSI Sentinel (Pure Pandas)\n"
    for s in STOCKS:
        try:
            df = yf.download(s, period="1y", interval="1d", progress=False)
            if df.empty: continue
            
            # คำนวณ RSI วันล่าสุด
            df['RSI'] = calculate_rsi(df['Close'])
            rsi = df['RSI'].iloc[-1]
            
            report += f"\n🔹 {s}: {rsi:.2f}"
            
            # เงื่อนไข Buy-the-dip ตามนโยบาย [cite: 2026-02-04]
            if rsi < 35:
                report += " 🚨 BUY DIP!"
            else:
                report += " ✅"
        except Exception as e:
            report += f"\n❌ {s}: Data Error"
            
    return report

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    return requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    if not LINE_TOKEN or not USER_ID:
        print("❌ Error: Missing LINE Secrets")
    else:
        msg = get_rsi_report()
        print(msg) # แสดงผลใน GitHub Log
        response = send_line(msg)
        print(f"Status Code: {response.status_code}")