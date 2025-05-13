
import streamlit as st
import pandas as pd
import plotly.express as px

fee_types_luyuan = ["電費", "水費", "瓦斯費"]
fee_types_oscar = ["電費", "度數", "公共電費", "純住宅電費", "水費", "瓦斯費"]
year_types = [year for year in range(2023, 2026)]

# set wide mode
st.set_page_config(page_title="帳單費用視覺化", layout="wide")


def prepare_filtered_data(csv_file, years, cost_types, fee_types):
    df = pd.read_csv(csv_file, encoding="utf-8")
    # print(df, years, cost_types, fee_types)


    filtered = df[df["年份"].isin(years)]
    # Make columns for each cost type and year

    print(filtered)
    for cost_type in cost_types:
        for year in years:
            filtered[f"{year}{cost_type}"] = filtered.apply(lambda x: x[cost_type] if x["年份"] == year else None, axis=1)

    bill_items = []
    for year in years:
        for cost_type in cost_types:
            bill_items.append(f"{year}{cost_type}")

    filtered = filtered.drop(columns = fee_types)

    print("######", filtered.columns)

    for item in bill_items:
        if item not in filtered.columns:
            filtered[item] = float("nan")
        else:
            filtered[item] = filtered[item].astype(float)

    return filtered, bill_items


tabs = st.tabs(["綠園帳單", "奧斯卡帳單"])

with tabs[0]:
    st.title("🏡 綠園水電瓦斯月度分析")
    st.write("可選擇多個年份及費用類型進行比較") 

    # 多選年份
    years = st.multiselect("選擇年份（可複選）", year_types, default = year_types, key = "luyuan")

    # 選擇要顯示的費用類型
    cost_types = st.multiselect("選擇要顯示的費用類型", fee_types_luyuan, default = fee_types_luyuan)

    filtered_luyuan, bill_items_luyuan = prepare_filtered_data("綠園水電瓦斯.csv", years, cost_types, fee_types_luyuan)

    df_melted = pd.melt(
        filtered_luyuan,
        id_vars=["年份", "月份"],
        value_vars=[col for col in filtered_luyuan.columns if any(y in col for y in ["2023", "2024", "2025"])],
        var_name="variable",
        value_name="value"
    )

    # 拆出年份與費用項目（例如 "2023電費" → 年份=2023, 項目=電費）
    df_melted["項目"] = df_melted["variable"].str.extract(r"(電費|水費|瓦斯費)")
    df_melted["變數年份"] = df_melted["variable"].str.extract(r"(2023|2024|2025)").astype(int)

    # 移除無效值
    df_melted = df_melted[df_melted["value"].notna()]

    st.subheader("綠園帳單")
    if not filtered_luyuan.empty and cost_types:
        fig = px.line(
            df_melted,
            x="月份",
            y="value",
            color="variable",   # 用「年份+費用類型」組合作為線條區分
            markers=True,
            title="綠園各年度各項費用趨勢"
        )

        fig.update_layout(
            xaxis=dict(tickmode='linear'),
            yaxis_title="金額（元）"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("請選擇至少一個年份與費用類型")

    # 顯示互動表格
    st.subheader("📋 費用明細表")
    st.dataframe(filtered_luyuan.sort_values(by=["年份", "月份"]).reset_index(drop=True))

with tabs[1]:
    st.title("🏡 奧斯卡水電瓦斯月度分析")
    st.write("可選擇多個年份及費用類型進行比較") 

    # 多選年份
    years = st.multiselect("選擇年份（可複選）", year_types, default = year_types, key = "oscar")

    # 選擇要顯示的費用類型
    cost_types = st.multiselect("選擇要顯示的費用類型", fee_types_oscar, default = ["純住宅電費", "水費", "瓦斯費"])

    filtered_oscar, bill_items_oscar = prepare_filtered_data("奧斯卡水電瓦斯.csv", years, cost_types, fee_types_oscar)

    df_melted = pd.melt(
        filtered_oscar,
        id_vars=["年份", "月份"],
        value_vars=[col for col in filtered_oscar.columns if any(y in col for y in ["2023", "2024", "2025"])],
        var_name="variable",
        value_name="value"
    )

    # 拆出年份與費用項目（例如 "2023電費" → 年份=2023, 項目=電費）
    df_melted["項目"] = df_melted["variable"].str.extract(r"(電費|水費|瓦斯費)")
    df_melted["變數年份"] = df_melted["variable"].str.extract(r"(2023|2024|2025)").astype(int)

    # 移除無效值
    df_melted = df_melted[df_melted["value"].notna()]

    st.subheader("綠園帳單")
    if not filtered_luyuan.empty and cost_types:
        fig = px.line(
            df_melted,
            x="月份",
            y="value",
            color="variable",   # 用「年份+費用類型」組合作為線條區分
            markers=True,
            title="綠園各年度各項費用趨勢"
        )

        fig.update_layout(
            xaxis=dict(tickmode='linear'),
            yaxis_title="金額（元）"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("請選擇至少一個年份與費用類型")

    # 顯示互動表格
    st.subheader("📋 費用明細表")
    st.dataframe(filtered_oscar.sort_values(by=["年份", "月份"]).reset_index(drop=True))
