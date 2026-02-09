import yfinance as yf
import pandas_ta as ta
import requests
import os

# รายการหุ้นที่คุณถือและเฝ้าจังหวะ [cite: 2026-02-04]
STOCKS = ["NVDA", "RKLB", "QQQM"]
LINE_TOKEN = os.getenv('MmqnTse/qKOyGjJsX4scf/2GJIIuiIWdj5af1YqJiYXXGIw3wZMS5rW9QlpVS5buXV7YDxSqk9LlSCTX0gyyaNar03Ks6LpV5sClnaVo5xz19ewJfGTOgc2uH95lU6K3ab9IQfptbEVGVmJJyhJflwdB04t89/1O/w1cDnyilFU=')
USER_ID = os.getenv('U0516ce932a17cd9201f385d753876c8e')

def get_rsi_report():
    report = "💹 James's RSI Sentinel\n"
    for s in STOCKS:
        try:
            # ดึงข้อมูล Daily และคำนวณ RSI
            df_d = yf.download(s, period="1y", interval="1d", progress=False)
            rsi_d = ta.rsi(df_d['Close'], length=14).iloc[-1]
            
            # ดึงข้อมูล Weekly และคำนวณ RSI
            df_w = yf.download(s, period="2y", interval="1wk", progress=False)
            rsi_w = ta.rsi(df_w['Close'], length=14).iloc[-1]
            
            report += f"\n🔹 {s}\n   D: {rsi_d:.2f} | W: {rsi_w:.2f}"
            
            # สัญญาณแจ้งเตือนตามนโยบาย Buy-the-dip [cite: 2026-02-04]
            if rsi_d < 35:
                report += "\n   🚨 ALERT: OVERSOLD (Daily)!"
            else:
                report += "\n   ✅ Normal (Daily)"
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
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    msg = get_rsi_report()
    if LINE_TOKEN and USER_ID:
        send_line(msg)