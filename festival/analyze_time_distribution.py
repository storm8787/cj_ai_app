#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI()

# ✅ 백데이터 로딩
def load_daily_reference():
    path = os.path.join("press_release_app", "data", "insights", "3_time.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
# ✅ 3번 분석기: 시간대별 관광객 존재현황 분석(표 + GPT 시사점)
def analyze_time_distribution():
    st.subheader("📊 3. 시간대별 관광객 존재현황 분석")
    st.markdown("시간대별 관광객 데이터를 포함한 엑셀 파일을 업로드하세요.")

    df = pd.DataFrame({
        "구분": ["현지인", "현지인", "현지인", "외지인", "외지인", "외지인"],
        "날짜": ["3일차", "2일차", "1일차", "3일차", "2일차", "1일차"],
        "06시 관광객": 0, "07시 관광객": 0, "08시 관광객": 0, "09시 관광객": 0,
        "10시 관광객": 0, "11시 관광객": 0, "12시 관광객": 0, "13시 관광객": 0,
        "14시 관광객": 0, "15시 관광객": 0, "16시 관광객": 0, "17시 관광객": 0,
        "18시 관광객": 0, "19시 관광객": 0, "20시 관광객": 0, "21시 관광객": 0,
        "22시 관광객": 0, "23시 관광객": 0
    })
    df.to_excel("data/templates/3_template.xlsx", index=False)

    uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ 시간대 그룹 정의
    time_groups = [
        ("06~09시", ["06시 관광객", "07시 관광객", "08시 관광객"]),
        ("09~12시", ["09시 관광객", "10시 관광객", "11시 관광객"]),
        ("12~15시", ["12시 관광객", "13시 관광객", "14시 관광객"]),
        ("15~18시", ["15시 관광객", "16시 관광객", "17시 관광객"]),
        ("18~21시", ["18시 관광객", "19시 관광객", "20시 관광객"]),
        ("21~24시", ["21시 관광객", "22시 관광객", "23시 관광객"]),
    ]

    # ✅ 현지인/외지인 분리 및 1일차부터 라벨링 (역순정렬 기준)
    local_df = df[df.iloc[:, 0] == "현지인"].copy().iloc[::-1].reset_index(drop=True)
    tourist_df = df[df.iloc[:, 0] == "외지인"].copy().iloc[::-1].reset_index(drop=True)

    local_df["날짜라벨"] = [f"{i+1}일차" for i in range(len(local_df))]
    tourist_df["날짜라벨"] = [f"{i+1}일차" for i in range(len(tourist_df))]

    result_rows = []

    def process_group(df_group, label):
        group_data = []
        for i, row in df_group.iterrows():
            day_data = {"구분": label, "날짜": row["날짜라벨"]}
            for group_name, cols in time_groups:
                total = sum([
                    int(str(row[col]).replace(",", "").replace("명", "")) if pd.notnull(row[col]) else 0
                    for col in cols
                ])
                day_data[group_name] = f"{total:,}명"
            group_data.append(day_data)
        return group_data

    def process_ratio(df_group, label):
        rows = [{"구분": "", "날짜": ""}]  # 공백 행
        for i, row in df_group.iterrows():
            ratio_row = {"구분": label, "날짜": ""}
            total = sum([
                int(str(row[col]).replace(",", "").replace("명", "")) if pd.notnull(row[col]) else 0
                for _, cols in time_groups for col in cols
            ])
            for group_name, cols in time_groups:
                subtotal = sum([
                    int(str(row[col]).replace(",", "").replace("명", "")) if pd.notnull(row[col]) else 0
                    for col in cols
                ])
                ratio_row[group_name] = f"{subtotal/total:.2%}" if total > 0 else "-"
            rows.append(ratio_row)
        return rows

    # ✅ 방문객 수 및 비율 계산
    result_rows.extend(process_group(local_df, "현지인"))
    result_rows.extend(process_group(tourist_df, "외지인"))
    result_rows.extend(process_ratio(local_df, "현지인"))
    result_rows.extend(process_ratio(tourist_df, "외지인"))

    # ✅ 출력
    st.subheader("📊 시간대별 관광객 현황")
    st.dataframe(pd.DataFrame(result_rows), use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        examples = load_daily_reference()
        lines = []

        for group_name, cols in time_groups:
            local_vals = []
            tourist_vals = []

            for i in range(len(local_df)):
                subtotal_local = sum([
                    int(str(local_df.iloc[i][col]).replace(",", "").replace("명", "")) if pd.notnull(local_df.iloc[i][col]) else 0
                    for col in cols
                ])
                local_vals.append(subtotal_local)

            for i in range(len(tourist_df)):
                subtotal_tourist = sum([
                    int(str(tourist_df.iloc[i][col]).replace(",", "").replace("명", "")) if pd.notnull(tourist_df.iloc[i][col]) else 0
                    for col in cols
                ])
                tourist_vals.append(subtotal_tourist)

            lines.append(f"{group_name} - 현지인: " + ", ".join(f"{v:,}명" for v in local_vals))
        lines.append(f"{group_name} - 외지인: " + ", ".join(f"{v:,}명" for v in tourist_vals))

        prompt = f"""
    [유사 시사점 예시]
    {examples}

    [시간대별 관광객 수]
    {chr(10).join(lines)}

    위 데이터를 참고하여 시간대별 특성과 변화 양상을 행정 보고서 스타일로 3~5문장 작성해주세요.
    """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

