
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="水電瓦斯視覺化", layout="centered")

st.title("🏡 綠園水電瓦斯月度分析")
st.write("可選擇多個年份及費用類型進行比較")

# 讀取資料
df = pd.read_csv("utility_cost_full.csv")

# 多選年份
years = st.multiselect("選擇年份（可複選）", sorted(df["年份"].unique()), default=sorted(df["年份"].unique()))
filtered = df[df["年份"].isin(years)]

# 選擇要顯示的費用類型
cost_types = st.multiselect("選擇要顯示的費用類型", ["電費", "水費", "瓦斯費"], default=["電費", "水費", "瓦斯費"])

# 畫圖（每個費用類型一條線）
if not filtered.empty and cost_types:
    fig = px.line(
        filtered,
        x="月份",
        y=cost_types,
        color="年份",
        markers=True,
        labels={"value": "金額（元）", "月份": "月份", "variable": "項目"},
        title="水電瓦斯月度趨勢比較"
    )
    fig.update_layout(xaxis=dict(tickmode='linear'), yaxis_title="金額（元）")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("請選擇至少一個年份與費用類型")

# 顯示互動表格
st.subheader("📋 費用明細表")
st.dataframe(filtered.sort_values(by=["年份", "月份"]).reset_index(drop=True))
