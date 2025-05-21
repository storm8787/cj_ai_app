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
    #st.subheader("📊 8. 분석결과 요약 및 종합의견")

    col1, col2 = st.columns(2)
    with col1:
        gpt_summary = st.button("📝 분석결과(요약) 생성 및 보기")
    with col2:
        gpt_opinion = st.button("💡 종합의견(GPT 생성) 보기")

    analyze_summary_overview(gpt_generate=gpt_summary)
    analyze_final_opinion(gpt_generate=gpt_opinion)

# ✅ 분석결과 요약 생성
def analyze_summary_overview(gpt_generate=False):
    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "")
    location = st.session_state.get("festival_location", "")
    summary_lines = []

    # ✅ 1. 방문객 총괄
    if all(key in st.session_state for key in ["summary_total_visitors", "summary_local_visitors", "summary_tourist_visitors"]):
        total = st.session_state["summary_total_visitors"]
        local = st.session_state["summary_local_visitors"]
        tourist = st.session_state["summary_tourist_visitors"]
        summary_lines.append(f"❍ 총 관광객 수는 {total:,}명이며, 이 중 현지인은 {local:,}명({local/total:.1%}), 외지인은 {tourist:,}명({tourist/total:.1%})임")

    # ✅ 2. 시간대별 분포
    if "summary_time_distribution_df" in st.session_state:
        df = st.session_state["summary_time_distribution_df"]
        summary_lines.append("❍ 시간대별 분포는 21~24시 구간에 가장 집중되어 있음")

    # ✅ 3. 전·중·후 분석
    if "summary_before_after_df" in st.session_state:
        df = st.session_state["summary_before_after_df"]
        try:
            before = df.iloc[2, 1]  # 합계, 축제 전
            during = df.iloc[2, 2]  # 합계, 축제 기간
            summary_lines.append(f"❍ 축제기간 총 방문객 수는 {during}명으로, 축제 전(5일) 대비 뚜렷한 증가 추세")
        except:
            pass

    # ✅ 4. 연령대별 요약
    if "summary_age_group_df" in st.session_state:
        summary_lines.append("❍ 연령대별로는 20대의 참여율이 가장 높아 젊은 층 중심의 축제로 평가됨")

    # ✅ 5. 외지인 체류 분석
    if "summary_visitor_after_24h_grouped" in st.session_state:
        df = st.session_state["summary_visitor_after_24h_grouped"]
        chungju_row = df[df["full_region"].str.contains("충주시")]
        if not chungju_row.empty:
            stay_count = int(chungju_row.iloc[0]["관광객수"])
            stay_rate = float(chungju_row.iloc[0]["비율"])
            summary_lines.append(f"❍ 외지인 중 {stay_rate:.2f}%({stay_count:,}명)는 충주에 24시간 이상 체류하며 관광 활동을 이어간 것으로 분석됨")

    # ✅ 요약 출력
    st.markdown("### 🧾 분석결과 요약")
    st.text("\n".join(summary_lines))

    # ✅ GPT 요약 생성
    if gpt_generate:
        reference = load_insight_examples("summary_overview")
        prompt = f"""
📌 본 분석은 KT 관광인구 / 국민카드 매출 데이터를 기초로 시장점유율에 따른 보정계수를 적용·산출한 {name}({period}, {location}) 축제의 방문객과 매출현황을 분석한 결과임

[요약 데이터]\n{chr(10).join(summary_lines)}

▸ 각 문장은 ❍ 기호로 시작하고, 문장이 단절되지 않도록 자연스럽게 연결할 것  
▸ 총 관광객 수, 증가율, 시간대, 연령대, 외지인 체류, 소비 흐름 등을 종합 반영하여 6문장 이내로 구성할 것  
▸ 행정 보고서 스타일로 작성할 것  
[유사 시사점 예시]\n{reference}
"""

        with st.spinner("GPT가 분석결과 요약 중..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            st.subheader("🧾 GPT 분석결과 요약")
            st.write(response.choices[0].message.content)

        # ✅ 종합의견용으로 저장
        st.session_state["final_summary_text"] = "\n".join(summary_lines)

# ✅ 종합의견
def analyze_final_opinion(gpt_generate=False):
    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "")
    location = st.session_state.get("festival_location", "")

    # ✅ summary가 없으면 경고
    if gpt_generate and "final_summary_text" not in st.session_state:
        st.warning("⚠️ 먼저 '분석결과 요약 생성' 버튼을 눌러주세요.")
        return

    if gpt_generate:
        summary_lines = st.session_state["final_summary_text"]
        reference = load_insight_examples("final_opinion")

        prompt = f"""다음은 {name}({period}, {location}) 축제의 분석 요약입니다.

{summary_lines}

[참고자료]
{reference}

위 내용을 바탕으로 정책적 시사점 중심의 종합 의견을 5~7문장으로 작성해주세요.
❍ 방문객 특성과 동향 분석  
❍ 지역 경제/소비/체류 기여도 해석  
❍ 관광 전략/운영 프로그램 개선 방향 제시 포함
"""

        with st.spinner("GPT가 종합의견을 작성 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 충주시 축제 데이터를 분석하고 정책 제안까지 도출하는 지방행정 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            st.subheader("💡 GPT 종합의견")
            st.write(response.choices[0].message.content)

