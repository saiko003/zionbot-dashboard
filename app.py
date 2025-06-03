from flask import Flask, render_template, jsonify
import requests
import random

app = Flask(__name__)

BASE_URL = "https://fapi.binance.com"
coin_list = [
    "DOGEUSDT", "AVAXUSDT", "WIFUSDT", "ORDIUSDT", "SOLUSDT",
    "MATICUSDT", "1000PEPEUSDT", "SOPHUSDT", "HYPEUSDT", "NOTUSDT"
]

strategies = ["Scalping", "Trend", "SMC"]

def get_price(symbol):
    try:
        res = requests.get(f"{BASE_URL}/fapi/v1/ticker/price?symbol={symbol}")
        return float(res.json()['price'])
    except:
        return None

def simulate_score(strategy):
    base = {
        "Scalping": 80,
        "Trend": 75,
        "SMC": 70
    }[strategy]
    return round(random.uniform(base, base + 15), 2)

def calculate_targets(price, direction, strength):
    if direction == "BUY":
        tp1 = round(price * (1 + 0.01 * (strength / 10)), 4)
        tp2 = round(price * (1 + 0.015 * (strength / 10)), 4)
        tp3 = round(price * (1 + 0.025 * (strength / 10)), 4)
        sl = round(price * (1 - 0.008 * (strength / 10)), 4)
    else:
        tp1 = round(price * (1 - 0.01 * (strength / 10)), 4)
        tp2 = round(price * (1 - 0.015 * (strength / 10)), 4)
        tp3 = round(price * (1 - 0.025 * (strength / 10)), 4)
        sl = round(price * (1 + 0.008 * (strength / 10)), 4)
    return tp1, tp2, tp3, sl

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan")
def scan():
    results = {}
    for strat in strategies:
        best_score = 0
        best_data = None
        for coin in coin_list:
            price = get_price(coin)
            if not price:
                continue
            score = simulate_score(strat)
            direction = "BUY" if score > 82 else "SELL" if score < 73 else "NEUTRAL"
            if direction == "NEUTRAL":
                continue
            if score > best_score:
                tp1, tp2, tp3, sl = calculate_targets(price, direction, score)
                best_score = score
                best_data = {
                    "coin": coin,
                    "strategy": strat,
                    "price": price,
                    "score": score,
                    "direction": direction,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "sl": sl
                }
        if best_data:
            results[strat] = best_data
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
