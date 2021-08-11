import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from FinMind.data import DataLoader
import mplfinance as mpf
import requests, time, lxml # lxml在本地端不用，但佈屬streamlit雲端就要
import matplotlib.pyplot as plt
from io import StringIO
from bs4 import BeautifulSoup

# Emoji按"Win"鍵加";" 亦可指定png檔／layout可centered
st.set_page_config(page_icon = '💯', page_title = 'Max選股', layout = 'wide', initial_sidebar_state = 'auto')
st.markdown("""<style>.main{background-color:#EFE3D8}</style>""", unsafe_allow_html = True)

choice = st.sidebar.selectbox('Menu', options = ['Home', 'US Stock', 'US Stock Backtest', 'TW Stock', 'TW Stock Backtest', 'Institutional Buyer', 'How To Learn'], index = 5)
st.sidebar.write('右上角 ≡ ☛ settings ☛ Theme 選 Light 體驗較佳')

if choice == 'Home':
    import page1
    page1.active()

elif choice == 'US Stock':
    import page2
    page2.active()

elif choice == 'US Stock Backtest':
    import page2a
    page2a.active()

elif choice == 'TW Stock':
    import page3
    page3.active()

elif choice == 'TW Stock Backtest':
    import page3a
    page3a.active()

elif choice == 'Institutional Buyer':
    import page4
    page4.active()

elif choice == 'How To Learn':
    import page5
    page5.active()
