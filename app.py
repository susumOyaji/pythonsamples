from flask import Flask, render_template, request, jsonify
import yfinance as yf
import time
import json

app = Flask(__name__)

def get_realtime_price_with_change(ticker_symbol):
    """指定されたティッカーシンボルの最新株価と前日比を取得します。"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.info
        if 'currentPrice' in data and 'regularMarketChange' in data and 'regularMarketChangePercent' in data and 'regularMarketTime' in data:
            price = data['currentPrice']
            timestamp = data['regularMarketTime']
            change = data['regularMarketChange']
            change_percent = data['regularMarketChangePercent']
            return price, timestamp, change, change_percent
        else:
            return None, None, None, None
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None, None, None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    stock_list = []
    if request.method == 'POST':
        try:
            local_storage_data = request.form.get('stock_data')
            if local_storage_data:
                stocks = json.loads(local_storage_data)
                for stock in stocks:
                    ticker = stock.get('ticker')
                    shares = stock.get('shares')
                    purchase_price = stock.get('purchase_price')
                    if ticker:
                        price, timestamp, change, change_percent = get_realtime_price_with_change(f"{ticker}.T")
                        formatted_timestamp = time.strftime('%Y-%m-%d %H:%M:%S') if timestamp else "取得できませんでした"
                        stock_info = {
                            'ticker': ticker,
                            'price': f"{price:.2f}" if price is not None else "取得できませんでした",
                            'timestamp': formatted_timestamp,
                            'change': f"{change:.2f}" if change is not None else "取得できませんでした",
                            'change_percent': f"{change_percent:.2f}" if change_percent is not None else "取得できませんでした",
                            'shares': shares,
                            'purchase_price': purchase_price
                        }
                        stock_list.append(stock_info)
            return jsonify({'stocks': stock_list})
        except json.JSONDecodeError:
            error_message = "ローカルストレージデータの形式が正しくありません。"
            return render_template('index.html', error=error_message)
        except Exception as e:
            error_message = f"データの処理中にエラーが発生しました: {e}"
            return render_template('index.html', error=error_message)

    return render_template('index.html', stocks=stock_list)

if __name__ == '__main__':
    app.run(debug=True)