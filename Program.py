import streamlit as st; st.set_option('deprecation.showPyplotGlobalUse', False)
import Home, Screener#, Backtest , _AfterMarket,tw_stock_bt, us_stock 

st.set_page_config(
    page_icon="💯", page_title="USStockScreener", layout="wide", initial_sidebar_state = "auto"
)

st.markdown(
    """<style>
    .main{
        background-color: #EFE3D8;
        color: #555555;
        font = bold 16px Arial, Helvetica, sans-serif;
        }
    </style>""",
    unsafe_allow_html = True,
)

choice = st.sidebar.selectbox(
    "Menu",
    options = [
        "Home",
        "Screener",
        # "Backtest",
    ],
    index = 0,
)


st.sidebar.write("Automated tools for comparing market indexes and sector stocks, featuring interactive parameter settings, and backtesting functionality within different stock pools based on predefined criteria.")
if choice == "Home":
    Home.active()
elif choice == "Screener":
    Screener.DefaultContent()
# elif choice == "Backtest":
#     Backtest.active()
