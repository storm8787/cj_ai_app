#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_insight_examples(section_id):
    try:
        path = f"press_release_app/data/insights/{section_id}.txt"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

from festival.analyze_summary_overview import analyze_summary_overview
from festival.analyze_final_opinion import analyze_final_opinion

def analyze_summary_and_opinion():
    st.subheader("📊 8. 분석결과 요약 및 종합의견")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 분석결과(요약) 보기"):
            analyze_summary_overview()

    with col2:
        if st.button("💡 종합의견(GPT 생성) 보기"):
            analyze_final_opinion()

def analyze_summary_overview():
    st.subheader("🧾 8-1. 분석결과 요약")

    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "")
    location = st.session_state.get("festival_location", "")
    summary_lines = []

    # 세션에서 요약 내용 가져오기 (1~7번 분석기 데이터 기반)
    if "summary_total_text" in st.session_state:
        summary_lines.append("📌 [1. 방문객 총괄]")
        summary_lines.append(st.session_state["summary_total_text"])
    if "summary_daily_table" in st.session_state:
        summary_lines.append("\n📌 [2. 일자별 방문객]")
        for _, row in st.session_state["summary_daily_table"].iterrows():
            summary_lines.append(f"- {row['날짜']}: 현지인 {row['현지인 방문객']:,} / 외지인 {row['외지인 방문객']:,} / 전체 {row['전체 방문객']:,}")
    if "summary_time_distribution" in st.session_state:
        summary_lines.append("\n📌 [3. 시간대별 관광객 분포]")
        summary_lines.append(st.session_state["summary_time_distribution"])
    if "summary_before_after" in st.session_state:
        summary_lines.append("\n📌 [4. 축제 전·중·후 방문객]")
        summary_lines.append(st.session_state["summary_before_after"])
    if "summary_age_group_text" in st.session_state:
        summary_lines.append("\n📌 [5. 연령대별 방문객]")
        summary_lines.append(st.session_state["summary_age_group_text"])
    if "summary_gender_by_age_df" in st.session_state:
        summary_lines.append("\n📌 [6. 연령별 성별 방문객]")
        df = st.session_state["summary_gender_by_age_df"]
        for _, row in df.iterrows():
            summary_lines.append(f"- {row['연령구분']}: 남자 {row['남자']}명 ({row['남자비율']}%), 여자 {row['여자']}명 ({row['여자비율']}%)")
    if "summary_visitor_by_province_sido" in st.session_state:
        summary_lines.append("\n📌 [7-1. 시도별 외지인 방문객]")
        df = st.session_state["summary_visitor_by_province_sido"]
        for _, row in df.iterrows():
            if row["시도_2"] not in ["", "합계", None]:
                summary_lines.append(f"- {row['시도_2']}: {row['관광객수_2']}명 ({row['비율_2']})")
    if "summary_visitor_by_province_gungu" in st.session_state:
        summary_lines.append("\n📌 [7-2. 시군구별 외지인 방문객]")
        df = st.session_state["summary_visitor_by_province_gungu"]
        for _, row in df.iterrows():
            if row["full_region_2"] not in ["", "합계", "기타", None]:
                summary_lines.append(f"- {row['full_region_2']}: {row['관광객수_2']}명 ({row['비율_2']})")
    if "summary_visitor_after_24h_grouped" in st.session_state:
        summary_lines.append("\n📌 [7-3. 외지인 24시간 이후 지역]")
        df = st.session_state["summary_visitor_after_24h_grouped"]
        for _, row in df.iterrows():
            summary_lines.append(f"- {row['full_region']}: {row['관광객수']:,}명 ({row['비율']:.2f}%)")

    # GPT 요약 생성
    if st.button("🧠 분석결과 요약 생성"):
        reference = load_insight_examples("summary_overview")
        prompt = f"""다음은 {name}({period}, {location}) 축제의 데이터 기반 분석결과입니다.

{chr(10).join(summary_lines)}

[참고자료]
{reference}

위 내용을 바탕으로 방문객 수, 성격, 체류, 소비 등 주요 지표 중심으로 분석결과를 공공보고서 스타일로 5~7문장으로 작성해주세요.
"""
        with st.spinner("GPT가 분석결과 요약 중..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 축제 데이터를 정리하는 지방행정 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=900
            )
            st.subheader("🧾 GPT 분석결과 요약")
            st.write(response.choices[0].message.content)

def analyze_final_opinion():
    st.subheader("💬 8-2. 종합의견 (정책적 시사점)")

    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "")
    location = st.session_state.get("festival_location", "")
    
    # GPT 종합의견 생성
    if st.button("🧠 종합의견 생성"):
        summary_lines = st.session_state.get("final_summary_text", "")
        reference = load_insight_examples("final_opinion")

        prompt = f"""다음은 {name}({period}, {location}) 축제의 요약 분석 결과입니다.

{summary_lines}

[참고자료]
{reference}

위 내용을 바탕으로 정책적 시사점 중심의 종합적인 의견을 5~7문장으로 작성해주세요.
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

