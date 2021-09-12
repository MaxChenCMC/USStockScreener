import streamlit as st
import landing_page, tw_stock, tw_stock_bt, after_market, # us_stock, us_stock_bt
import pandas as pd
import numpy as np
from FinMind.data import DataLoader
import mplfinance as mpf
import requests, time, lxml  # lxml在本地端不用，但佈屬streamlit雲端就要
import matplotlib.pyplot as plt
from io import StringIO
from bs4 import BeautifulSoup

st.set_page_config(
    page_icon="💯", page_title="Max選股", layout="centered", initial_sidebar_state="auto"
)

st.markdown(
    """<style>
.main{
    background-color: #EFE3D8;
    color: #black;
    font = bold 14px Arial, Helvetica, sans-serif;
}
</style>""",
    unsafe_allow_html=True,
)

choice = st.sidebar.selectbox(
    "Menu",
    options=[
        "Home",
        "TW Stock",
        "TW Stock Backtest",
        "After Market Disclosure",
#         "US Stock",
#         "US Stock Backtest",
    ],
    index=0,
)
st.sidebar.write("右上角 ≡ ☛ settings ☛ Theme選'Light'體驗較佳")

if choice == "Home":
    landing_page.active()

elif choice == "TW Stock":
    tw_stock.active()

elif choice == "TW Stock Backtest":
    tw_stock_bt.active()

elif choice == "After Market Disclosure":
    after_market.active()
    
# elif choice == "US Stock":
#     us_stock.active()

# elif choice == "US Stock Backtest":
#     us_stock_bt.active()
