import streamlit as st
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
import requests, lxml
st.set_option('deprecation.showPyplotGlobalUse', False) # pyplot那邊很囉嗦

def kbar_plot(ticker, horizon = 'fix', mkt = 'us'):
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

def rebase(sids):
    df = pd.DataFrame({ i: yf.Ticker(i).history(start = start, end = end)['Close'] for i in sids })
    return ((1 + df.pct_change()).cumprod() - 1).fillna(0.0)

def watchlist_us():
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

    ark = pd.read_html('https://cathiesark.com/ark-funds-combined/complete-holdings')[0]['Ticker'][1:31].to_list()
    my_watchlist = ['ZM','AVID','BGFV','TIGR','APPS','ENPH','CDLX','NTP','SBOW','NIO','ZS','PLUG']
    watchlist_us = list(set(sid1 + sid2 + sid3 + sid4 + sid5 + sid6 + sid7 + sid8 + ark + my_watchlist))
    return watchlist_us

def active():
    st.image('./cover_us.jpg', use_column_width = True)
    st.markdown(f"<h1 style= 'text-align: center;'> Max US stocks </h1>", unsafe_allow_html = True)

    st.markdown("""
    # 動能選股
    #### 選股範圍
    [ARK方舟基金前30大持股](https://cathiesark.com/ark-funds-combined/complete-holdings)
    加 [S&P500成份股](https://www.slickcharts.com/sp500)
    加 [Yahoo Finance Screeners](https://finance.yahoo.com/screener)
    ####
    """)
    criteria = st.multiselect('最多4個',['即將創近月新高','長紅K棒','爆量','最近剛黃金交叉'],
    default = ['即將創近月新高','長紅K棒','爆量'])
    run = st.button('開始選股(需要8~10分鐘)')
    if run:
        list_to_trade = []
        for i in watchlist_us():
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
                kbar_plot(i, horizon = 'fix', mkt = 'us')
        else:
            st.warning('條件別設太嚴不然選不出東西')

    st.markdown('------------------------------------------------------------------------------------')
    st.header('我有自己想看的')
    req1, req2, req3 = st.beta_columns(3)
    global start, end
    start = req1.date_input('Start', value = pd.to_datetime('2021-04-01'),key = '1')
    end = req2.date_input('End', key = '2')
    ticker = req3.text_input('股號', value='GME')
    kbar_plot(ticker, horizon = 'free', mkt = 'us')


    st.markdown('------------------------------------------------------------------------------------')
    st.header('同期強弱勢比較')
    col1, col2 = st.beta_columns(2)
    start = col1.date_input('Start', value = pd.to_datetime('2021-01-01'), key='3')
    end = col2.date_input('End', key='4')

    sids = st.radio('',('國際指數','SPDR 11 SECTORS','ARKK Top15')) #'Freddy的MFA', '我瞎湊的MFA'
    if sids == '國際指數':
        df = rebase(['^DJI','^IXIC','^GSPC','^SOX','^GDAXI','EWT','^TWII','^TWOII'])
        df.columns = ['道瓊','那斯達克','標普500','費城半導體','德國DAX','MSCI台灣','加權','櫃買']
    elif sids == 'SPDR 11 SECTORS':
        df = rebase(['XLB','XLC','XLE','XLF','XLI','XLK','XLP','XLRE','XLU','XLV','XLY'])
        df.columns = ['Materials','Communication Services','Energy','Financials','Industrials','Technology',
        'Consumer Staples','Real Estate','Utilities','Health Care','Consumer Discretionary']
    elif sids == 'ARKK Top15':
        ark = pd.read_html('https://cathiesark.com/ark-funds-combined/complete-holdings')[0]['Ticker'][1:16].to_list()
        df = rebase(ark)
    st.line_chart(df) # APP原生圖的legend照字母排序 .sort_values(by = df.index[-1], ascending= False, axis= 1)


    st.markdown('------------------------------------------------------------------------------------')
    st.header('前16大權值股，挑幾檔順眼的來比一比')
    col1, col2 = st.beta_columns(2)
    start = col1.date_input('Start', value = pd.to_datetime('2021-01-01'), key='5')
    end = col2.date_input('End', key='6')

    blue_chips = ['AAPL','MSFT','AMZN','GOOG','FB','TSLA','TSM','BABA','V','JPM','JNJ','WMT','MA','NVDA','UNH','BA']
    weighted = st.multiselect('', blue_chips, default = ['GOOG','FB','AAPL','TSLA'])
    show = st.button('先挑這些', key = '7')
    if show:
        st.line_chart(rebase(weighted))
