import streamlit as st; st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd
import ffn
import matplotlib.pyplot as plt; plt.style.use('bmh')
from datetime import datetime, timedelta

import yfinance as yf
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup


def DefaultContent() -> None:
    st.image("./img/cover_us.jpg", use_column_width=True)
    st.markdown(f"<h1 style= 'text-align: center;'>US stocks</h1>", unsafe_allow_html=True)
    st.subheader("Cross Market/Groups Comparison 不同市場類股漲跌幅比較")
    col1, col2, col3 = st.columns(3)
    Section1_Status = col1.selectbox('Select a group:', [None, "US & TW index", "SPDR ETF 11 SECTORS", "Market Cap Top25", "ARKK Components Top15"], index = 0)
    StartDate = col2.date_input("Start", value = (datetime.today() - timedelta(days = 3*30)), key = "1")
    EndDate = col3.date_input("End", value = datetime.today(), key = "2")

  
    if Section1_Status != None:
        if Section1_Status == "US & TW index":
            df = ffn.get('^DJI,^IXIC,^GSPC,SOXX,^TWII,^TWOII',start = StartDate, end = EndDate)
            df.columns = [
                "DowJones",
                "Nasdaq",
                "S&P 500",
                "PHLX Semiconductor",
                "TSE",
                "OTC",
            ]
            df.rebase().plot()
            
        elif Section1_Status == "SPDR ETF 11 SECTORS":
            df1 = ffn.get('XLB,XLC,XLE,XLF,XLI,XLK,XLP,XLRE,XLU,XLV,XLY',start = StartDate, end = EndDate)
            df1.columns = [
                "Materials",
                "Communication Services",
                "Energy",
                "Financials",
                "Industrials",
                "Technology",
                "Consumer Staples",
                "Real Estate",
                "Utilities",
                "Health Care",
                "Consumer Discretionary",
            ]
            df1.rebase().sort_values(by = df1.index[-1], axis = 1, ascending = False).plot(); plt.legend( bbox_to_anchor=(1,0.9))
                    
        elif Section1_Status == "Market Cap Top25":
            MarketCapsTop25 = 'MSFT,AAPL,NVDA,AMZN,GOOGL,META,LLY,TSM,AVGO,JPM,NVO,V,TSLA,WMT,XOM,MA,UNH,ASML,PG,JNJ,HD,ORCL,TM,MRK,COST'
            df_MarketCapsTop25 = ffn.get(MarketCapsTop25,start = StartDate, end = EndDate).rebase()
            df_MarketCapsTop25.sort_values(by = df_MarketCapsTop25.index[-1], axis = 1, ascending = False).plot(); plt.legend( bbox_to_anchor=(1,1.3))
                            
        elif Section1_Status == "ARKK Components Top15":
            Ark_Top15: list[str] = pd.read_html('https://cathiesark.com/ark-funds-combined/complete-holdings')[0]['Ticker'][1:16].to_list()
            df_Ark = ffn.get(",".join(Ark_Top15),start = StartDate, end = EndDate).rebase()
            df_Ark.sort_values(by = df_Ark.index[-1], axis = 1, ascending = False).plot(); plt.legend( bbox_to_anchor=(1,1))

        st.pyplot()
    
    
    st.markdown("------------------------------------------------------------------------------------")
    
    
    st.subheader("自選股漲跌幅比較")
    MostActives: list[str] = pd.read_html('https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100')[0].Symbol.to_list()
    [MostActives.append(i) for i in ["MSFT","AAPL","NVDA","AMZN","GOOGL","META"]]
    weighted = st.multiselect("multi select", MostActives, default = ["MSFT","AAPL","NVDA","AMZN","GOOGL","META"])
    col4, col5 = st.columns(2)
    _StartDate = col4.date_input("Start", value = (datetime.today() - timedelta(days = 3*30)))
    _EndDate = col5.date_input("End", value = datetime.today())
    Section2_Status = st.button("Check Comparison")
     
    if Section2_Status:
        df_Discretionary = ffn.get(",".join(weighted), start = _StartDate, end = _EndDate).rebase()
        df_Discretionary.sort_values(by = df_Discretionary.index[-1], axis = 1, ascending = False).plot(); plt.legend( bbox_to_anchor=(1,1))
        st.pyplot()