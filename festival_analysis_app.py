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

# ✅ 통합 분석기 실행 함수 (탭 기반)
def festival_analysis_app():
    st.markdown("""
    <style>
    /* 탭 전체 너비 늘리기 */
    .css-1e5imcs .stTabs [data-baseweb="tab"] {
        flex: 1 1 auto;
        white-space: nowrap;
    }

    /* 탭 그룹 전체의 padding과 wrapping 없애기 */
    .css-1e5imcs .stTabs {
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎯 축제 빅데이터 분석기")

    # 1. 공통정보 입력
    festival_basic_info()

    # 2. 분석기별 탭 구성
    tabs = st.tabs([
        "방문객 현황",
        "일자별 방문객",
        "시간대별 관광객",
        "전·중·후 분석",
        "연령별 방문객",
        "성별 연령",
        "시도·시군구별 방문객",
        "24시간 이후지역",
        "일자별 상권 소비매출",
        "축제 전중 소비변화",
        "방문유형별 소비현황",
        "성별/연령별 소비현황",
        "요약 및 종합의견(준비중)"
    ])

    # ✅ 각 탭에서 분석기 실행
    with tabs[0]:
        from festival.analyze_summary import analyze_summary
        analyze_summary()
    with tabs[1]:
        from festival.analyze_daily_visitor import analyze_daily_visitor
        analyze_daily_visitor()
    with tabs[2]:
        from festival.analyze_time_distribution import analyze_time_distribution
        analyze_time_distribution()
    with tabs[3]:
        from festival.analyze_before_after import analyze_before_after
        analyze_before_after()
    with tabs[4]:
        from festival.analyze_age_group import analyze_age_group
        analyze_age_group()
    with tabs[5]:
        from festival.analyze_gender_by_age import analyze_gender_by_age
        analyze_gender_by_age()
    with tabs[6]:
        from festival.analyze_visitor_by_province import analyze_visitor_by_province
        analyze_visitor_by_province()
    with tabs[7]:
        from festival.analyze_visitor_after_24h import analyze_visitor_after_24h
        analyze_visitor_after_24h()
    with tabs[8]:
        from festival.analyze_card_spending import analyze_card_spending
        analyze_card_spending()
    with tabs[9]:
        from festival.analyze_sales_before_during import analyze_sales_before_during
        analyze_sales_before_during()
    with tabs[10]:
        from festival.analyze_spending_by_visitor_type import analyze_spending_by_visitor_type
        analyze_spending_by_visitor_type()
    with tabs[11]:
        from festival.analyze_spending_by_gender_age import analyze_spending_by_gender_age
        analyze_spending_by_gender_age()    
    with tabs[-1]:
        #from festival.analyze_summary_and_opinion import analyze_summary_and_opinion
        #analyze_summary_and_opinion()
        st.subheader("📊 8. 요약 및 종합의견")
        st.info("🚧 이 기능은 현재 준비 중입니다. 다음 업데이트에서 제공될 예정입니다.")



# In[ ]:




