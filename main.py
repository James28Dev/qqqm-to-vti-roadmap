import yfinance as yf
import pandas as pd
import requests
import os

# ลิสต์รายการหุ้นใหม่ [cite: 2026-02-10]
STOCKS = ["NVDA", "RKLB", "QQQM"]
LINE_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_stock_data(symbol, interval="1d"):
    period = "1y" if interval == "1d" else "2y"
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if not df.empty:
        df['RSI'] = calculate_rsi(df['Close'])
        return df['RSI'].iloc[-1]
    return None

def get_rsi_report():
    report = "🚀 James's Investment Sentinel (08:00 AM)\n"
    for s in STOCKS:
        try:
            rsi_day = get_stock_data(s, "1d")
            rsi_week = get_stock_data(s, "1wk")
            
            if rsi_day is None or rsi_week is None: continue
            
            status = ""
            # Logic: เช็คสัญญาณซื้อตามเงื่อนไขเจมส์ [cite: 2026-02-10]
            if rsi_week <= 40 and rsi_day <= 35:
                status = "🚨 สัญญาณ: **ต้องซื้อ!**"
            elif rsi_week <= 45 and rsi_day <= 35:
                status = "⚠️ สัญญาณ: เฝ้าระวัง"
            else:
                status = "⏳ สัญญาณ: อาจจะยังนะ"
            
            report += f"\n📌 {s}\n- RSI Day: {rsi_day:.2f}\n- RSI Week: {rsi_week:.2f}\n{status}\n"
            
        except Exception as e:
            report += f"\n❌ {s}: Data Error"
            
    return report

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    return requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    if LINE_TOKEN and USER_ID:
        msg = get_rsi_report()
        send_line(msg)