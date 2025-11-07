from fastapi import FastAPI, HTTPException
from database import SessionLocal, User, Deposit
from utils import calc_profit
from datetime import datetime, timedelta

app = FastAPI()
db = SessionLocal()

MIN_AMOUNTS = {
    "BTC": 0.0003,
    "ETH": 0.009,
    "BNB": 0.032,
    "TRX": 100
}

@app.post("/register/{telegram_id}")
def register_user(telegram_id: int):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
    return {"message": "User registered", "telegram_id": telegram_id}

@app.post("/deposit/{telegram_id}")
def create_deposit(telegram_id: int, coin: str, amount: float):
    coin = coin.upper()
    if coin not in MIN_AMOUNTS:
        raise HTTPException(400, "Unsupported coin")
    if amount < MIN_AMOUNTS[coin]:
        raise HTTPException(400, f"Minimum deposit for {coin} is {MIN_AMOUNTS[coin]}")
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    deposit = Deposit(user_id=user.id, coin=coin, amount=amount)
    db.add(deposit)
    db.commit()
    return {"message": f"{amount} {coin} deposited successfully"}

@app.get("/account/{telegram_id}")
def get_account(telegram_id: int):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    deposits = db.query(Deposit).filter(Deposit.user_id == user.id).all()
    total = 0
    data = []
    for d in deposits:
        d = calc_profit(d)
        db.commit()
        total += d.amount + d.profit
        data.append({
            "coin": d.coin,
            "amount": d.amount,
            "profit": d.profit
        })
    return {"telegram_id": telegram_id, "total_balance": total, "deposits": data}

@app.post("/withdraw/{telegram_id}")
def withdraw_request(telegram_id: int):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    deposits = db.query(Deposit).filter(Deposit.user_id == user.id, Deposit.withdrawn == 0).all()
    total = 0
    now = datetime.utcnow()
    for d in deposits:
        if now - d.created_at >= timedelta(hours=72):
            total += d.amount + d.profit
            d.withdrawn = 1
    db.commit()
    if total == 0:
        raise HTTPException(400, "No withdrawable balance yet")
    return {"message": "Withdraw request accepted", "amount": total}
