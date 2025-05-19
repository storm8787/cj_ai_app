#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 시사점 예시 불러오기
def load_insight_examples(section_id):
    try:
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 6번 분석기: 연령별 성별 방문객 분석
def analyze_gender_by_age():
    st.subheader("📊 6. 연령별 성별 방문객 분석")

    uploaded_file = st.file_uploader("📂 연령별 성별 방문객 엑셀 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    # ✅ 엑셀 로딩
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        st.error("❌ 엑셀 파일을 불러오는 데 문제가 발생했습니다.")
        return

    # ✅ 필수 컬럼 확인
    required_cols = {"연령대", "구분", "남성", "여성"}
    if not required_cols.issubset(df.columns):
        st.error("❌ 엑셀 파일에 '연령대', '구분', '남성', '여성' 컬럼이 필요합니다.")
        return

    # ✅ 수치 정제
    df["남성"] = df["남성"].apply(lambda x: int(str(x).replace(",", "")) if pd.notnull(x) else 0)
    df["여성"] = df["여성"].apply(lambda x: int(str(x).replace(",", "")) if pd.notnull(x) else 0)

    # ✅ 연령대별 성별 합산
    grouped = df.groupby("연령대")[["남성", "여성"]].sum().reset_index()

    # ✅ 전체 합산
    total_male = grouped["남성"].sum()
    total_female = grouped["여성"].sum()

    # ✅ 비율 계산
    grouped["남자비율"] = (grouped["남성"] / total_male * 100).round(2)
    grouped["여자비율"] = (grouped["여성"] / total_female * 100).round(2)

    st.dataframe(grouped, use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        #reference = load_insight_examples("6_gender")

        summary = "\n".join([
            f"- {row['연령대']}: 남성 {row['남성']:,}명 / 여성 {row['여성']:,}명"
            for _, row in grouped.iterrows()
        ])

        prompt = f"""다음은 {name}({period}, {location}) 축제의 연령별 성별 방문객 분석입니다.

[연령대별 성별 방문객 수 요약]
{summary}

[참고자료]
{reference}

위 데이터를 바탕으로, 연령대별 남녀 방문자의 특징과 시사점을 3~5문장으로 간결히 작성해주세요.
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

