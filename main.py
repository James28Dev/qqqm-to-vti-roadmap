import yfinance as yf
import pandas as pd
import requests
import os

# ลิสต์รายการหุ้น
STOCKS = ["NVDA", "RKLB"]
LINE_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')
PB_TOKEN = os.getenv('PUSHBULLET_TOKEN')

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    # สูตร Wilder's Smoothing (EWMA)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_stock_data(symbol, interval="1d"):
    period = "1y" if interval == "1d" else "2y"
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if not df.empty:
        df['RSI'] = calculate_rsi(df['Close'])
        return df['RSI'].iloc[-1]
    return None

def get_rsi_report():
    report = "🚀 James's Investment Sentinel\n"
    for s in STOCKS:
        try:
            rsi_day = get_stock_data(s, "1d")
            rsi_week = get_stock_data(s, "1wk")
            
            if rsi_day is None or rsi_week is None: continue
            
            status = ""              
            # ปรับ Logic ให้คมขึ้นสำหรับคนไม่กลัวตกรถ
            if rsi_week <= 40 and rsi_day <= 30:
            # จุดนี้คือ Buy-the-dip > 20% ตามนโยบาย
                status = "🚨 Sniper: FULL SEND! (ไม้ 3)"
            elif rsi_week <= 45 and rsi_day <= 35:
            # จุดพักฐานใหญ่ที่เริ่มน่าสนใจ
                status = "🔫 Sniper: ไม้ 1"
            elif rsi_day <= 30:
                # Week ยังไม่ลง แต่ Day ลงมาแรงมาก (Short-term Panic)
                status = "⚡ Sniper: แหย่เท้า พอได้ซื้อ"
            else:
                status = "🚫 Sniper: กลับไปนอน"
            
            report += f"\n📌 {s}\nRSI Day: {rsi_day:.2f} | RSI Week: {rsi_week:.2f}\n{status}\n"
            
        except Exception as e:
            report += f"\n❌ {s}: Data Error"
            
    return report

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    return requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    # ส่งเข้า Line
    if LINE_TOKEN and USER_ID:
        msg = get_rsi_report()
        send_line(msg)

    # ส่งเข้า Pushbullet
    if PB_TOKEN:
        send_pushbullet("📈 James's RSI Alert", msg)
