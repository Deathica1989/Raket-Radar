# Raketradar ZIP generator
# Dette er en tekstlig repræsentation af alle filer du skal bruge i ZIP.

# Struktur:
# Raketradar.zip/
# ├── app/
# │   ├── raketradar.py
# │   ├── entrypoint.sh
# │   └── .env.example
# ├── Dockerfile
# ├── requirements.txt
# └── README.md

# === app/raketradar.py ===
raketradar_py = """
#!/usr/bin/env python3
"""
Hybrid Raketradar - NASDAQ vækst + mikrocap
"""
import os
import time
from datetime import datetime
import pandas as pd
import yfinance as yf
from ta.trend import SMAIndicator
from telegram import Bot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger("raketradar")

TICKERS = os.getenv('TICKERS', 'NVDA,PLTR,AMD,SMCI,TALK')
TICKERS = [t.strip().upper() for t in TICKERS.split(',') if t.strip()]
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '3600'))
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
LOG_CSV = os.getenv('LOG_CSV', '/app/data/raketradar_log.csv')
MA_WINDOW = int(os.getenv('MA_WINDOW', '20'))
VOL_WINDOW = int(os.getenv('VOL_WINDOW', '20'))

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("TELEGRAM_TOKEN eller TELEGRAM_CHAT_ID ikke sat i env. Afslutter.")
    raise SystemExit("Telegram credentials mangler")

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        logger.info("Telegram sendt: %s", text[:120])
    except Exception as e:
        logger.exception("Fejl ved sending af Telegram: %s", e)

def get_intraday_df(ticker, period="10d", interval="60m"):
    try:
        d = yf.download(tickers=ticker, period=period, interval=interval, progress=False, threads=False)
        d.dropna(inplace=True)
        return d
    except Exception as e:
        logger.exception("Fejl ved hent af data for %s: %s", ticker, e)
        return pd.DataFrame()

def analyze_ticker(ticker):
    df = get_intraday_df(ticker, period="10d", interval="60m")
    if df.empty or len(df) < max(MA_WINDOW, VOL_WINDOW) + 2:
        return None

    df['ma'] = SMAIndicator(df['Close'], window=MA_WINDOW).sma_indicator()
    df['vol_avg'] = df['Volume'].rolling(VOL_WINDOW).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    price = float(latest['Close'])
    ma = float(latest['ma']) if not pd.isna(latest['ma']) else None
    vol = int(latest['Volume'])
    vol_avg = int(latest['vol_avg']) if not pd.isna(latest['vol_avg']) else 0

    score = 0
    reasons = []

    if ma and price > ma and prev['Close'] <= prev['ma']:
        score += 1
        reasons.append('Pris brød over MA')

    if vol_avg > 0 and vol >= 2 * vol_avg:
        score += 1
        reasons.append(f'Volumen {vol} >= 2× ({vol_avg})')

    return {
        'ticker': ticker,
        'price': price,
        'ma': ma,
        'vol': vol,
        'vol_avg': vol_avg,
        'score': score,
        'reasons': reasons,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

def append_log(row, path=LOG_CSV):
    df = pd.DataFrame([row])
    header = not os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, mode='a', header=header, index=False)

if __name__ == '__main__':
    logger.info('Starter Raketradar med tickers: %s', ','.join(TICKERS))
    while True:
        try:
            for t in TICKERS:
                res = analyze_ticker(t)
                if not res:
                    continue
                append_log(res)
                # Sender besked for alle signaler
                if res['score'] > 0:
                    msg = f"[RAKET-SIGNAL] {res['ticker']} | pris {res['price']:.2f} | score {res['score']} | " + "; ".join(res['reasons'])
                    send_telegram(msg)
        except Exception as e:
            logger.exception('Fejl i hoved-løkke: %s', e)
        time.sleep(CHECK_INTERVAL_SECONDS)
"""

# === app/entrypoint.sh ===
entrypoint_sh = """
#!/bin/sh
python raketradar.py
"""

# === app/.env.example ===
env_example = """
# Skift disse til dine egne værdier
TICKERS=NVDA,PLTR,AMD,SMCI,TALK
CHECK_INTERVAL_SECONDS=3600
TELEGRAM_TOKEN=DIN_TOKEN_HER
TELEGRAM_CHAT_ID=1272304432
LOG_CSV=/app/data/raketradar_log.csv
MA_WINDOW=20
VOL_WINDOW=20
"""

# === Dockerfile ===
dockerfile = """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
WORKDIR /app/app
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
"""

# === requirements.txt ===
requirements_txt = """
yfinance==0.2.27
pandas==2.2.2
ta==0.12.0
python-telegram-bot==20.3
numpy==1.26.2
"""

# === README.md ===
readme_md = """
# Raketradar

Denne ZIP indeholder færdigopsat Raketradar:
- Scanner NASDAQ vækst + mikro/small cap
- Sender Telegram-besked ved alle signaler
- Dockerfile til nem deployment (Render.com)
- .env.example til dine nøgler

Se README i zip for fuld Render-opsætning og instruktioner.
"""
