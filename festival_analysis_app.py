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
    st.title("🎯 축제 빅데이터 분석기")

    # ✅ 기본정보 입력
    festival_basic_info()

    # ✅ 대분류 구간
    category = st.radio("📌 분석 카테고리 선택", ["👣 방문객 분석", "💳 카드 소비 분석", "📋 종합 분석"], horizontal=True)

    if category == "👣 방문객 분석":
        selected = st.selectbox("📁 방문객 분석기 선택", [
            "1. 방문객 총괄 분석",
            "2. 일자별 방문객 분석",
            "3. 시간대별 관광객 분석",
            "4. 전·중·후 방문객 분석",
            "5. 연령별 방문객 분석",
            "6. 성별/연령별 방문객 분석",
            "7. 외지인 거주지역 분석",
            "7-3. 방문 24시간 이후 지역 분석"
        ])
        if selected.startswith("1."):
            from festival.analyze_summary import analyze_summary
            analyze_summary()
        elif selected.startswith("2."):
            from festival.analyze_daily_visitor import analyze_daily_visitor
            analyze_daily_visitor()
        elif selected.startswith("3."):
            from festival.analyze_time_distribution import analyze_time_distribution
            analyze_time_distribution()
        elif selected.startswith("4."):
            from festival.analyze_before_after import analyze_before_after
            analyze_before_after()
        elif selected.startswith("5."):
            from festival.analyze_age_group import analyze_age_group
            analyze_age_group()
        elif selected.startswith("6."):
            from festival.analyze_gender_by_age import analyze_gender_by_age
            analyze_gender_by_age()
        elif selected.startswith("7."):
            from festival.analyze_visitor_by_province import analyze_visitor_by_province
            analyze_visitor_by_province()
        elif selected.startswith("7-3."):
            from festival.analyze_visitor_after_24h import analyze_visitor_after_24h
            analyze_visitor_after_24h()

    elif category == "💳 카드 소비 분석":
        selected = st.selectbox("📁 카드 소비 분석기 선택", [
            "8. 일자별 소비 분석기",
            "9. 축제 전·중 소비 분석",
            "10. 방문유형별 소비현황",
            "11. 성별/연령별 소비현황",
            "12. 외지인 소비지역 분석"
        ])
        if selected.startswith("8."):
            from festival.analyze_card_spending import analyze_card_spending
            analyze_card_spending()
        elif selected.startswith("9."):
            from festival.analyze_sales_before_during import analyze_sales_before_during
            analyze_sales_before_during()
        elif selected.startswith("10."):
            from festival.analyze_spending_by_visitor_type import analyze_spending_by_visitor_type
            analyze_spending_by_visitor_type()
        elif selected.startswith("11."):
            from festival.analyze_spending_by_gender_age import analyze_spending_by_gender_age
            analyze_spending_by_gender_age()
        elif selected.startswith("12."):
            from festival.analyze_external_visitor_spending_by_region import analyze_external_visitor_spending_by_region
            analyze_external_visitor_spending_by_region()

    elif category == "📋 종합 분석":
        #from festival.analyze_summary_and_opinion import analyze_summary_and_opinion
        #analyze_summary_and_opinion()
        st.subheader("📊 13. 요약 및 종합의견")
        st.info("🚧 이 기능은 현재 준비 중입니다. 다음 업데이트에서 제공될 예정입니다.")


# In[ ]:




