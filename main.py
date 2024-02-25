import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFAM+α 株価
こちらは株価可視化ツールです。

オプションによりグラフが変動します。
"""
)

st.sidebar.write("""
## 表示日数
"""
)

days = st.sidebar.slider('日数を指定して下さい', 1, 50, 20)

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
    0.0, 1000.0, (0.0, 1000.0)
)

tickers = {
    'apple': 'AAPL',
    'meta': 'META',
    'google': 'GOOGL',
    'microsoft': 'MSFT',
    'netflix': 'NFLX',
    'amazon': 'AMZN',
}

df = get_data(days, tickers)

companies = st.multiselect(
    '会社名を選択して下さい。',
    list(df.index),
    ['google', 'amazon', 'meta', 'apple','microsoft']
)

if not companies:
    st.error('少なくとも一社は選んでください')
else:
    data = df.loc[companies]
    st.write("## 株価(USD)", data.sort_index())
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['Date']).rename(
        columns={'value': 'Stock Prices(USD)'} 
    )

    chart = (
        alt.Chart(data)
        .mark_line(opacity=0.8, clip=True)
        .encode(
            x="Date:T",
            y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
            color = 'Name:N'
        )
    )

    st.write("## 株価(USD)チャート")
    st.altair_chart(chart, use_container_width=True)

