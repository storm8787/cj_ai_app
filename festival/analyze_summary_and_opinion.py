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

    # ✅ 외지인 유입지역 Top3 (시도 / 시군구 기준) 불러오기
    top3_sido_str = st.session_state.get("summary_external_top_region_top3_str", "")
    top3_gungu_str = st.session_state.get("summary_external_top_region_full_top3_str", "")


    avg_daily = st.session_state.get("summary_avg_during", 0)       # 축제기간 일평균
    before_avg = st.session_state.get("summary_avg_before", 0)      # 축제 전 일평균
    reference_avg = st.session_state.get("summary_reference_avg", 0)    # 전년도 일평균

    # 축제기간 일평균 관광객 수가 축제 5일 전 일평균 관광객 수 대비 몇 % 증가했는지 계산 (이전 수치가 0일 경우 0으로 처리)
    before_ratio = ((avg_daily-before_avg) / before_avg * 100) if before_avg else 0 
    # 축제기간 일평균 관광객 수가 전년도 수안보온천 일평균 관광객 수 대비 몇 % 증가했는지 계산 (기준 수치가 0일 경우 0으로 처리)
    reference_ratio = ((avg_daily-reference_avg) / reference_avg * 100) if reference_avg else 0
    
    stay_ratio = st.session_state.get("summary_visitor_after_24h_top1_ratio", "")
    stay_count = st.session_state.get("summary_visitor_after_24h_top1_count", 0)

    total_sales = st.session_state.get("summary_card_total_sales", 0)
    daily_sales = st.session_state.get("summary_card_avg_sales_per_day", 0)

    this_before = st.session_state["summary_sales_before_this"]   # 올해 직전 1주 매출액 (천원)
    this_before_per_day = st.session_state["summary_sales_before_this_per_day"]  # 올해 직전 1주 일평균 매출액 (천원)
    this_rate = st.session_state["summary_sales_change_this"]    # 올해 증감률 (%)

    top_region_ratio = st.session_state["summary_external_top_region_ratio"]

    top_eup = st.session_state.get("top_eupmyeondong_name", "")
    eup_ratio = st.session_state.get("top_eupmyeondong_ratio", "")

    # ✅ 1단계: 마크다운 요약 먼저 출력
    st.markdown(f"""
📊 **본 분석은 KT 관광인구 / 국민카드 매출 데이터를 기초로 시장점유율에 따른 보정계수를 적용·산출한 **{festival_name}** 방문객과 매출현황을 분석한 결과임**

📍 {year}년 {festival_name}의 총 관광객은 **{current_total:,}명**으로 전년 **{last_total:,}명** 대비 **{total_diff:,}명({total_rate:.2f}%)** {total_trend}
   - 현지인: {current_local:,}명, 전년 대비 {abs(local_diff):,}명({local_rate:.2f}%) {'증가' if local_diff >= 0 else '감소'}  
   - 외지인: {current_tourist:,}명, 전년 대비 {abs(tourist_diff):,}명({tourist_rate:.2f}%) {'증가' if tourist_diff >= 0 else '감소'}

🧬 종합현황  
   - 전체: {top_age}, {top_weekday}, {top_hour}  
   - 현지인: {top_age_local}, {top_weekday_local}, {top_hour_local}  
   - 외지인: {top_age_tourist}, {top_weekday_tourist}, {top_hour_tourist}""")

    st.markdown(f"""
📍 축제기간 중 일평균 관광객은 **{avg_daily:,}명**으로 축제 5일전 대비 **{before_ratio:.2f}% 증가**했고, 전년도 일평균 수안보온천 관광객보다 **{reference_ratio:.2f}% 증가**하여  
&nbsp;&nbsp;&nbsp;&nbsp;**{festival_name}**이 지역 관광 수요를 효과적으로 견인한 것을 확인 """, unsafe_allow_html=True)
    
    st.markdown(f"""
📍 외지인 유입지역으로는 시도 기준 **{top3_sido_str}** 순으로 방문이 많았으며,  
&nbsp;&nbsp;&nbsp;&nbsp;시군 기준으로는 **{top3_gungu_str}** 순으로 나타남.
""", unsafe_allow_html=True)


    st.markdown(f"""
📍 축제 방문 외지인 관광객 {stay_ratio:.2f}%({stay_count:,}명)는 하루 이상 충주에 체류하며 연계관광을 즐김

📍 축제기간 주변 총 소비 매출액은 **{total_sales:,}천원** (일평균 : {daily_sales:,}천원)으로 축제 전주 **{this_before:,}천원**
(일평균 : {this_before_per_day}) 대비 **{this_rate:.2f}%** 증가함  
   ※ 축제장소 내 푸드트럭은 사업자가 타지로 등록되어 집계에 미포함

📍 **축제 방문 외지인**은 축제 후 충북 전역에서 소비활동을 하였으며,
    충북내 소비금액의 {top_region_ratio}가 충주시에서 소비함
   - 이 중 **{top_eup}** 에서 추가 소비가 가장 많이 이루어짐({eup_ratio})
""")

    # ✅ 2단계: 마지막 문단 GPT 생성
    if gpt_generate:
        final_prompt = f"""
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨') 
▸ 첫 문장은 "{festival_name} 방문객 분석 결과"로 시작
▸ 전년도 대비 전체 방문객 수가 증가하고 외지인 비중이 확대되었으며, 축제기간 동안 {top_weekday}을 중심으로 고른 방문객 유입이 이어졌음을 행정문서체로 기술할 것  
▸ 온화한 기후나 쾌적한 환경 등 계절적 장점이 관광 수요에 기여했음을 기술  
▸ 마지막 문장은 “체류형 관광 활성화를 이끈 건강한 축제였다는 표현으로 마무리 할 것
▸ 전체적으로 긍정적이고 정책적 시사점을 부각하는 어조 유지
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 데이터를 분석하고 정책 시사점을 도출하는 전문가야."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )

        st.markdown("#### 🧠 GPT 시사점 (정책적 해석)")
        st.write(response.choices[0].message.content)

def analyze_final_opinion(gpt_generate=True):
    st.markdown("### 💡 종합의견")
    st.markdown("---")

    # ✅ 세션 값 불러오기
    festival_name = st.session_state.get("festival_name", "축제")
    year = st.session_state.get("festival_year", "2025")
    
    # 방문객 관련
    current_total = st.session_state.get("summary_total_visitors", 0)
    last_total = st.session_state.get("summary_total_visitors_prev", 0)
    total_diff = current_total - last_total
    total_rate = (total_diff / last_total * 100) if last_total else 0

    current_tourist = st.session_state.get("summary_tourist_visitors", 0)
    tourist_ratio = (current_tourist / current_total * 100) if current_total else 0

    tourist_diff = current_tourist - st.session_state.get("summary_tourist_visitors_prev", 0)
    tourist_rate = (tourist_diff / st.session_state.get("summary_tourist_visitors_prev", 0) * 100) if st.session_state.get("summary_tourist_visitors_prev", 0) else 0

    top_day = st.session_state.get("summary_top_day_all", "")
    top_region = st.session_state.get("summary_external_top_region_name", "")
    top_region_subs = st.session_state.get("summary_external_top_region_subs", [])

        # 매출 관련
    this_rate = st.session_state.get("summary_sales_change_this", 0.0)
    top_sales_day = st.session_state.get("summary_sales_top_day", "")

    # 소비층
    top_age_ratio1 = st.session_state.get("summary_top_age_ratio1", "")
    top_age_ratio2 = st.session_state.get("summary_top_age_ratio2", "")

    # 소비 분포
    tourist_sales_ratio = st.session_state.get("summary_tourist_sales_ratio", 0.0)
    price_gap = st.session_state.get("summary_price_gap_tourist_local", 0.0)
    top_eup = st.session_state.get("top_eupmyeondong_name", "")
    other_eup_list = st.session_state.get("summary_sales_top_eups", [])

    if gpt_generate:
        prompt = f"""
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨') 
▸ 다음 정보를 바탕으로 행정문서체 형식으로 종합의견을 작성해줘. 각 문장은 '❍' 또는 '-' 로 시작하고, 3개 단락 이상으로 구성할 것.
- {year}년 {festival_name}은 전년도 대비 {total_rate:.2f}% 증가한 {current_total:,}명의 방문객을 기록함
- 외지인 방문객은 전체의 {tourist_ratio:.2f}%({current_tourist:,}명)이며, 전년도 대비 {tourist_rate:.2f}% 증가
- 일자별로는 {top_day} 방문이 가장 많았고, {top_region} 등 주요 도시에서 유입
- 매출은 직전 주 대비 {this_rate:.2f}% 증가하였으며, {top_sales_day}에 집중됨
- 주요 소비층은 {top_age_ratio1}, {top_age_ratio2} 등 중장년층이 다수
- 외지인 소비는 전체 소비의 약 {tourist_sales_ratio:.2f}% 차지하며, 현지인보다 1인당 소비단가가 약 {price_gap:.1f}배 높음
- 주요 소비지역은 {top_eup}, 기타 {', '.join(other_eup_list)} 지역 등으로 확산됨
- 전반적으로 축제 개최의 긍정적인 요소에 대해서 부각할것
- 마지막 문장은 축제 성과에 대한 긍정적 평가로 마무리할 것 (예: 지역경제 파급효과, 체류형 관광 기여 등)
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 데이터를 바탕으로 행정문서 스타일의 종합의견을 작성하는 공무원 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )

        st.markdown("#### 🧠 GPT 종합의견")
        st.write(response.choices[0].message.content)



# In[ ]:




