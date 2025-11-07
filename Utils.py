from datetime import datetime, timedelta

def calc_profit(deposit):
    now = datetime.utcnow()
    diff = (now - deposit.last_update).total_seconds() / 60
    intervals = int(diff // 15)
    if intervals > 0:
        profit = deposit.amount * 0.007 * intervals
        deposit.profit += profit
        deposit.last_update = now
    return deposit
