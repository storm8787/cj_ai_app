#!/usr/bin/env python
# coding: utf-8

# In[3]:


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

# ✅ 전체 분석기 실행 함수
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    # ✅ 축제 기본정보 입력
    festival_basic_info()

    # ✅ 분석 항목 선택
    selected = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 방문객 현황 분석",
        "2. 축제 일자별 방문객 수 분석",
        "3. 시간대별 관광객 존재현황 분석"
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
    elif selected_analysis == "4. 축제 전·중·후 방문객 분석":
        from festival.analyze_before_after import analyze_before_after
        analyze_before_after()
    elif selected_analysis == "5. 연령별 방문객 분석":
        from festival.analyze_age_group import analyze_age_group
        analyze_age_group()
    elif selected_analysis == "6. 외지인 이동지역 분석":
        from festival.analyze_mobility import analyze_mobility
        analyze_mobility()


