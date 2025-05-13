from flask import Flask, jsonify, render_template, request
import yfinance as yf
import json
import os
import re  # 正規表現用モジュールを追加

app = Flask(__name__, template_folder='.')

DATA_FILE = "data.json"

# JSONファイルから登録データを読み込む
def load_custom_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  # ファイルが空または不正なJSONの場合は空のリストを返す
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
        try:
            info = ticker.info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("regularMarketPreviousClose")
            price_diff = price - prev_close if price and prev_close else None
            data[key] = {
                "price": price,
                "name": info.get("shortName", key),
                "previous_close": prev_close,
                "price_diff": price_diff,
            }
        except Exception as e:
            print(f"Error fetching data for {key}: {e}")
            data[key] = {"price": None, "name": key, "previous_close": None, "price_diff": None, "error": "データ取得エラー"}

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
                "name": info.get("shortName", symbol) or symbol,
                "price": current_price,
                "shares": shares,
                "unit_price": unit_price,
                "profit": profit,
            }
        except Exception as e:
            print(f"Error fetching data for custom symbol {symbol}: {e}")
            data[f"custom_{symbol}"] = {
                "name": symbol,
                "price": None,
                "shares": shares,
                "unit_price": unit_price,
                "profit": None,
                "error": "株価取得エラー"
            }

    return jsonify(data)

@app.route('/api/add', methods=['POST'])
def add_stock_entry():
    try:
        body = request.get_json()
        symbol = body["symbol"].strip()
        shares = int(body["shares"])
        unit_price = float(body["unit_price"])

        if not symbol:
            return jsonify({"error": "企業コードを入力してください"}), 400
        if not re.match(r"^[a-zA-Z0-9\.\-]+$", symbol): # 簡単なシンボルフォーマットチェック
            return jsonify({"error": "企業コードの形式が正しくありません"}), 400
        if shares <= 0:
            return jsonify({"error": "株数は1以上の整数を入力してください"}), 400
        if unit_price <= 0:
            return jsonify({"error": "購入単価は0より大きい数値を入力してください"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "入力値が不正です"}), 400
    except KeyError:
        return jsonify({"error": "必要なパラメータが不足しています"}), 400

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
        original_symbol = body.get("originalSymbol") # 元のシンボルを取得

        if not symbol:
            return jsonify({"error": "企業コードを入力してください"}), 400
        if not re.match(r"^[a-zA-Z0-9\.\-]+$", symbol): # 簡単なシンボルフォーマットチェック
            return jsonify({"error": "企業コードの形式が正しくありません"}), 400
        if shares <= 0:
            return jsonify({"error": "株数は1以上の整数を入力してください"}), 400
        if unit_price <= 0:
            return jsonify({"error": "購入単価は0より大きい数値を入力してください"}), 400
        if not original_symbol:
            return jsonify({"error": "更新に必要な情報が不足しています"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "入力値が不正です"}), 400
    except KeyError:
        return jsonify({"error": "必要なパラメータが不足しています"}), 400

    data = load_custom_data()
    found_index = -1
    for i, entry in enumerate(data):
        if entry["symbol"] == original_symbol:
            found_index = i
            break

    if found_index == -1:
        return jsonify({"error": "対象の銘柄が見つかりません"}), 404

    data[found_index]["symbol"] = symbol
    data[found_index]["shares"] = shares
    data[found_index]["unit_price"] = unit_price

    save_custom_data(data)
    return jsonify({"message": "更新しました"})


if __name__ == '__main__':
    app.run(debug=True)