import streamlit as st
import pandas as pd
import numpy as np
from FinMind.data import DataLoader
import matplotlib.pyplot as plt
plt.style.use('bmh')
st.set_option('deprecation.showPyplotGlobalUse', False) # pyplot那邊很囉嗦

def crazy_dog_backtest(df, prior_high = 22, stp = 8):
    cond1 = (df['close'] * 1.03 > df['max'].rolling(prior_high).max())
    cond2 = ((df['close'] - df['open']) > abs(df['open'] - df['close']).rolling(10).mean()*2.5)
    cond3 = (df['Trading_Volume'] > df['Trading_Volume'].rolling(5).mean() * 1.5)
    duo_ma = df['close'].rolling(5).mean() >= df['close'].rolling(10).mean()
    cond4 = ((duo_ma == True) & ((duo_ma != duo_ma.shift()).rolling(5).sum() == 1))
    buy = pd.concat([cond1, cond2, cond3, cond4], axis = 1)
    buy.index = df.index
    buy_raw = buy[buy.sum(axis = 1) >= 3].index

    global date_buy, date_sell
    date_buy, date_sell = [], []

    df_ = df[df.index > buy_raw[0]]
    date_buy.append(df_.index[0])
    for i in range(len(df_)):
        # 算出第一個停損日。日期不用轉datetime格式，純str也可比大小。大於就會從隔天算起
        if df_.iloc[i].close <= df_.iloc[:i+1]['max'].rolling(10).max()[-1] * (stp - 100) / -100:
            date_sell.append(df_.iloc[i].name)
            break

    for i in date_sell:
        try:
            df_ = df[df.index > buy_raw[buy_raw > date_sell[-1]][0]]
            date_buy.append(df_.index[0])
            for j in range(len(df_)):
                    if df_.iloc[j].close <= df_.iloc[:j+1]['max'].rolling(10).max()[-1] * (stp - 100) / -100:
                        date_sell.append(df_.iloc[j].name)
                        break
        except Exception as e:
            continue

    # 損益LOG
    profit,res = [], []
    for i in range(len(date_buy)):
        entry = df[df.index == date_buy[i]].open[0]
        exit = df[df.index == date_sell[i]].close[0]
        holding = (pd.to_datetime(date_sell[i]) - pd.to_datetime(date_buy[i])).days
        net_pnl = round(((exit - entry)/entry - 0.00425) * 100, 2)
        profit.append(net_pnl)
        res.append([date_buy[i], entry, date_sell[i], exit, holding, net_pnl])
    st.table(pd.DataFrame(res, columns = ['開盤買','買價','收盤賣','賣價','持有天數','淨損益%']))
    st.write(f'平均損益{np.mean(profit)}')

    # 損益折線圖
    df.index = pd.to_datetime(df.index)
    df['close'].plot(figsize = (15,8))
    for i in range(len(date_buy)):
        plt.plot([pd.to_datetime(date_buy)[i], pd.to_datetime(date_sell)[i]],
                [df[df.index == date_buy[i]].open[0], df[df.index == date_sell[i]].close[0]],
                marker = '^', color = 'r', lw = 1)
    st.pyplot()


def active():
    # GUI自訂變數
    st.markdown("""
    # 瘋狗選股法 回測
    ```
    以下4點符合3點以上時就隔天買進
    ● 再漲不到3%就會創近n日新高(天數自訂)
    ● 長紅實體K棒為近10天實體K棒平均的2.5倍
    ● 比過去5日均量多出50%
    ● 近5天出現過5日均線穿越10日均線的黃金交叉
    ```
    ```
    ● 自買入後的近10日高點拉回x%就停損或停利(%自訂)
    ```
    """)
    a, b, c = st.beta_columns(3)
    sid = a.text_input('輸入股號', value = '2603')
    start = b.date_input('Start', value = pd.to_datetime('2019-01-01'))
    end = c.date_input('End')
    d, e = st.beta_columns(2)
    v1 = d.slider('即將創幾日新高？', int(22), int(100), value = 22)
    v2 = e.slider('從高點拉回幾趴停損？', 5, 20, value = 8)

    criteria = st.button(label = '看結果')
    if criteria:
        fm = DataLoader()
        df = fm.taiwan_stock_daily(sid, start_date = start, end_date = end )[['date','open','max','min','close','Trading_Volume']]
        df = df.set_index('date')
        crazy_dog_backtest(df, v1, v2)