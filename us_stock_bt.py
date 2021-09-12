import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
plt.style.use('bmh')
import requests, lxml
st.set_option('deprecation.showPyplotGlobalUse', False) # pyplot那邊很囉嗦

ark = pd.read_html('https://cathiesark.com/ark-funds-combined/complete-holdings')[0]['Ticker'][1:31].to_list()
web = requests.get('https://www.slickcharts.com/sp500',
                   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}).text
sid1 = pd.read_html(web)[0]['Symbol'].apply(lambda x: x.replace('.', '-')).to_list()
sid2 = pd.read_html('https://finance.yahoo.com/screener/predefined/day_gainers?offset=0&count=100')[0].Symbol.to_list()
sid3 = pd.read_html('https://finance.yahoo.com/screener/predefined/small_cap_gainers?offset=0&count=100')[0].Symbol.to_list()
sid4 = pd.read_html('https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100')[0].Symbol.to_list()
sid5 = pd.read_html('https://finance.yahoo.com/screener/predefined/growth_technology_stocks')[0].Symbol.to_list()
sid6 = pd.read_html('https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks?offset=0&count=100')[0].Symbol.to_list()
sid7 = pd.read_html('https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset=0&count=100')[0].Symbol.to_list()
sid8 = pd.read_html('https://finance.yahoo.com/screener/predefined/aggressive_small_caps?offset=0&count=100')[0].Symbol.to_list()
backtest = ['ZM','AVID','BGFV','TIGR','APPS','ENPH','CDLX','NTP','SBOW','NIO','ZS','PLUG','MARA','PENN','HIMX','DAC','BILI','TGI','THO','TSLA','TCS','MRNA','SQ']
# 近一兩季太鳥 先不要 'MVIS','MSTR','SPWR','DQ','FSLY'
watchlist_us = list(set(ark + sid1 + sid2 + sid3 + sid4 + sid5 + sid6 + sid7 + sid8 + backtest))


def crazy_dog_backtest(ticker, start = None, end = None, prior_high = 22, stp = 8, log = False, plot = False):
    df = yf.Ticker(ticker).history(start = start, end = end).iloc[:,:5]
    cond1 = (df['Close'] * 1.03 > df['High'].rolling(prior_high).max())
    cond2 = ((df['Close'] - df['Open']) > abs(df['Open'] - df['Close']).rolling(10).mean()*2.5)
    cond3 = (df['Volume'] > df['Volume'].rolling(5).mean() * 1.3)
    duo_ma = df['Close'].rolling(5).mean() >= df['Close'].rolling(10).mean()
    cond4 = ((duo_ma == True) & ((duo_ma != duo_ma.shift()).rolling(5).sum() == 1))
    buy = pd.concat([cond1, cond2, cond3, cond4], axis = 1)
    buy_raw = buy[buy.sum(axis = 1) >= 3].index

    global date_buy, date_sell
    date_buy, date_sell = [], []

    df_ = df[df.index > buy_raw[0]]
    date_buy.append(df_.index[0])

    for i in range(len(df_)):
        # 算出第一個停損日。日期不用轉datetime格式，純str也可比大小
        if df_.iloc[i].Close <= df_.iloc[:i+1]['High'].rolling(10).max()[-1] * (stp - 100) / -100:
            date_sell.append(df_.iloc[i].name)
            break

    for i in date_sell:
        try:
            df_ = df[df.index >= buy_raw[buy_raw > date_sell[-1] ][0]]
            date_buy.append(df_.index[0])
            for j in range(len(df_)):
                    if df_.iloc[j].Close <= df_.iloc[:j+1]['High'].rolling(10).max()[-1] * (stp - 100) / -100:
                        date_sell.append(df_.iloc[j].name)
                        break
        except Exception as e:
            continue

    if len(date_buy) > len(date_sell):
        print(f'{ticker}於{date_buy[-1]}進場後，還沒出場')
        date_buy = date_buy[:-1]

    # 損益LOG
    profit, res = [], []
    for i in range(len(date_buy)):
        entry = df[df.index == date_buy[i]]['Open'][0]
        exit = df[df.index == date_sell[i]]['Close'][0]
        holding = (pd.to_datetime(date_sell[i]) - pd.to_datetime(date_buy[i])).days
        net_pnl = round(((exit - entry)/entry - 0.00425) * 100, 2)
        profit.append(net_pnl)
        res.append([date_buy[i], entry, date_sell[i], exit, holding, net_pnl])
    global df_log
    df_log = pd.DataFrame(res, columns = ['開盤買','買價','收盤賣','賣價','持有天數','淨損益%'])
    df_log.index.name = ticker
    if log == True:
        st.write('-----')
        st.table(df_log) # print(df_log)

    # 股價買賣點線圖
    if plot == True:
        plt.figure(figsize = (10,5))
        plt.title(f'{ticker}')
        df['Close'].plot()
        for i in range(len(date_buy)):
            plt.plot([pd.to_datetime(date_buy)[i], pd.to_datetime(date_sell)[i]],
                    [df[df.index == date_buy[i]]['Open'][0], df[df.index == date_sell[i]]['Close'][0]],
                    marker = '^', color = 'r', lw = 1)
        st.pyplot()

    return np.mean(profit), len(profit), df['Close'][-1:].values[0]


def active():
    st.markdown("""
    # 動能選股回測
    有些股票一追高就拉回，有些則一過前高就噴出一去不回，那就回測看看哪些股票適合追高。
    #### 選股範圍
    [ARK方舟基金前30大持股](https://cathiesark.com/ark-funds-combined/complete-holdings)
    加 [S&P500成份股](https://www.slickcharts.com/sp500)
    加 [Yahoo Finance Screeners](https://finance.yahoo.com/screener)
    ```
    買進條件：以下4點符合3點以上時就隔天開盤買進
    ● 再漲不到3%就會創近22日新高
    ● 長紅實體K棒為近10天實體K棒平均的2.5倍
    ● 比過去5日均量多出30%
    ● 近5天出現過5日均線穿越10日均線的黃金交叉
    ```
    ```
    賣出條件：
    ● 從最近10日高點拉回8%就於收盤賣出
    ```
    """)
    req1, req2 = st.beta_columns(2)
    start = req1.date_input('Start', value = pd.to_datetime('2019-01-01'))
    end = req2.date_input('End')
    run = st.button('開始選股(需要8~10分鐘)')
    st.write('註：僅列出`平均每次獲利10%以上`、`交易記錄10筆以上`、`股價10塊以上`的結果')
    if run:
        good_enough = []
        for i in watchlist_us:
            try:
                res = crazy_dog_backtest(i, start = start, end = end, prior_high = 22, stp = 8, log = False, plot = False)
                if res[0] > 9 and res[1] > 9 and res[2] > 15:
                    good_enough.append(i)
                    crazy_dog_backtest(i, start = start, end = end, prior_high = 22, stp = 8, log = True, plot = True)
            except Exception as e:
                print(f'{i}不符合')
            continue