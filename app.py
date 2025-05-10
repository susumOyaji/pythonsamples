import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time
from IPython import display

ticker_symbol = '6758.T'
ticker = yf.Ticker(ticker_symbol)
price_history = []
time_history = []

plt.ion()  # Turn on interactive mode

fig, ax = plt.subplots()
line, = ax.plot([], [], label=ticker_symbol)
ax.set_xlabel('Time')
ax.set_ylabel('Price (JPY)')
ax.set_title(f'Real-time Stock Price of {ticker_symbol}')
ax.legend()
plt.grid(True)

def update_plot():
    info = ticker.info
    if 'currentPrice' in info:
        current_price = info['currentPrice']
        current_time = pd.Timestamp.now()
        price_history.append(current_price)
        time_history.append(current_time)
        line.set_xdata(time_history)
        line.set_ydata(price_history)
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