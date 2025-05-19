#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_insight_examples(section_id):
    try:
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def analyze_age_group():
    st.subheader("📊 5. 연령별 방문객 분석")

    uploaded_file = st.file_uploader("📂 연령대별 방문객 엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file).dropna(how="all")
    df = df[df["구분"].isin(["현지인", "외지인"])].copy()
    df["날짜정렬"] = df["날짜"].str.extract(r"(\d+)").astype(int)
    df = df.sort_values(by=["구분", "날짜정렬"], ascending=[True, False]).drop(columns="날짜정렬")

    age_cols = ["10대미만", "10대", "20대", "30대", "40대", "50대", "60대", "70대이상"]
    results = {}

    for group in ["현지인", "외지인"]:
        sub_df = df[df["구분"] == group]
        age_sums = sub_df[age_cols].applymap(lambda x: int(str(x).replace("명", "").replace(",", "")) if pd.notnull(x) else 0).sum()
        results[group] = age_sums

    total = results["현지인"] + results["외지인"]
    df_result = pd.DataFrame({
        "현지인": results["현지인"],
        "외지인": results["외지인"],
        "합계": total,
        "현지인 비율": (results["현지인"] / total).apply(lambda x: f"{x:.1%}"),
        "외지인 비율": (results["외지인"] / total).apply(lambda x: f"{x:.1%}")
    })

    st.dataframe(df_result, use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("5_age")

        age_summary = "\n".join([
            f"- {age}: 현지인 {results['현지인'][age]:,}명 / 외지인 {results['외지인'][age]:,}명 / 합계 {total[age]:,}명"
            for age in age_cols
        ])

        prompt = f"""다음은 {name}({period}, {location}) 축제의 연령대별 방문객 분석입니다.

[연령대별 방문객 수 요약]
{age_summary}

[참고자료]
{reference}

위 데이터를 참고하여, 연령대별 방문 패턴과 주요 특징을 3~5문장으로 작성해주세요.
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=700
        )
        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

