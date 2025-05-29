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
        path = f"press_release_app/data/insights/{section_id}.txt"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 8. 분석결과 요약 및 종합의견
def analyze_summary_and_opinion():
    st.markdown("### 📊 8. 분석결과 요약 및 종합의견")

    # ✅ 버튼 하나씩 세로로 배치
    gpt_summary = st.button("📝 분석결과(요약) 생성 및 보기")
    gpt_opinion = st.button("💡 종합의견(GPT 생성) 보기")

    # ✅ 각각 아래로 출력
    if gpt_summary:
        analyze_summary_overview(gpt_generate=True)
    
    if gpt_opinion:
        analyze_final_opinion(gpt_generate=True)

def analyze_summary_overview():
    import streamlit as st

    # ✅ 기본 정보 불러오기
    festival_name = st.session_state.get("festival_name", "축제")
    festival_period = st.session_state.get("festival_period", "")
    festival_location = st.session_state.get("festival_location", "")
    festival_season = st.session_state.get("festival_season", "")
    program_features = st.session_state.get("program_features", "특색있는 프로그램 구성")

    # ✅ 방문객 수
    current_total = st.session_state.get("summary_total_visitors", 0)
    current_local = st.session_state.get("summary_local_visitors", 0)
    current_tourist = st.session_state.get("summary_tourist_visitors", 0)

    last_total = st.session_state.get("summary_total_visitors_lastyear", 0)
    last_local = st.session_state.get("summary_local_visitors_lastyear", 0)
    last_tourist = st.session_state.get("summary_tourist_visitors_lastyear", 0)

    # ✅ 비율 및 증감 계산
    diff_total = current_total - last_total
    rate_total = (diff_total / last_total * 100) if last_total else 0
    diff_status = "증가" if diff_total >= 0 else "감소"

    diff_local = current_local - last_local
    rate_local = (diff_local / last_local * 100) if last_local else 0

    diff_tourist = current_tourist - last_tourist
    rate_tourist = (diff_tourist / last_tourist * 100) if last_tourist else 0

    rate_local_ratio = (current_local / current_total * 100) if current_total else 0
    rate_tourist_ratio = (current_tourist / current_total * 100) if current_total else 0

    # ✅ 시사점 고정 템플릿 출력
    st.markdown("### 📝 분석요약(행정문서체)")
    st.markdown("---")

    st.markdown(f"""\
 본 분석은 KT 관광인구 / 국민카드 매출 데이터를 기초로 시장점유율에 따른 보정계수를 적용·산출한 {festival_name} 방문객과 매출현황을 분석한 결과임

❍ {festival_name}의 총 관광객은 {current_total:,}명으로 전년 {last_total:,}명 대비 {abs(diff_total):,}명({rate_total:.2f}%) {diff_status}
  - 현지인은 {current_local:,}명({rate_local_ratio:.2f}%)으로 전년 {last_local:,}명 대비 {abs(diff_local):,}명({rate_local:.2f}%) {'증가' if diff_local >= 0 else '감소'}
  - 외지인은 {current_tourist:,}명({rate_tourist_ratio:.2f}%)으로 전년 {last_tourist:,}명 대비 {abs(diff_tourist):,}명({rate_tourist:.2f}%) {'증가' if diff_tourist >= 0 else '감소'}

❍ 축제기간은 {festival_period}로, 총 {st.session_state.get("festival_days", 'N일')}간 운영되었음

❍ {program_features}가 긍정적으로 작용하여 체류형 관광 활성화를 이끈 건강하고 따뜻한 {festival_season} 대표 축제로 자리매김
""")

    # 📌 다음 요약요소(GPT 기반 또는 수치기반) 삽입 가능: 체류율, 소비금액, 요일별 분포 등

