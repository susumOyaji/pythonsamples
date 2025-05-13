from flask import Flask, jsonify, render_template, request
import yfinance as yf
import json
import os

#app = Flask(__name__)
app = Flask(__name__, template_folder='.')

DATA_FILE = "data.json"

# JSONファイルから登録データを読み込む
def load_custom_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# JSONファイルへ登録データを保存
def save_custom_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/market')
def get_market_data():
    data = {}
    tickers = {
        "usd_jpy": yf.Ticker("USDJPY=X"),
        "dow": yf.Ticker("^DJI"),
        "nikkei": yf.Ticker("^N225"),
        
    }

    for key, ticker in tickers.items():
        info = ticker.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("regularMarketPreviousClose")
        try:
            price_diff = price - prev_close if price and prev_close else None
        except:
            price_diff = None

        data[key] = {
            "price": price,
            "name": info.get("shortName", key),
            "previous_close": prev_close,
            "price_diff": price_diff,
        }

    # カスタム登録データを読み込み、損益計算
    custom_entries = load_custom_data()
    for entry in custom_entries:
        symbol = entry["symbol"]
        shares = entry["shares"]
        unit_price = entry["unit_price"]
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            profit = (current_price - unit_price) * shares if current_price else None
            data[f"custom_{symbol}"] = {
                "name": info.get("shortName", symbol),
                "price": current_price,
                "shares": shares,
                "unit_price": unit_price,
                "profit": profit
            }
        except:
            continue

    return jsonify(data)

@app.route('/api/add', methods=['POST'])
def add_stock_entry():
    try:
        body = request.get_json()
        symbol = body["symbol"].strip()
        shares = int(body["shares"])
        unit_price = float(body["unit_price"])
        assert symbol and shares > 0 and unit_price > 0
    except:
        return jsonify({"error": "入力が不正です"}), 400

    new_entry = {"symbol": symbol, "shares": shares, "unit_price": unit_price}
    data = load_custom_data()
    data.append(new_entry)
    save_custom_data(data)
    return jsonify({"message": "登録しました"})


@app.route('/api/update', methods=['POST'])
def update_stock_entry():
    try:
        body = request.get_json()
        symbol = body["symbol"].strip()
        shares = int(body["shares"])
        unit_price = float(body["unit_price"])
        assert symbol and shares > 0 and unit_price > 0
    except:
        return jsonify({"error": "入力が不正です"}), 400

    data = load_custom_data()
    found = False
    for entry in data:
        if entry["symbol"] == symbol:
            entry["shares"] = shares
            entry["unit_price"] = unit_price
            found = True
            break

    if not found:
        return jsonify({"error": "対象の銘柄が見つかりません"}), 404

    save_custom_data(data)
    return jsonify({"message": "更新しました"})


if __name__ == '__main__':
    app.run(debug=True)
