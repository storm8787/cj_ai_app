#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
from datetime import date, timedelta
from openai import OpenAI
from datetime import datetime

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 시사점 예시 불러오기
def load_insight_examples(section_id):
    try:
        with open(f"data/insights/{section_id}.txt", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 공통 정보 입력부
def festival_basic_info():
    st.subheader("📌 축제 기본정보 입력")

    festival_name = st.text_input("🎪 축제명")
    location = st.text_input("📍 축제 장소")
    start_date = st.date_input("🗓 축제 시작일")
    end_date = st.date_input("🏁 축제 종료일")

    period = f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"
    days = (end_date - start_date).days + 1

    st.session_state["festival_name"] = festival_name
    st.session_state["festival_location"] = location
    st.session_state["festival_period"] = period
    st.session_state["festival_days"] = days
    st.session_state["festival_start_date"] = start_date
    st.session_state["festival_end_date"] = end_date

# ✅ 전체 분석기 실행 함수
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    # ✅ 축제 기본정보 입력
    festival_basic_info()

    # ✅ 분석 항목 선택
    selected_analysis = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 방문객 현황(총괄)",
        "2. 축제 일자별 방문객 수",
        "3. 시간대별 관광객 존재 현황",
        "4. 축제 전·중·후 방문객 현황",
        "5. 연령별 방문객 현황"        
    ])

    # ✅ 항목별 실행
    if selected_analysis == "1. 축제 방문객 현황(총괄)":
        from festival.analyze_summary import analyze_summary
        analyze_summary()
    elif selected_analysis == "2. 축제 일자별 방문객 수":
        from festival.analyze_daily_visitor import analyze_daily_visitor
        analyze_daily_visitor()
    elif selected_analysis == "3. 시간대별 관광객 존재 현황":
        from festival.analyze_time_distribution import analyze_time_distribution
        analyze_time_distribution()
    elif selected_analysis == "4. 축제 전·중·후 방문객 현황":
        from festival.analyze_before_after import analyze_before_after
        analyze_before_after()
    elif selected_analysis == "5. 연령별 방문객 현황":
        from festival.analyze_age_group import analyze_age_group
        analyze_age_group()
    #elif selected_analysis == "6. 외지인 이동지역 분석":
    #    from festival.analyze_mobility import analyze_mobility
    #    analyze_mobility()



# In[ ]:




