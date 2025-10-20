# Raketradar

Dette er din Raketradar-agent 🚀

## Hvad den gør
- Scanner NASDAQ vækstaktier + mikro/small cap
- Sender Telegram-besked for alle potentielle raketsignaler
- Logger alle signaler i CSV (`/app/data/raketradar_log.csv`)
- Kører automatisk via Docker/Render

## Filer
- `app/raketradar.py` → Hovedscript, som scanner aktier
- `app/entrypoint.sh` → Starter scriptet
- `app/.env.example` → Eksempel på miljøvariabler (sæt din Telegram-token her)
- `Dockerfile` → Til at bygge container på Render
- `requirements.txt` → Python-pakker der skal installeres

## Deployment på Render
1. Upload hele mappen som et repository til GitHub
2. Opret en ny Web Service på Render med type: Docker
3. Indsæt `TELEGRAM_TOKEN` (din bot token) og `TELEGRAM_CHAT_ID` (`1272304432`) som Environment Variables
4. Deploy, og agenten begynder automatisk at sende beskeder
