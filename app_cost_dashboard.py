
import streamlit as st
import pandas as pd
import plotly.express as px

fee_types_luyuan = ["電費", "水費", "瓦斯費"]
fee_types_oscar = ["總電費", "用電度數", "公共電費", "純住宅電費", "水費", "瓦斯費"]
year_types = [year for year in range(2023, 2026)]

# set wide mode
st.set_page_config(page_title="帳單費用視覺化", layout="wide")


def prepare_filtered_data(csv_file, years, cost_types, fee_types, postfix = ""):
    df = pd.read_csv(csv_file, encoding="utf-8")
    # print(df, years, cost_types, fee_types)


    filtered = df[df["年份"].isin(years)]
    # Make columns for each cost type and year

    print(filtered)
    for cost_type in cost_types:
        for year in years:
            filtered[f"{year}{postfix}{cost_type}"] = filtered.apply(lambda x: x[cost_type] if x["年份"] == year else None, axis=1)

    bill_items = []
    for year in years:
        for cost_type in cost_types:
            bill_items.append(f"{year}{postfix}{cost_type}")

    filtered = filtered.drop(columns = fee_types)

    for item in bill_items:
        if item not in filtered.columns:
            filtered[item] = float("nan")
        else:
            filtered[item] = filtered[item].astype(float)

    df_melted = pd.melt(
        filtered,
        id_vars=["年份", "月份"],
        value_vars=[col for col in filtered.columns if any(y in col for y in str(year_types))],
        var_name="variable",
        value_name="value"
    )

    # 拆出年份與費用項目（例如 "2023電費" → 年份=2023, 項目=電費）
    df_melted["項目"] = df_melted["variable"].str.extract(f"({'|'.join(fee_types)})")
    df_melted["變數年份"] = df_melted["variable"].str.extract(r"(" + "|".join(map(str, year_types)) + r")").astype(int)

    # 移除無效值
    df_melted = df_melted[df_melted["value"].notna()]

    return df_melted, bill_items



filtered_luyuan = None
bill_items_luyuan = None
filtered_oscar = None
bill_items_oscar = None



tabs = st.tabs(["民生綠園帳單", "奧斯卡帳單", "對比分析"])

with tabs[0]:
    st.title("🏡 民生綠園水電瓦斯月度分析")
    st.write("可選擇多個年份及費用類型進行比較") 

    # 多選年份
    years = st.multiselect("選擇年份（可複選）", year_types, default = year_types, key = "luyuan")

    # 選擇要顯示的費用類型
    cost_types = st.multiselect("選擇要顯示的費用類型", fee_types_luyuan, default = fee_types_luyuan)

    filtered_luyuan, bill_items_luyuan = prepare_filtered_data("綠園帳單.csv", years, cost_types, fee_types_luyuan)

    st.subheader("民生綠園帳單")
    if not filtered_luyuan.empty and cost_types:
        fig = px.line(
            filtered_luyuan,
            x = "月份",
            y = "value",
            color = "variable",   # 用「年份+費用類型」組合作為線條區分
            markers = True,
            title = "綠園各年度各項費用趨勢"
        )

        fig.update_layout(
            xaxis = dict(tickmode='linear'),
            yaxis_title = "金額（元）"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("請選擇至少一個年份與費用類型")

    # 顯示互動表格
    st.subheader("📋 費用明細表")
    st.dataframe(filtered_luyuan.sort_values(by=["年份", "月份"]).reset_index(drop=True))

with tabs[1]:
    st.title("🏡 展昇奧斯卡水電瓦斯月度分析")
    st.write("可選擇多個年份及費用類型進行比較") 

    # 多選年份
    years = st.multiselect("選擇年份（可複選）", year_types, default = year_types, key = "oscar")

    # 選擇要顯示的費用類型
    cost_types = st.multiselect("選擇要顯示的費用類型", fee_types_oscar, default = ["總電費", "水費", "瓦斯費"])

    filtered_oscar, bill_items_oscar = prepare_filtered_data("奧斯卡帳單.csv", years, cost_types, fee_types_oscar)

    st.subheader("展昇奧斯卡帳單")
    if not filtered_luyuan.empty and cost_types:
        fig = px.line(
            filtered_oscar,
            x = "月份",
            y = "value",
            color = "variable",   # 用「年份+費用類型」組合作為線條區分
            markers = True,
            title = "展昇奧斯卡各年度各項費用趨勢"
        )
        fig.update_layout(
            xaxis = dict(tickmode='linear'),
            yaxis_title = "金額（元）"
            # always show figure
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("請選擇至少一個年份與費用類型")

    # 顯示互動表格
    st.subheader("📋 費用明細表")
    st.dataframe(filtered_oscar.sort_values(by=["年份", "月份"]).reset_index(drop=True))

with tabs[2]:
    st.title("🏡 民生綠園 vs 奧斯卡水電瓦斯月度分析")
    st.write("可選擇多個年份及費用類型進行比較") 

    # 多選年份
    years = st.multiselect("選擇年份（可複選）", year_types, default = year_types, key = "compare")

    # 選擇要顯示的費用類型
    cost_types = st.multiselect("選擇要顯示的費用類型", fee_types_luyuan, default = fee_types_luyuan, key = "compare_cost")

    filtered_luyuan, bill_items_luyuan = prepare_filtered_data("綠園帳單.csv", years, cost_types, fee_types_luyuan, "綠園")

    cost_types_oscar = cost_types.copy()
    if "電費" in cost_types_oscar:
        cost_types_oscar.remove("電費")
        cost_types_oscar.append("純住宅電費")

    filtered_oscar, bill_items_oscar = prepare_filtered_data("奧斯卡帳單.csv", years, cost_types_oscar, fee_types_oscar, "奧斯卡")

    # concate two dataframes
    filtered = pd.concat([filtered_luyuan, filtered_oscar])

    print(filtered)

    if not filtered_luyuan.empty and not filtered_oscar.empty and cost_types:
        fig = px.line(
            filtered,
            x = "月份",
            y = "value",
            color = "variable",   # 用「年份+費用類型」組合作為線條區分
            markers = True,
            title = "民生綠園 vs 奧斯卡各年度各項費用趨勢"
        )
        fig.update_layout(
            xaxis = dict(tickmode='linear'),
            yaxis_title = "金額（元）"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("請選擇至少一個年份與費用類型")

    # 顯示互動表格
    st.subheader("📋 費用明細表")
    st.dataframe(pd.concat([filtered_luyuan, filtered_oscar]).sort_values(by=["年份", "月份"]).reset_index(drop=True))