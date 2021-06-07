import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import mplfinance as mpf
import requests, lxml # lxml在本地端不用，但佈屬streamlit雲端就要
import matplotlib.pyplot as plt

# Emoji按"Win"鍵加";" 亦可指定png檔／layout可centered
st.set_page_config(page_icon = '💯', page_title = 'Max選股', layout = 'wide', initial_sidebar_state = 'auto')
st.markdown("""<style>.main{background-color:#EFE3D8}</style>""", unsafe_allow_html = True)

choice = st.sidebar.selectbox('Menu', options = ['Home', 'US Stock', 'TW Stock', 'How To Learn'], index = 0)
st.sidebar.write('右上角 ≡ ☛ settings ☛ Theme 選 Light 體驗較佳')

if choice == 'Home':
    import page1
    page1.active()

elif choice == 'US Stock':
    import page2
    page2.active()

elif choice == 'TW Stock':
    import page3
    page3.active()

elif choice == 'How To Learn':
    import page4
    page4.active()
