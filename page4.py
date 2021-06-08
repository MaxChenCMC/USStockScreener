import streamlit as st
import streamlit.components.v1 as components
import requests, time, lxml
import numpy as np
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
import yfinance as yf

def active():
    # google搜圖右鍵 copy img addr.
    components.iframe('https://www.thebalance.com/thmb/UZS2curMfBJpwbb8LrvpxttXhA0=/2103x1428/filters:fill(auto,1)/Stock-Market-Charts-Are-Useless-56a093595f9b58eba4b1ae5b.jpg')
    tb = []
    for i in range(9+0, -1, -1):
        date_index = (pd.datetime.today() - pd.tseries.offsets.BDay(i)).strftime('%Y-%m-%d')
        date_tse = (pd.datetime.today() - pd.tseries.offsets.BDay(i)).strftime('%Y%m%d')
        date_txf = (pd.datetime.today() - pd.tseries.offsets.BDay(i)).strftime('%Y/%m/%d')
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
            txnet = int([i.text.strip() for i in tx][5].replace(',', ''))
            txoi = int([i.text.strip() for i in tx][11].replace(',', ''))
            mtx = table.find_all('tr')[14].find_all('td')
            mtxnet = int([i.text.strip() for i in mtx][5].replace(',', ''))
            mtxoi = int([i.text.strip() for i in mtx][11].replace(',', ''))
            res = [date_index, institution, trust, txnet, txoi, mtxnet, mtxoi]
            tb.append(res)
        else:
            print(f'{date_index}休市\n')

    oi = pd.DataFrame(columns = ['date','inst_f buy', 'inst_t buy','inst_txf_net','inst_txf_oi','inst_mtx_net','inst_mtx_oi'], data = tb)
    oi['date'] = pd.to_datetime(oi['date'])
    oi.set_index('date', inplace = True)

    df = oi.copy()
    df['外資買賣超'] = np.where( df['inst_f buy'] > df['inst_f buy'].rolling(5).mean(), 1, 0) # 中位☛多停85；空整體都有利
    df['投信買賣超'] = np.where( df['inst_t buy'] > df['inst_t buy'].rolling(5).mean() , 1, 0) #唯一選擇 平均
    df['外資大台多空淨額'] = np.where( df['inst_txf_net'] > 0, 1, 0)
    df['外資大台未平倉'] = np.where( df['inst_txf_oi'] > df['inst_txf_oi'].rolling(5).median(), 1, 0)
    df['外資小台多空淨額'] = np.where( df['inst_mtx_net'] > 0, 1, 0)
    df['外資小台未平倉'] = np.where( (df['inst_mtx_oi'] > df['inst_mtx_oi'].rolling(5).median()) & (df['inst_mtx_oi'] > 0), 1, 0)
    df['隔天加權漲跌點數'] = yf.Ticker('^TWII').history(period = '10d')['Close'].diff().shift(-1)
    df.index = df.index.strftime('%Y-%m-%d')
    st.title('法人籌碼轉換成多空訊號')
    st.table(df[['外資買賣超', '投信買賣超', '外資大台多空淨額', '外資大台未平倉', '外資小台多空淨額', '外資小台未平倉','隔天加權漲跌點數']])
