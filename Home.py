import streamlit as st; st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd


def active():
    today = pd.to_datetime("today").strftime("%Y-%m-%d")
    st.image("./img/cover.jpg", use_column_width = True)
    st.markdown(
        f"<h1 style= 'text-align: center;'> {today}國際重要指數</h1>", unsafe_allow_html = True
    )
    st.markdown(
        "------------------------------------------------------------------------------------"
    )
    st.markdown(
        """
            # 市場行情短評
            ```
            none
            ```
    """
    )
    st.markdown(
    "------------------------------------------------------------------------------------"
    )
    st.title("推薦不錯的資訊管道")

    st.write("""不錯的Podcast：""")
    pod1, pod2, pod3, pod4, pod5 = st.columns([0.75, 0.75, 1, 2, 2])
    pod1.markdown(
        "##### [股癌](https://open.spotify.com/show/1zWxx5pKk0XBEzMupVC7UZ?si=PN1MkeJkRaGJ0wC-c6g-IA)"
    )
    pod2.markdown(
        "##### [財報狗](https://open.spotify.com/show/02nixW8CEcAuGOp31YdpLt?si=twaSpkZ9TYWfUzI0F7Neew)"
    )
    pod3.markdown(
        "##### [升鴻投資](https://open.spotify.com/show/195n5DWopLz7y4p2IfO8c3?si=WTjpnmRGS6S-hQUT-ZWlNA)"
    )
    pod4.markdown(
        "##### [Gamma-美股科技投資](https://open.spotify.com/show/3izX06Ke3Cgwggs8saJ0TK?si=NwWhNvSYRTu4fBkVxv8KWQ)"
    )
    pod5.markdown(
        "##### [美股投資學-財女Jenny](https://open.spotify.com/show/3dTKJkvceKNHaYoh7Przbg?si=k6jB8uJQRWCg1PMlrvNXFw)"
    )
