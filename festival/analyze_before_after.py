#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 백데이터 로딩 함수
def load_insight_examples(section_id):
    try:
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 전·중·후 방문객 분석 (현지인/외지인 구분)
def analyze_before_after():
    st.subheader("📊 4. 축제 전·중·후 방문객 분석")

    st.markdown("**현지인·외지인을 구분하여 축제 전 5일, 축제기간, 축제 후 5일 방문객 수를 입력해주세요.**")

    st.markdown("#### 🔹 현지인 방문객")
    col1, col2, col3 = st.columns(3)
    with col1:
        local_before = st.number_input("현지인(전)", min_value=0, step=100)
    with col2:
        local_during = st.number_input("현지인(중)", min_value=0, step=100)
    with col3:
        local_after = st.number_input("현지인(후)", min_value=0, step=100)

    st.markdown("#### 🔹 외지인 방문객")
    col4, col5, col6 = st.columns(3)
    with col4:
        tourist_before = st.number_input("외지인(전)", min_value=0, step=100)
    with col5:
        tourist_during = st.number_input("외지인(중)", min_value=0, step=100)
    with col6:
        tourist_after = st.number_input("외지인(후)", min_value=0, step=100)

    reference_avg = st.number_input("비교 기준 일평균 방문객 (예: 연평균)", min_value=0, step=10)

    if st.button("🚀 분석 실행", key="before_after_btn"):
        def calc_avg(before, during, after):
            return round(before / 5, 2), round(during / 4, 2), round(after / 5, 2)

        avg_local_before, avg_local_during, avg_local_after = calc_avg(local_before, local_during, local_after)
        avg_tourist_before, avg_tourist_during, avg_tourist_after = calc_avg(tourist_before, tourist_during, tourist_after)

        avg_total_before = avg_local_before + avg_tourist_before
        avg_total_during = avg_local_during + avg_tourist_during
        avg_total_after = avg_local_after + avg_tourist_after

        inc_rate = round((avg_total_during / avg_total_before - 1) * 100, 2) if avg_total_before else 0
        inc_from_ref = round((avg_total_during / reference_avg - 1) * 100, 2) if reference_avg else 0

        df = pd.DataFrame([
            ["일평균 방문객 수", f"{avg_total_before:,.1f}명", f"{avg_total_during:,.1f}명", f"{avg_total_after:,.1f}명"],
            ["전 대비 증가율", "-", f"{inc_rate:.2f}%", "-"],
            ["기준 대비 증가율", "-", f"{inc_from_ref:.2f}%", "-"]
        ], columns=["구분", "축제 전 (5일)", "축제기간", "축제 후 (5일)"])

        st.dataframe(df, use_container_width=True)

        # ✅ 세션에 저장
        st.session_state["summary_avg_before"] = avg_total_before
        st.session_state["summary_avg_during"] = avg_total_during
        st.session_state["summary_avg_after"] = avg_total_after
        st.session_state["summary_increase_rate"] = inc_rate
        st.session_state["summary_avg_reference"] = reference_avg
        st.session_state["summary_increase_from_reference"] = inc_from_ref
        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            prompt = f"""
다음은 {name}({period}, {location}) 축제기간 전·중·후 방문객 수 비교 결과입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 각 문장은 ▸ 기호로 시작하고, 총 3~5문장으로 구성  
▸ 증가 수치 중심의 긍정적 해석 권장  
▸ ※ 기호로 부가 설명 가능  
▸ 마지막 문장은 실무적 제언 포함  
▸ **각 문장은 줄바꿈(엔터)으로 구분될 것**

[방문객 수 요약]
- 전 기간 일평균: {avg_before:,.1f}명
- 축제기간 일평균: {avg_during:,.1f}명
- 후 기간 일평균: {avg_after:,.1f}명
- 전 대비 증가율: {inc_rate:.2f}%
- 기준(연평균 등) 대비 증가율: {inc_from_ref:.2f}%

이 데이터를 바탕으로 시사점을 작성해주세요.
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

