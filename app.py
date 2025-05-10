import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

ticker_symbols = ['3930.T', '7203.T', '6758.T']  # 例：HATENA (3930.T), トヨタ (7203.T), ソニー (6758.T)
tickers = [yf.Ticker(symbol) for symbol in ticker_symbols]
price_histories = {symbol: [] for symbol in ticker_symbols}
time_history = []

plt.ion()  # Turn on interactive mode

fig, ax = plt.subplots()
lines = {}
for symbol in ticker_symbols:
    line, = ax.plot([], [], label=symbol)
    lines[symbol] = line

ax.set_xlabel('Time')
ax.set_ylabel('Price (JPY)')
ax.set_title('Real-time Stock Prices')
ax.legend()
plt.grid(True)

def update_plot():
    current_time = pd.Timestamp.now()
    time_history.append(current_time)
    for symbol, ticker in zip(ticker_symbols, tickers):
        info = ticker.info
        if 'currentPrice' in info:
            current_price = info['currentPrice']
            price_histories[symbol].append(current_price)
            lines[symbol].set_xdata(time_history)
            lines[symbol].set_ydata(price_histories[symbol])
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()

if __name__ == '__main__':
    print("リアルタイム株価グラフを表示します。ウィンドウを閉じると終了します。")
    try:
        while True:
            update_plot()
            time.sleep(5)  # 5秒ごとに更新
    except KeyboardInterrupt:
        print("停止しました。")
    finally:
        plt.ioff()
        plt.show()