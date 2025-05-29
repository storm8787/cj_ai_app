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
    location = st.text_input("📍 축제장소")
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

def festival_analysis_app():
    st.markdown("""
    <style>
    /* 탭 글씨 크기와 굵기 조절 */
    [data-baseweb="tab"] > div {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("🎯 축제 빅데이터 분석기")

    # ✅ 기본정보 입력
    festival_basic_info()

    # ✅ 분석영역 선택
    section = st.selectbox("🔍 분석 영역 선택", ["방문객 분석", "카드 소비 분석", "분석요약 및 종합의견"])

    if section == "방문객 분석":
        tabs = st.tabs([
            "1. 방문객 총괄", "2. 일자별 방문객", "3. 시간대별 관광객",
            "4. 전·중·후", "5. 연령별", "6. 성별/연령", "7. 지역분석"
        ])
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

    elif section == "카드 소비 분석":
        tabs = st.tabs([
            "8. 일자별 소비", "9. 전·중 소비비교", "10. 방문유형별 소비",
            "11. 성별/연령 소비", "12. 외지인 소비지역", "13. 도내 소비현황", "14. 충주관내 소비현황"
        ])
        with tabs[0]:
            from festival.analyze_card_spending import analyze_card_spending
            analyze_card_spending()
        with tabs[1]:
            from festival.analyze_sales_before_during import analyze_sales_before_during
            analyze_sales_before_during()
        with tabs[2]:
            from festival.analyze_spending_by_visitor_type import analyze_spending_by_visitor_type
            analyze_spending_by_visitor_type()
        with tabs[3]:
            from festival.analyze_spending_by_gender_age import analyze_spending_by_gender_age
            analyze_spending_by_gender_age()
        with tabs[4]:
            from festival.analyze_external_visitor_spending_by_region import analyze_external_visitor_spending_by_region
            analyze_external_visitor_spending_by_region()
        with tabs[5]:
            from festival.analyze_internal_spending_by_region import analyze_internal_spending_by_region
            analyze_internal_spending_by_region()
        with tabs[6]:
            from festival.analyze_external_visitor_spending_in_chungju import analyze_external_visitor_spending_in_chungju
            analyze_external_visitor_spending_in_chungju()
                      
    elif section == "분석요약 및 종합의견":
        st.subheader("📋 분석요약 및 종합의견")
        
        from festival.analyze_summary_and_opinion import analyze_summary_and_opinion
        analyze_summary_and_opinion()


# In[ ]:




