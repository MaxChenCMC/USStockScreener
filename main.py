import streamlit as st
import landing_page, tw_stock, tw_stock_bt, after_market, us_stock, us_stock_bt

st.set_page_config(
    page_icon="💯", page_title="Max選股", layout="wide", initial_sidebar_state="auto"
)

st.markdown(
    """<style>
.main{
    background-color: #EFE3D8;
    color: #555555;
    font = bold 16px Arial, Helvetica, sans-serif;
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
        "US Stock",
        "US Stock Backtest",
    ],
    index=0,
)
st.sidebar.write("To have a better experience...\nSettings > Theme > Light")

if choice == "Home":
    landing_page.active()

elif choice == "TW Stock":
    tw_stock.active()

elif choice == "TW Stock Backtest":
    tw_stock_bt.active()

elif choice == "After Market Disclosure":
    after_market.active()

elif choice == "US Stock":
    us_stock.active()

elif choice == "US Stock Backtest":
    us_stock_bt.active()
