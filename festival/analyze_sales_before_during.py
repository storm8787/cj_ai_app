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

def analyze_sales_before_during():
    st.subheader("📊 9. 축제 전·중 축제장 주변 매출 현황")

    # ✅ 기본 정보
    start_date = st.session_state.get("festival_start_date")
    end_date = st.session_state.get("festival_end_date")
    days = (end_date - start_date).days + 1 if start_date and end_date else None

    if not start_date or not end_date:
        st.warning("먼저 축제 기본정보를 입력해주세요.")
        return

    st.markdown("🎫 **축제기간 및 직전 1주간 매출액을 입력해주세요 (단위: 천원)**")

    this_before = st.number_input("📉 올해 직전 1주 매출액", min_value=0, step=1000, key="this_before")
    this_during = st.number_input("📈 올해 축제기간 매출액", min_value=0, step=1000, key="this_during")

    compare_last = st.radio("📂 전년도 데이터가 있나요?", ["없음", "있음"], horizontal=True)

    last_before = last_during = None
    if compare_last == "있음":
        last_before = st.number_input("📉 전년도 직전 1주 매출액", min_value=0, step=1000, key="last_before")
        last_during = st.number_input("📈 전년도 축제기간 매출액", min_value=0, step=1000, key="last_during")

    if st.button("📊 분석 실행", key="btn_analyze_sales_before_during"):
        # ✅ 올해 분석
        this_avg = int(this_during / days)
        this_diff = this_during - this_before
        this_rate = round(this_diff / this_before * 100, 1) if this_before > 0 else 0

        st.markdown(f"✅ 올해 축제기간 일평균 매출액: **{this_avg:,}천원**")
        st.markdown(f"📈 직전 1주 대비 매출 증감률: **{this_rate:+.1f}%**")

        # ✅ 전년도 비교
        last_avg = last_diff = last_rate = None
        if compare_last == "있음" and last_before and last_during:
            last_avg = int(last_during / days)
            last_diff = last_during - last_before
            last_rate = round(last_diff / last_before * 100, 1) if last_before > 0 else 0

            st.markdown("---")
            st.markdown(f"📊 전년도 축제기간 일평균 매출액: **{last_avg:,}천원**")
            st.markdown(f"📉 전년도 직전 1주 대비 증감률: **{last_rate:+.1f}%**")

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            prompt = f"""다음은 {name}({period}, {location})의 축제장 주변 매출 분석입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ ▸ 기호로 시작하여 3~5문장으로 작성  
▸ 수치 나열과 함께 원인과 배경, 정책적 맥락을 포함할 것  
▸ '직전 1주 대비 변화', '과거 연도와의 비교', '소비 여건의 영향' 등 행정적 분석 포인트 포함 
▸ 전년도 데이터가 있는 경우 비교 분석도 포함  
▸ 부정적 표현은 지양하고, 완곡하거나 중립적 표현 사용  
▸ 필요 시 ※ 표시로 부가 설명 포함 
▸ 각 문장은 줄바꿈(엔터)으로 구분되도록 작성  

## 올해 지표:
- 축제기간 총 매출: {this_during:,}천원 / 일평균 {this_avg:,}천원
- 직전 1주 매출: {this_before:,}천원
- 직전 1주 대비 증감률: {this_rate:+.1f}%

"""

            if compare_last == "있음" and last_before and last_during:
                prompt += f"""## 전년도 지표:
- 축제기간 총 매출: {last_during:,}천원 / 일평균 {last_avg:,}천원
- 직전 1주 매출: {last_before:,}천원
- 직전 1주 대비 증감률: {last_rate:+.1f}%\n"""

            prompt += "\n위 정보를 바탕으로 시사점을 작성해주세요."

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 충주시 축제의 지역 소비 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

