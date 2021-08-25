import streamlit as st
import pandas as pd


def global_index():
    df = pd.read_html("http://jsjustweb.jihsun.com.tw/z/ze/zeo/zeo.djhtm")[2]
    df.columns = list(df.iloc[2, :])
    df = df[
        df["指數名稱"].str.contains("上市")
        | df["指數名稱"].str.contains("櫃買")
        | df["指數名稱"].str.contains("道瓊指")
        | df["指數名稱"].str.contains("那斯達克")
        | df["指數名稱"].str.contains("S&P")
        | df["指數名稱"].str.contains("費城")
        | df["指數名稱"].str.contains("日經")
        | df["指數名稱"].str.contains("KOSPI")
    ]
    df.reset_index(inplace=True, drop=True)
    return df


def active():
    today = pd.to_datetime("today").strftime("%Y-%m-%d")
    st.image("./img/cover.jpg", use_column_width=True)
    st.markdown(
        f"<h1 style= 'text-align: center;'> {today}國際重要指數</h1>", unsafe_allow_html=True
    )
    st.table(global_index())

    st.markdown(
        "------------------------------------------------------------------------------------"
    )
    st.markdown(
        """
            # 市場行情幹話
            ```
            自主封城，大家WFH，白天可以光明正大盯盤炒股，資金行情源源不絕
            科技股沒明顯主流，傳產強翻天，偶爾會看到航運成交比重大於電子
            ```
    """
    )

    st.markdown(
        "------------------------------------------------------------------------------------"
    )
    st.title("最近看到不錯的酷東西")

    st.write("""不錯的Podcast：""")
    pod1, pod2, pod3, pod4, pod5 = st.beta_columns([0.75, 0.75, 1, 2, 2])
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

    st.write(
        """
    #
    ▌不錯的YouTube"""
    )
    st.write("""技術分析的使用時機與局限""")
    st.video(
        "https://www.youtube.com/watch?v=2i6zjMOHx0k",
        format="video/mp4",
        start_time=803,
    )


active()
