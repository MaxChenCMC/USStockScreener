import streamlit as st
import pandas as pd
from pandas.tseries.offsets import BDay
import requests, time
from io import StringIO
from bs4 import BeautifulSoup
from FinMind.data import DataLoader

def active():
    today = pd.date_range(end = pd.to_datetime('today'), periods = 1, freq = 'B').strftime('%Y-%m-%d')
    st.header(f'{today[0]}三大法人大小台動向')
    st.text('盤後15:00左右更新')
    df = pd.read_html('https://www.taifex.com.tw/cht/3/futContractsDate')[3][3:15]
    df = df[(df[0] == '序號') | (df[1] == '臺股期貨') | (df[1] == '小型臺指期貨')]
    df = df[[1,2,7,13]]
    df.columns = ['商品名稱','身份別','多空淨額(口數)', '未平倉餘額(口數)']
    df.set_index('商品名稱', inplace=True)
    df.index.name = ''
    st.table(df)

    st.header('歷史行情籌碼解讀')
    show = st.button('我瞧瞧(需要1分鐘)')
    if show:
        tb = []
        for i in range(9+0, -1, -1):
            date_index = (pd.datetime.today() - BDay(i)).strftime('%Y-%m-%d')
            date_tse = (pd.datetime.today() - BDay(i)).strftime('%Y%m%d')
            date_txf = (pd.datetime.today() - BDay(i)).strftime('%Y/%m/%d')
            r = requests.get('https://www.twse.com.tw/fund/BFI82U?response=csv&dayDate='+ date_tse +'&type=day')
            if r.text != '\r\n':
                df = pd.read_csv(StringIO(r.text), header=1).dropna(how='all', axis=1).dropna(how='any')
                institution = int(df.loc[3,'買賣差額'].replace(',','')) # 外資及陸資(不含自營)
                trust = int(df.loc[2,'買賣差額'].replace(',','')) # 投信
                time.sleep(3)
                # 現貨沒休市的話 期貨也不必偵錯了 直接爬
                myobj = {'queryDate': date_txf, "queryType": 1}
                response = requests.post("https://www.taifex.com.tw/cht/3/futContractsDate", data = myobj)
                soup = BeautifulSoup(response.text,features = "html.parser")
                table = soup.find( "table", class_ = "table_f")
                tx = table.find_all('tr')[5].find_all('td')
                txnet = int([i.text.strip() for i in tx][4].replace(',', ''))
                txoi = int([i.text.strip() for i in tx][10].replace(',', ''))
                mtx = table.find_all('tr')[14].find_all('td')
                mtxnet = int([i.text.strip() for i in mtx][4].replace(',', ''))
                mtxoi = int([i.text.strip() for i in mtx][10].replace(',', ''))
                res = [date_index, institution, trust, txnet, txoi, mtxnet, mtxoi]
                tb.append(res)
            else:
                print(f'{date_index}休市\n')

        oi = pd.DataFrame(data = tb, columns = ['date','inst_f buy', 'inst_t buy','inst_txf_net','inst_txf_oi','inst_mtx_net','inst_mtx_oi'])
        oi['date'] = pd.to_datetime(oi['date'])
        oi.set_index('date', inplace = True)

        # 前50大權值股，站上十日均的家數
        tse = pd.read_html('https://www.taifex.com.tw/cht/9/futuresQADetail')[0]['證券名稱'][:50].to_list()
        fm = DataLoader()
        start = (pd.to_datetime('today') - BDay(20)).strftime('%Y-%m-%d')
        end = (pd.to_datetime('today')).strftime('%Y-%m-%d')
        tw50 = pd.DataFrame({i: fm.taiwan_stock_daily(i, start, end)['close'] for i in tse})
        ma = tw50 > tw50.rolling(10).mean()
        gold_cross = ma.sum(axis=1)[-10:]

        # 合併期貨籌碼與黃金交叉家數
        gold_cross.index = oi.index
        comb = pd.concat([oi,gold_cross], axis = 1) # 自動命名欄位為數字0
        comb.index = comb.index.strftime('%Y-%m-%d')

        # 轉化成主觀訊號
        df = pd.DataFrame()
        df['外資買賣超'] = comb['inst_f buy'] > comb['inst_f buy'].rolling(5).mean() # 中位 ☛ 多停85；空整體都有利
        df['投信買賣超'] = comb['inst_t buy'] > comb['inst_t buy'].rolling(5).mean() #唯一選擇 平均
        df['外資大台多空淨額'] = comb['inst_txf_net'] > 0
        df['外資大台未平倉'] = comb['inst_txf_oi'] > comb['inst_txf_oi'].rolling(5).median()
        df['外資小台多空淨額'] = comb['inst_mtx_net'] > 0
        df['外資小台未平倉'] = (comb['inst_mtx_oi'] > comb['inst_mtx_oi'].rolling(5).median()) & (comb['inst_mtx_oi'] > 0)
        df['前50大站上10ma家數'] = comb[0] > comb[0].rolling(5).mean()

        # df['隔天加權漲跌點數'] = yf.Ticker('^TWII').history(period = '10d')['Close'].diff().shift(-1)
        comb.columns = ['外資現股買賣超','投信現股買賣超','外資大台多空淨額','外資大台未平倉','外資小台多空淨額','外資小台未平倉','前50大權值股站上十日線總檔數']
        st.table(comb.tail())

        st.markdown("""
        法人現股買賣超若比過去5日的平均值還多，表示法人偏多；反之則偏空。

        外資大小台當日多空淨額若為正，即表示偏多，而未平倉口數若較過去5日的中位數高，即表示行情偏多；反之則偏空。

        上市前50大權值股中，若站上十日線的檔數比過去5日平均還多，則行情偏多。

        `歷史行情7個欄位中，若都沒出現訊號則行情偏空，而訊號 4~7 則行情偏多`
        """)
        signal = pd.DataFrame(df.sum(axis = 1)[-5:].to_list(), columns = ['訊號'], index = df.index[-5:]).T
        st.table(signal)
