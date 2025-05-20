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

def analyze_summary_and_opinion():
    st.subheader("📊 8. 분석결과 요약 및 종합의견")

    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "")
    location = st.session_state.get("festival_location", "")
    summary_lines = []

    # ✅ [분석결과 요약] 세션 기반으로 각 항목 출력
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
            if row["시도_2"] not in [None, "", "합계"]:
                summary_lines.append(f"- {row['시도_2']}: {row['관광객수_2']}명 ({row['비율_2']})")

    if "summary_visitor_by_province_gungu" in st.session_state:
        summary_lines.append("\n📌 [7-2. 시군구별 외지인 방문객]")
        df = st.session_state["summary_visitor_by_province_gungu"]
        for _, row in df.iterrows():
            if row["full_region_2"] not in [None, "", "합계", "기타"]:
                summary_lines.append(f"- {row['full_region_2']}: {row['관광객수_2']}명 ({row['비율_2']})")

    if "summary_visitor_after_24h_grouped" in st.session_state:
        summary_lines.append("\n📌 [7-3. 외지인 24시간 이후 지역]")
        df = st.session_state["summary_visitor_after_24h_grouped"]
        for _, row in df.iterrows():
            summary_lines.append(f"- {row['full_region']}: {row['관광객수']:,}명 ({row['비율']:.2f}%)")

    # ✅ 분석결과(요약) 출력
    st.markdown("### 🧾 분석결과 요약")
    summary_text = "\n".join(summary_lines)
    st.text(summary_text)

    # ✅ 종합의견 GPT 생성
    st.markdown("---")
    st.markdown("### 💬 종합의견 (GPT 자동작성)")

    if st.button("🚀 종합의견 생성하기"):
        reference = load_insight_examples("final_opinion")
        prompt = f"""다음은 {name}({period}, {location}) 축제에 대한 주요 분석 요약입니다.

{summary_text}

[참고자료]
{reference}

위 요약내용을 기반으로, 축제 방문객의 분포와 주요 특징을 통합적으로 설명하고,
정책적 시사점을 포함한 종합의견을 5~7문장으로 작성해주세요.
"""

        with st.spinner("🤖 GPT가 종합의견을 작성 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 충주시 축제 데이터를 분석하고 정책 시사점을 도출하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            st.markdown("#### 🧠 종합의견")
            st.write(response.choices[0].message.content)

