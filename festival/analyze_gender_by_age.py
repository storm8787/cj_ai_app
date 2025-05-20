#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 연령대 고정 목록
age_groups = [
    "10세미만", "10대", "20대", "30대", "40대", "50대", "60대", "70대이상"
]

# ✅ 분석기 시작
def analyze_gender_by_age():
    st.subheader("📊 6. 연령별 성별 방문객 분석 (직접 입력 방식)")

    data = []

    with st.form("age_gender_form"):
        st.markdown("#### 👉 연령대별 성별 방문객 수 입력")

        for age in age_groups:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                male_local = st.number_input(f"{age} - 남성(현지인)", min_value=0, step=1, key=f"{age}_ml")
            with col2:
                male_tourist = st.number_input(f"{age} - 남성(외지인)", min_value=0, step=1, key=f"{age}_mt")
            with col3:
                female_local = st.number_input(f"{age} - 여성(현지인)", min_value=0, step=1, key=f"{age}_fl")
            with col4:
                female_tourist = st.number_input(f"{age} - 여성(외지인)", min_value=0, step=1, key=f"{age}_ft")
            data.append((age, male_local, male_tourist, female_local, female_tourist))

        submitted = st.form_submit_button("🚀 분석 실행")

    if not submitted:
        return

    # ✅ 데이터프레임 생성 및 계산
    df = pd.DataFrame(data, columns=["연령구분", "남성_현지", "남성_외지", "여성_현지", "여성_외지"])
    df["남자"] = df["남성_현지"] + df["남성_외지"]
    df["여자"] = df["여성_현지"] + df["여성_외지"]

   # 총합 기준으로 비율 계산 (남녀 각각이 아닌 전체 기준)
    grand_total = df["남자"].sum() + df["여자"].sum()

    df["남자비율"] = (df["남자"] / grand_total * 100).round(2)
    df["여자비율"] = (df["여자"] / grand_total * 100).round(2)


    result_df = df[["연령구분", "남자", "여자", "남자비율", "여자비율"]]
    st.dataframe(result_df, use_container_width=True)

    # ✅ 8번 분석기에서 활용할 수 있도록 저장
    st.session_state["summary_gender_by_age_df"] = result_df.copy()

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")

        summary = "\n".join([
            f"- {row['연령구분']}: 남성 {row['남자']:,}명 / 여성 {row['여자']:,}명"
            for _, row in result_df.iterrows()
        ])

        prompt = f"""다음은 {name}({period}, {location}) 축제의 연령대별 성별 방문객 직접 입력 데이터를 기반으로 한 분석입니다.

[연령대별 성별 방문객 수 요약]
{summary}

이 데이터를 바탕으로, 연령대별 남녀 방문자의 특징 및 주요 시사점을 3~5문장으로 간결하게 정리해주세요.
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

