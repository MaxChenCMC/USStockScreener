import streamlit as st
import streamlit.components.v1 as components
# google搜圖右鍵 copy img addr.

def active():
    components.iframe('https://www.thebalance.com/thmb/UZS2curMfBJpwbb8LrvpxttXhA0=/2103x1428/filters:fill(auto,1)/Stock-Market-Charts-Are-Useless-56a093595f9b58eba4b1ae5b.jpg')
    expand = st.beta_expander('About')
    expand.markdown("""
    # 關於自學Python，我一律建議 ~~放棄~~
    ```
    ▌免費資源
    繁體中文資源首推<FinLab財經實驗室>(沒業配)、政大蔡炎龍的也不錯。
    還是以Youtube為主，當看過幾個影片後，演算法就會推薦你滿滿的類似教學了。
    不過免費的最貴，自學超沒效，英聽還不能太差，且要習慣印度腔。
    ```
    ```
    ▌線下教學
    好學的妹子我很樂意教，男生的話…看緣份。
    我有程式碼，你有酒或大餐嗎？
    ```
    `求職`
    沒軟體工程業界經驗的中年男子仍想混口飯吃，求大大們引薦。
    """)

