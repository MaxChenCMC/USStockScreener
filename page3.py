import streamlit as st
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
import lxml
st.set_option('deprecation.showPyplotGlobalUse', False) # pyplot那邊很囉嗦

# start, end = '2021-01-01', pd.to_datetime('today') # 不先指定變數的話 函式奇怪會生不出來
def kbar(ticker, horizon = 'fix', mkt = 'us'):
    if horizon == 'fix':
        kwargs = dict(period = '3mo')
    elif horizon == 'free':
        kwargs = dict(start = start, end = end)
    df = yf.Ticker(ticker).history(**kwargs).iloc[:,:5]
    df.columns = df.columns.str.lower()
    if mkt == 'us':
        clr = mpf.make_marketcolors(up = 'g', down = 'r', edge = 'k', wick = 'k')
    elif mkt == 'tw':
        clr = mpf.make_marketcolors(up = 'r', down = 'g', edge = 'k', wick = 'k')
    sty = mpf.make_mpf_style( base_mpf_style = 'default', marketcolors = clr)
    kwargs = dict(type = 'candle', volume = True, style = sty)
    plt.figure(figsize = (15,5))
    mpf.plot(df, **kwargs, title = ticker)
    return st.pyplot()

def active():
    st.image('./cover_tw.jpg', use_column_width = True)
    st.markdown(f"<h1 style= 'text-align: center;'> Max TW stocks </h1>", unsafe_allow_html = True)
    st.markdown("""
    # 近期市場關注標的
    #### 資料來源：[HiStock 嗨投資](https://histock.tw/stock/rank.aspx?p=all)
    #### 篩選條件： `價格 ＜ 100`／`振幅 ＞ 5％`／`成交量 ＞ 2000張`／`成交值 ＞ 15億`
    ####
    """)
    show = st.button('我瞧瞧！')
    if show:
        vola = pd.read_html('https://histock.tw/stock/rank.aspx?p=all')[0]
        cond1 = vola['代號▼'].apply(lambda x: len(x) == 4)
        cond2 = vola['振幅▼'].apply(lambda x: float(x[:-1]) > 5.0)
        vola_rank = vola[(vola['成交值(億)▼'] > 15) & (vola['成交量▼'] > 2000) & (vola['價格▼'] < 100) & cond1 & cond2]
        vola_rank[['漲跌▼','漲跌幅▼']] = vola_rank[['漲跌▼','漲跌幅▼']].replace('--','0.00%')
        vola_rank['漲跌幅%'] = vola_rank['漲跌幅▼'].apply(lambda x: float(x[:-1]))
        vola_rank.drop(['周漲跌▼','開盤▼','最高▼','最低▼','昨收▼','漲跌幅▼'],axis = 1, inplace = True)
        vola_rank.set_index('代號▼', inplace = True)
        st.table(vola_rank.sort_values('漲跌幅%', ascending = False))

    st.markdown('------------------------------------------------------------------------------------')
    st.markdown("""
    # 動能選股法
    #### 資料來源：[富邦證券](https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_0_10.djhtm)
    #### 14:30左右會更新當天排行，從上市跟上櫃當天漲幅前50名(共100檔)裡挑選
    ####
    """)
    criteria = st.multiselect('最多4個',['即將創近月新高','長紅K棒','爆量','最近剛黃金交叉'],
    default = ['即將創近月新高','長紅K棒','爆量']) #,'最近剛黃金交叉'
    run = st.button('開始選股(需要20秒)')
    if run:
        rank_tse = pd.read_html('https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_0_10.djhtm')[2][1][2:]
        rank_otc = pd.read_html('https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_1_10.djhtm')[2][1][2:]
        top100 = []
        for i in rank_tse:
            sid = i[:4] + '.TW'
            top100.append(sid)
        for i in rank_otc:
            sid = i[:4] + '.TWO'
            top100.append(sid)

        list_to_trade = []
        for i in top100:
            df = yf.Ticker(i).history(period = '1mo').iloc[:,:5]
            cond1 = (df['Close'] * 1.03 > df['High'].rolling(22).max())[-1]
            cond2 = ((df['Close'] - df['Open']) > abs(df['Open'] - df['Close']).rolling(10).mean()*2.5)[-1]
            cond3 = (df['Volume'] > df['Volume'].rolling(5).mean() * 1.3)[-1]
            duo_ma = df['Close'].rolling(5).mean() >= df['Close'].rolling(10).mean()
            cond4 = ((duo_ma == True) & ((duo_ma != duo_ma.shift()).rolling(5).sum() == 1))[-1]
            criteria_ = []
            if '即將創近月新高' in criteria:
                criteria_.append(cond1)
            if '長紅K棒' in criteria:
                criteria_.append(cond2)
            if '爆量' in criteria:
                criteria_.append(cond3)
            if '最近剛黃金交叉' in criteria:
                criteria_.append(cond4)
            if sum(criteria_) == len(criteria) :
                list_to_trade.append(i)
        if list_to_trade != []:
            st.text_area(label = '選股結果請先複製下來，不然網頁更新時會被洗掉', value = list_to_trade)
            for i in list_to_trade:
                kbar(i, horizon = 'fix', mkt = 'tw')
        else:
            st.warning('條件別設太嚴不然選不出東西')


    st.markdown('------------------------------------------------------------------------------------')
    st.header('我有自己想看的')
    req1, req2, req3 = st.beta_columns([1,1,2])
    global start, end
    start = req1.date_input('Start', value = pd.to_datetime('2021-04-01'))
    end = req2.date_input('End')
    sid = req3.text_input('輸入股號(上市☛.TW、上櫃☛.TWO、頭尾不用加引號)', value = '2603.TW')
    st.text('(後台使用的套件無法提供最即時的台股資訊，若K棒看起來不強，請用別的平臺查詢)')
    kbar(sid, horizon = 'free', mkt = 'tw')