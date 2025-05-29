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

import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_before_after():
    st.subheader("📊 4. 축제 전·중·후 방문객 분석")
    st.markdown("**현지인·외지인을 구분하여 2024년 일평균 및 축제 전후 방문객 수를 입력해주세요.**")

    col_avg1, col_avg2 = st.columns(2)
    with col_avg1:
        avg_local = st.number_input("전년도 현지인 일평균 방문객", min_value=0, step=10)
    with col_avg2:
        avg_tourist = st.number_input("전년도 외지인 일평균 방문객", min_value=0, step=10)
    avg_total = avg_local + avg_tourist

    col1, col2, col3 = st.columns(3)
    with col1:
        local_before = st.number_input("현지인(축제 전 5일)", min_value=0, step=100)
    with col2:
        local_during = st.number_input("현지인(축제기간)", min_value=0, step=100)
    with col3:
        local_after = st.number_input("현지인(축제 후 5일)", min_value=0, step=100)

    col4, col5, col6 = st.columns(3)
    with col4:
        tourist_before = st.number_input("외지인(축제 전 5일)", min_value=0, step=100)
    with col5:
        tourist_during = st.number_input("외지인(축제기간)", min_value=0, step=100)
    with col6:
        tourist_after = st.number_input("외지인(축제 후 5일)", min_value=0, step=100)

    if st.button("🚀 분석 실행", key="before_after_btn"):
        # 일평균 계산
        local_avg_before = round(local_before / 5, 1)
        local_avg_during = round(local_during / 4, 1)
        local_avg_after = round(local_after / 5, 1)

        tourist_avg_before = round(tourist_before / 5, 1)
        tourist_avg_during = round(tourist_during / 4, 1)
        tourist_avg_after = round(tourist_after / 5, 1)

        # 합계
        total_avg_2024 = local_avg_2024 + tourist_avg_2024
        total_before = local_avg_before + tourist_avg_before
        total_during = local_avg_during + tourist_avg_during
        total_after = local_avg_after + tourist_avg_after

        # 증가율
        def calc_rate(before, during):
            return round((during / before - 1) * 100, 2) if before else 0.0

        local_rate = calc_rate(local_avg_before, local_avg_during)
        tourist_rate = calc_rate(tourist_avg_before, tourist_avg_during)
        total_rate = calc_rate(total_before, total_during)

        # 표 생성
        df = pd.DataFrame([
            ["현지인", f"{local_avg_2024:,}명", f"{local_avg_before:,}명", f"{local_avg_during:,}명", f"{local_avg_after:,}명", f"({local_rate:.2f}% 증가)"],
            ["외지인", f"{tourist_avg_2024:,}명", f"{tourist_avg_before:,}명", f"{tourist_avg_during:,}명", f"{tourist_avg_after:,}명", f"({tourist_rate:.2f}% 증가)"],
            ["합 계", f"{total_avg_2024:,}명", f"{total_before:,}명", f"{total_during:,}명", f"{total_after:,}명", f"({total_rate:.2f}% 증가)"],
        ], columns=["구분", "2024년 일평균", "축제 전", "축제기간", "축제 후", "비고"])

        st.dataframe(df, use_container_width=True)

        st.session_state["summary_avg_before"] = avg_total_before
        st.session_state["summary_avg_during"] = avg_total_during
        st.session_state["summary_avg_after"] = avg_total_after
        st.session_state["summary_increase_rate"] = inc_rate
        st.session_state["summary_avg_reference"] = avg_total
        st.session_state["summary_increase_from_reference"] = inc_from_ref

        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            prompt = f"""
다음은 {name}({period}, {location}) 축제기간 전·중·후 방문객 수 분석 결과입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 각 문장은 ▸ 기호로 시작하고, 총 4~6문장으로 구성  
▸ 분석 내용은 현지인·외지인을 구분하여 작성  
▸ 총 방문객 수 기준 전 대비·기준 대비 증가율을 긍정적으로 해석할 것  
▸ ※ 기호(※, ◎ 등)를 활용하여 부가 설명 가능  
▸ 마지막 문장은 실무적 제언 포함 (예: 체류형 관광 유도, 지역 상권 연계 전략 등)  
▸ **각 문장은 줄바꿈(엔터)으로 구분할 것**

[분석 요약]
- 현지인 일평균 방문객: 전 {avg_local_before:,.1f}명 / 중 {avg_local_during:,.1f}명 / 후 {avg_local_after:,.1f}명  
- 외지인 일평균 방문객: 전 {avg_tourist_before:,.1f}명 / 중 {avg_tourist_during:,.1f}명 / 후 {avg_tourist_after:,.1f}명  
- 전체 방문객 일평균: 전 {avg_total_before:,.1f}명 / 중 {avg_total_during:,.1f}명 / 후 {avg_total_after:,.1f}명  
- 전 기간 대비 축제기간 증가율: {inc_rate:.2f}%  
- 기준(연평균 등) 대비 축제기간 증가율: {inc_from_ref:.2f}%
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

