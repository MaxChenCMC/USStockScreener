import streamlit as st
import pandas as pd
import numpy as np
from FinMind.data import DataLoader
import matplotlib.pyplot as plt

plt.style.use("bmh")


st.set_option("deprecation.showPyplotGlobalUse", False)  # pyplot那邊很囉嗦


def crazy_dog_backtest(
    sid, start=None, end=None, prior_high=22, stp=8, log=False, plot=False
):
    fm = DataLoader()
    df = fm.taiwan_stock_daily(sid, start_date=start, end_date=end)[
        ["date", "open", "max", "min", "close", "Trading_Volume"]
    ]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df = df.set_index("date")

    cond1 = df["close"] * 1.03 > df["high"].rolling(prior_high).max()
    cond2 = (df["close"] - df["open"]) > abs(df["open"] - df["close"]).rolling(
        10
    ).mean() * 2.5
    cond3 = df["volume"] > df["volume"].rolling(5).mean() * 1.5
    duo_ma = df["close"].rolling(5).mean() >= df["close"].rolling(10).mean()
    cond4 = (duo_ma == True) & ((duo_ma != duo_ma.shift()).rolling(5).sum() == 1)
    buy = pd.concat([cond1, cond2, cond3, cond4], axis=1)
    buy.index = df.index
    buy_raw = buy[buy.sum(axis=1) >= 3].index

    global date_buy, date_sell
    date_buy, date_sell = [], []

    df_ = df[df.index > buy_raw[0]]
    date_buy.append(df_.index[0])

    for i in range(len(df_)):
        # 算出第一個停損日。日期不用轉datetime格式，純str也可比大小。大於就會從隔天算起
        if (
            df_.iloc[i]["close"]
            <= df_.iloc[: i + 1]["high"].rolling(10).max()[-1] * (stp - 100) / -100
        ):
            date_sell.append(df_.iloc[i].name)
            break

    for i in date_sell:
        try:
            df_ = df[df.index > buy_raw[buy_raw > date_sell[-1]][0]]
            date_buy.append(df_.index[0])
            for j in range(len(df_)):
                if (
                    df_.iloc[j]["close"]
                    <= df_.iloc[: j + 1]["high"].rolling(10).max()[-1]
                    * (stp - 100)
                    / -100
                ):
                    date_sell.append(df_.iloc[j].name)
                    break
        except Exception as e:
            continue

    if len(date_buy) > len(date_sell):
        print(f"{sid}於{date_buy[-1]}進場後，還沒出場")
        date_buy = date_buy[:-1]

    # 損益LOG
    profit, res = [], []
    for i in range(len(date_buy)):
        entry = df[df.index == date_buy[i]]["open"][0]
        exit = df[df.index == date_sell[i]]["close"][0]
        holding = (pd.to_datetime(date_sell[i]) - pd.to_datetime(date_buy[i])).days
        net_pnl = round(((exit - entry) / entry - 0.00425) * 100, 2)
        profit.append(net_pnl)
        res.append([date_buy[i], entry, date_sell[i], exit, holding, net_pnl])

    global df_log
    df_log = pd.DataFrame(res, columns=["開盤買", "買價", "收盤賣", "賣價", "持有天數", "淨損益%"])
    df_log.index.name = sid
    if log == True:
        st.table(df_log)
        st.write(np.mean(profit))

    # 損益折線圖
    if plot == True:
        df.index = pd.to_datetime(df.index)
        plt.figure(figsize=(10, 5))
        plt.title(f"{sid}")
        df["close"].plot()
        for i in range(len(date_buy)):
            plt.plot(
                [pd.to_datetime(date_buy)[i], pd.to_datetime(date_sell)[i]],
                [
                    df[df.index == date_buy[i]]["open"][0],
                    df[df.index == date_sell[i]]["close"][0],
                ],
                marker="^",
                color="r",
                lw=1,
            )
        st.pyplot()

    return np.mean(profit), len(profit), df["close"][-1:].values[0]


def active():
    st.markdown(
        """
    ## 瘋狗選股法回測單一個股
    ```
    買進條件：以下4點符合3點以上時就隔天買進
    ● 再漲不到3%就會創近n日新高(天數自訂)
    ● 長紅實體K棒為近10天實體K棒平均的2.5倍
    ● 比過去5日均量多出50%
    ● 近5天出現過5日均線穿越10日均線的黃金交叉
    ```
    ```
    賣出條件：
    ● 自買入後的近10日高點拉回x%就停損或停利(%自訂)
    ```
    """
    )
    a, b, c = st.columns(3)
    sid = a.text_input("輸入股號", value="2603")
    start = b.date_input("Start", value=pd.to_datetime("2019-01-01"))
    end = c.date_input("End")
    d, e = st.columns(2)
    v1 = d.slider("即將創幾日新高？", int(22), int(100), value=22)
    v2 = e.slider("從高點拉回幾趴停損？", 5, 20, value=8)
    criteria = st.button(label="看結果")
    if criteria:
        crazy_dog_backtest(
            sid, start=start, end=end, prior_high=v1, stp=v2, log=True, plot=True
        )

    st.write(
        "------------------------------------------------------------------------------------------"
    )
    st.markdown(
        """
    ## 瘋狗選股法回測成交值前350大的股票
    僅列出`平均每次獲利10%以上`、`交易記錄10筆以上`、`股價10~500塊`的結果

    右上角「RUNNING...」動畫跑完才算結束
    """
    )
    f, g = st.columns(2)
    start_ = f.date_input("Start", value=pd.to_datetime("2019-01-01"), key="1")
    end_ = g.date_input("End", key="2")
    criteria_ = st.button(label="看結果(需要5分鐘)", key="3")
    if criteria_:
        df = pd.read_html("https://histock.tw/stock/rank.aspx?p=all")[0]
        sids = df.sort_values("成交值(億)▼", ascending=False)["代號▼"].to_list()
        sids = [i for i in sids if len(i) == 4][:350]
        good_enough = []
        for i in sids:
            try:
                res = crazy_dog_backtest(
                    i,
                    start=start_,
                    end=end_,
                    prior_high=22,
                    stp=8,
                    log=False,
                    plot=False,
                )
                if res[0] > 10 and res[1] > 10 and res[2] > 10 and res[2] < 500:
                    good_enough.append(i)
                    crazy_dog_backtest(
                        i,
                        start=start_,
                        end=end_,
                        prior_high=22,
                        stp=8,
                        log=True,
                        plot=True,
                    )
            except Exception as e:
                continue
        if good_enough == []:
            st.warning("選不出股票")


active()
