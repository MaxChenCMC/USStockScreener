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
            # 市場行情短評
            ```
            台股航運是因為籌碼被玩爛了，不管之前的暴漲十倍，或是現在腰斬沈船中，主要還是籌碼介入太深。
            若看評價面，長榮已經不比ZIM, MATX或其他同業貴，今年本益比可能只有3-4倍。
            當時大家都說3Q21運價高點反轉，現在看起來，可能比當時還更塞。
            投資不能只看股價漲就說好話，股價跌就換種說法，中心思想要一致。
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

    st.write(
        """
    #
    ▌不錯的YouTube"""
    )
    st.write("""##### 技術分析的使用時機與局限""")
    st.video(
        "https://www.youtube.com/watch?v=2i6zjMOHx0k",
        format="video/mp4",
        start_time=803,
    )


active()
