# OceanVest Backend

FastAPI backend for the OceanVest Telegram Mini App.

## Features
- User auto registration via Telegram ID
- Deposit tracking for BTC, ETH, BNB, TRX
- Profit calculation (0.7% every 15 minutes)
- Withdrawal lock (72 hours)
- SQLite database support

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload# oceanvest-backend
