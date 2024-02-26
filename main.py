import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('株価可視化アプリ')

st.sidebar.write("""
## 表示日数
"""
)

days = st.sidebar.slider('日数を指定して下さい', 1, 20000, 300)

st.write(f"""
### 過去　**{days}日間** の株価
"""
)

@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()  # DataFrameを初期化
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = pd.to_datetime(hist.index).strftime('%d %B %Y')  # 日付時刻をフォーマット
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist]) 
    return df


st.sidebar.write("""
## 株価の範囲指定
""")

ymin, ymax = st.sidebar.slider(
    '範囲を指定してください',
    0.0, 100000.0, (0.0, 10000.0)
)

tickers = {
    'NTT': '9432.T','NTTデータ': '9613.T','キーエンス': '6861.T','任天堂': '7974.T','日立': '6501.T','JT': '2914.T','大塚商会': '4768.T',
    '光通信': '9435.T','オムロン': '6645.T','楽天グループ': '4755.T','カプコン': '9697.T','いすゞ': '7202.T','日本オラクル': '4716.T','味の素': '2802.T'
}

df = get_data(days, tickers)

companies = st.multiselect(
    '会社名を選択して下さい。',
    list(df.index),
    ['味の素','大塚商会','任天堂','オムロン','JT']
)

if not companies:
    st.error('少なくとも一社は選んでください')
else:
    data = df.loc[companies]
    st.write("## 株価(JPY)", data.sort_index())
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['Date']).rename(
        columns={'value': 'Stock Prices(JPY)'} 
    )

    chart = (
        alt.Chart(data)
        .mark_line(opacity=0.8, clip=True)
        .encode(
            x="Date:T",
            y=alt.Y("Stock Prices(JPY):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
            color = 'Name:N'
        )
    )

    st.write("## 株価(JPY)チャート")
    st.altair_chart(chart, use_container_width=True)
