import streamlit as st
import pandas as pd
from FinMind.data import DataLoader
import mplfinance as mpf
import matplotlib.pyplot as plt

# import lxml

st.set_option("deprecation.showPyplotGlobalUse", False)  # pyplot那邊很囉嗦


def kbar_plot(i=None, start=None, end=None, plot=False):
    fm = DataLoader()
    df = fm.taiwan_stock_daily(i, start_date=start, end_date=end)[
        ["date", "open", "max", "min", "close", "Trading_Volume"]
    ]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df = df.set_index("date")
    df.index = pd.to_datetime(df.index)
    if plot == True:
        clr = mpf.make_marketcolors(up="r", down="g", edge="k", wick="k")
        sty = mpf.make_mpf_style(base_mpf_style="default", marketcolors=clr)
        kwargs = dict(type="candle", volume=True, style=sty)
        plt.figure(figsize=(15, 5))
        mpf.plot(df, **kwargs, title=i)
        st.pyplot()
    else:
        return df


# 過去一季66個交易日的日期list
quarter = pd.date_range(end=pd.to_datetime("today"), periods=66, freq="B").strftime(
    "%Y-%m-%d"
)


def active():
    st.markdown(
        """
    <h1 style= 'text-align: center;'> Max TW stocks </h1>
    <h1 style= 'text-align: center; color: grey;'>近期市場關注標的</h1>
    <h3>依成交值排序</h3>

    資料來源：[HiStock 嗨投資](https://histock.tw/stock/rank.aspx?p=all)
    """,
        unsafe_allow_html=True,
    )

    df = pd.read_html("https://histock.tw/stock/rank.aspx?p=all")[0]
    df.drop(["漲跌▼", "周漲跌▼", "開盤▼", "最高▼", "最低▼", "昨收▼"], axis=1, inplace=True)
    df = df[df["代號▼"].apply(lambda x: len(x) == 4)]
    df = df.replace("--", "+0.0%")
    df["漲跌幅▼"] = df["漲跌幅▼"].apply(lambda x: float(x[:-1]))
    df["振幅▼"] = df["振幅▼"].apply(lambda x: float(x[:-1]))
    df.columns = ["代號", "名稱", "價格", "漲跌幅", "振幅", "成交量", "成交值(億)"]
    df.set_index("代號", inplace=True)
    df_ = df[
        (df["價格"] < 150)
        & (df["漲跌幅"] > 0)
        & (df["振幅"] > 5)
        & (df["成交量"] > 2000)
        & (df["成交值(億)"] > 15)
    ]

    st.table(df_.sort_values("成交值(億)", ascending=False))

    st.header("我想自訂標準")
    a, b, c = st.columns(3)
    v1 = a.slider("價格幾塊以下？", int(df["價格"].min()), int(df["價格"].max()), value=150)
    v2 = b.slider("漲跌幅超過幾%？", int(df["漲跌幅"].min()), int(df["漲跌幅"].max()), value=0)
    v3 = c.slider("振幅超過幾%？", int(df["振幅"].min()), int(df["振幅"].max()), value=5)
    d, e = st.columns(2)
    v4 = d.slider("成交量超過幾張？", int(df["成交量"].min()), int(df["成交量"].max()), value=2000)
    v5 = e.slider(
        "成交值超過幾億？", int(df["成交值(億)"].min()), int(df["成交值(億)"].max()), value=15
    )
    criteria = st.button(label="看結果")
    if criteria:
        table = df[
            (df["價格"] < v1)
            & (df["漲跌幅"] > v2)
            & (df["振幅"] > v3)
            & (df["成交量"] > v4)
            & (df["成交值(億)"] > v5)
        ]
        st.dataframe(table)

    st.markdown(
        "------------------------------------------------------------------------------------"
    )
    st.markdown(
        """
    # 動能選股法
    #### 資料來源：[富邦證券](https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_0_10.djhtm)
    #### 14:30左右會更新當天排行，從上市跟上櫃當天漲幅前50名(共100檔)裡挑選
    ####
    """
    )

    criteria = st.multiselect(
        "最多4個", ["即將創近月新高", "長紅K棒", "爆量", "最近剛黃金交叉"], default=["長紅K棒", "爆量"]
    )
    run = st.button("開始選股(需要20秒)")
    if run:
        rank_tse = pd.read_html(
            "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_0_1.djhtm"
        )[2][1][2:]
        rank_otc = pd.read_html(
            "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_1_1.djhtm"
        )[2][1][2:]
        top100 = []
        for i in rank_tse:
            top100.append(i[:4])
        for i in rank_otc:
            top100.append(i[:4])

        list_to_trade = []
        for i in top100:
            df = kbar_plot(i=i, start=quarter[-22], end=quarter[-1], plot=False)
            cond1 = (df["close"] * 1.03 > df["high"].rolling(22).max())[-1]
            cond2 = (
                (df["close"] - df["open"])
                > abs(df["open"] - df["close"]).rolling(10).mean() * 2.5
            )[-1]
            cond3 = (df["volume"] > df["volume"].rolling(5).mean() * 1.5)[-1]
            duo_ma = df["close"].rolling(5).mean() >= df["close"].rolling(10).mean()
            cond4 = (
                (duo_ma == True) & ((duo_ma != duo_ma.shift()).rolling(5).sum() == 1)
            )[-1]
            criteria_ = []
            if "即將創近月新高" in criteria:
                criteria_.append(cond1)
            if "長紅K棒" in criteria:
                criteria_.append(cond2)
            if "爆量" in criteria:
                criteria_.append(cond3)
            if "最近剛黃金交叉" in criteria:
                criteria_.append(cond4)
            if sum(criteria_) == len(criteria):
                list_to_trade.append(i)
        if list_to_trade != []:
            st.text_area(label="選股結果請先複製下來，不然網頁更新時會被洗掉", value=list_to_trade)
            for i in list_to_trade:
                kbar_plot(i=i, start=quarter[-66], end=quarter[-1], plot=True)
        else:
            st.warning("條件別設太嚴不然選不出東西")

    st.markdown(
        "------------------------------------------------------------------------------------"
    )
    st.header("我有自己想看的")
    req1, req2, req3 = st.columns([1, 1, 2])
    start = req1.date_input("Start", value=pd.to_datetime("2021-07-01"))
    end = req2.date_input("End")
    i = req3.text_input("輸入股號", value="6104")
    run = st.button("開始")
    if run:
        kbar_plot(i=i, start=start, end=end, plot=True)


active()
