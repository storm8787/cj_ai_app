#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
    #st.markdown("### 📊 8. 분석결과 요약 및 종합의견")

    # ✅ 버튼 하나씩 세로로 배치
    gpt_summary = st.button("📝 분석결과(요약) 생성 및 보기")
    gpt_opinion = st.button("💡 종합의견(GPT 생성) 보기")

    # ✅ 각각 아래로 출력
    if gpt_summary:
        analyze_summary_overview(gpt_generate=True)
    
    if gpt_opinion:
        analyze_final_opinion(gpt_generate=True)

def analyze_summary_overview(gpt_generate=True):

    st.markdown("### 📝 분석요약")
    st.markdown("---")

    # ✅ 세션 값 불러오기
    festival_name = st.session_state.get("festival_name", "축제")
    year = st.session_state.get("festival_year", "2025")
    current_total = st.session_state.get("summary_total_visitors", 0)
    current_local = st.session_state.get("summary_local_visitors", 0)
    current_tourist = st.session_state.get("summary_tourist_visitors", 0)
    last_total = st.session_state.get("summary_total_visitors_prev", 0)
    last_local = st.session_state.get("summary_local_visitors_prev", 0)
    last_tourist = st.session_state.get("summary_tourist_visitors_prev", 0)

    total_diff = current_total - last_total
    local_diff = current_local - last_local
    tourist_diff = current_tourist - last_tourist

    # ✅ 증감 여부 문자열 변수 추가
    total_trend = "증가" if total_diff > 0 else "감소" if total_diff < 0 else "변화 없음"
    local_trend = "증가" if local_diff > 0 else "감소" if local_diff < 0 else "변화 없음"
    tourist_trend = "증가" if tourist_diff > 0 else "감소" if tourist_diff < 0 else "변화 없음"

    total_diff = current_total - last_total
    total_rate = (total_diff / last_total * 100) if last_total else 0
    local_diff = current_local - last_local
    local_rate = (local_diff / last_local * 100) if last_local else 0
    tourist_diff = current_tourist - last_tourist
    tourist_rate = (tourist_diff / last_tourist * 100) if last_tourist else 0
    local_ratio = (current_local / current_total * 100) if current_total else 0
    tourist_ratio = (current_tourist / current_total * 100) if current_total else 0

    top_age = st.session_state.get("summary_age_group_top", "")
    top_weekday = st.session_state.get("summary_top_day_all", "")
    top_hour = st.session_state.get("summary_top_hour_all", "")
    top_age_local = st.session_state.get("summary_age_group_top_local", "")
    top_weekday_local = st.session_state.get("summary_top_day_local", "")
    top_hour_local = st.session_state.get("summary_top_hour_local", "")
    top_age_tourist = st.session_state.get("summary_age_group_top_tourist", "")
    top_weekday_tourist = st.session_state.get("summary_top_day_tourist", "")
    top_hour_tourist = st.session_state.get("summary_top_hour_tourist", "")

    avg_daily = st.session_state.get("summary_daily_avg", 0)
    before_avg = st.session_state.get("summary_before_daily_avg", 0)
    before_ratio = (avg_daily / before_avg * 100) if before_avg else 0
    reference_avg = st.session_state.get("summary_reference_avg", 0)
    reference_ratio = (avg_daily / reference_avg * 100) if reference_avg else 0

    stay_ratio = st.session_state.get("summary_visitor_after_24h_ratio", "")
    stay_count = st.session_state.get("summary_visitor_after_24h_count", 0)

    total_sales = st.session_state.get("summary_total_sales", 0)
    daily_sales = st.session_state.get("summary_daily_sales", 0)

    top_eup = st.session_state.get("top_eupmyeondong_name", "")
    eup_ratio = st.session_state.get("top_eupmyeondong_ratio", "")

    # ✅ 1단계: 마크다운 요약 먼저 출력
    st.markdown(f"""
📊 ##본 분석은 KT 관광인구 / 국민카드 매출 데이터를 기초로 시장점유율에 따른 보정계수를 적용·산출한 **{festival_name}** 방문객과 매출현황을 분석한 결과임##

👥 {year}년 {festival_name}의 총 관광객은 **{current_total:,}명**으로 전년 **{last_total:,}명** 대비 **{total_diff:,}명({total_rate:.2f}%)** {total_trend}
   - 현지인: {current_local:,}명, 전년 대비 {abs(local_diff):,}명({local_rate:.2f}%) {'증가' if local_diff >= 0 else '감소'}  
   - 외지인: {current_tourist:,}명, 전년 대비 {abs(tourist_diff):,}명({tourist_rate:.2f}%) {'증가' if tourist_diff >= 0 else '감소'}

🧬 종합현황  
   - 전체: {top_age}, {top_weekday}, {top_hour}  
   - 현지인: {top_age_local}, {top_weekday_local}, {top_hour_local}  
   - 외지인: {top_age_tourist}, {top_weekday_tourist}, {top_hour_tourist}

📈 축제기간 중 일평균 관광객은 **{avg_daily:,}명**으로 축제 5일전 대비 **{before_ratio:.2f}% 증가**했고,
    전년도 일평균 수안보온천 관광객 보다 **{reference_ratio:.2f}% 증가**
    {festival_name}이 지역 관광 수요를 효과적으로 견인한 것을 확인

🛌 축제 방문 외지인 관광객 {stay_ratio}({stay_count:,}명)는 하루 이상 충주에 체류하며 연계관광을 즐김

💰 축제기간 주변 총 소비 매출액은 **{total_sales:,}천원** (일평균 {daily_sales:,}천원)  
   ※ 축제장 푸드트럭 제외

🗺 **축제 방문 외지인**은 축제 후 충북 전역에서 소비활동을 하였으며,
    충북내 소비금액의 81.92%가 충주시에서 소비함
   - 이 중 **{top_eup}** 에서 추가 소비가 가낭 많이 이루어짐({eup_ratio})
""")

    # ✅ 2단계: 마지막 문단 GPT 생성
    if gpt_generate:
        final_prompt = f"""
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨') 
▸ 전년도 대비 전체 방문객 수가 증가하고 외지인 비중이 확대되었으며, 축제기간 동안 {top_weekday}을 중심으로 고른 방문객 유입이 이어졌음을 행정문서체로 기술할 것  
▸ 온화한 기후나 쾌적한 환경 등 계절적 장점이 관광 수요에 기여했음을 기술  
▸ 마지막 문장은 “체류형 관광 활성화를 이끈 건강한 축제였다는 표현으로 마무리 할 것
▸ 전체적으로 긍정적이고 정책적 시사점을 부각하는 어조 유지
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하고 정책 시사점을 도출하는 전문가야."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )

        st.markdown("#### 🧠 GPT 시사점 (정책적 해석)")
        st.write(response.choices[0].message.content)


# In[ ]:




