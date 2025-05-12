import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("綠園水電瓦斯.csv")  # 假設有年份、月份、水費、電費欄位

year = st.selectbox("選擇年份", sorted(df["年份"].unique()))
filtered = df[df["年份"] == year]

fig = px.line(filtered, x="月份", y=["水費", "電費"], title=f"{year} 年水電瓦斯費")
st.plotly_chart(fig)