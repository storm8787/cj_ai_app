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
    st.subheader("📊 8. 분석결과 요약 및 종합의견")

    col1, col2 = st.columns(2)
    with col1:
        gpt_summary = st.button("📝 분석결과(요약) 생성 및 보기")
    with col2:
        gpt_opinion = st.button("💡 종합의견(GPT 생성) 보기")

    analyze_summary_overview(gpt_generate=gpt_summary)
    analyze_final_opinion(gpt_generate=gpt_opinion)

# ✅ 분석결과 요약
def analyze_summary_overview(gpt_generate=False):
    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "")
    location = st.session_state.get("festival_location", "")
    summary_lines = []

    if "summary_total_text" in st.session_state:
        summary_lines.append("📌 [1. 방문객 총괄]")
        summary_lines.append(st.session_state["summary_total_text"])

    if "summary_daily_table" in st.session_state:
        summary_lines.append("\n📌 [2. 일자별 방문객]")
        df = st.session_state["summary_daily_table"]
        for _, row in df.iterrows():
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

    # ✅ (요약용) 시도별 외지인 방문객 – 상위 5개만
    if "summary_visitor_by_province_sido" in st.session_state:
        summary_lines.append("\n📌 [7-1. 시도별 외지인 방문객 상위 5]")
        df = st.session_state["summary_visitor_by_province_sido"]
        df = df[df["시도_2"].notnull() & (df["시도_2"] != "합계")].head(5)
        for _, row in df.iterrows():
            summary_lines.append(f"- {row['시도_2']}: {row['관광객수_2']}명 ({row['비율_2']})")

    # ✅ (요약용) 시군구별 외지인 방문객 – 상위 5개만
    if "summary_visitor_by_province_gungu" in st.session_state:
        summary_lines.append("\n📌 [7-2. 시군구별 외지인 방문객 상위 5]")
        df = st.session_state["summary_visitor_by_province_gungu"]
        df = df[df["full_region_2"].notnull() & (df["full_region_2"] != "합계")].head(5)
        for _, row in df.iterrows():
            summary_lines.append(f"- {row['full_region_2']}: {row['관광객수_2']}명 ({row['비율_2']})")

    # ✅ (요약용) 24시간 이후 지역 – 상위 5개만
    if "summary_visitor_after_24h_grouped" in st.session_state:
        summary_lines.append("\n📌 [7-3. 외지인 24시간 이후 지역 상위 5]")
        df = st.session_state["summary_visitor_after_24h_grouped"]
        df = df.sort_values(by="관광객수", ascending=False).head(5)
        for _, row in df.iterrows():
            summary_lines.append(f"- {row['full_region']}: {row['관광객수']:,}명 ({row['비율']:.2f}%)")

    # ✅ 요약 출력
    st.markdown("### 🧾 분석결과 요약")
    st.text("\n".join(summary_lines))

    # ✅ GPT 요약 생성
    if gpt_generate:
        reference = load_insight_examples("summary_overview")

        prompt = f"""📌 본 분석은 KT 관광인구 / 국민카드 매출 데이터를 기초로 시장점유율에 따른 보정계수를 적용·산출한 {name}({period}, {location}) 축제의 방문객과 매출현황을 분석한 결과임

분석 개요:
{chr(10).join(summary_lines)}

[참고자료]
{reference}

아래 형식에 맞춰 5~7문장으로 행정 보고서 스타일의 분석결과를 작성하세요.

❍ 총 관광객 수, 전년 대비 증감  
  - 현지인과 외지인 각각 수치 및 증감 포함  
❍ 일평균 관광객 증감 / 일반 시기 대비 변화율 포함  
❍ 연령대, 요일, 시간대별 특징  
❍ 체류형 관광객의 비율 및 연계관광 시사점  
❍ 전반적 평가: 방문객 흐름, 프로그램 특성, 기후 등 종합적 해석

이 형식을 엄격히 따르세요.
"""

        with st.spinner("GPT가 분석결과 요약 중..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=900
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

