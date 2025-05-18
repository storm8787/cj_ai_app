#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI

# ✅ GPT 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 시사점 예시 불러오기
def load_insight_examples(section_id):
    try:
        with open(f"data/insights/{section_id}.txt", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 축제 기본정보 입력
def festival_basic_info():
    st.subheader("📌 축제 기본정보 입력")

    festival_name = st.text_input("🎪 축제명", value="2025년 수안보온천제")
    location = st.text_input("📍 축제 장소", value="충주시 수안보면 일원")
    period = st.text_input("🗓 축제 기간", value="2025. 4. 11 ~ 4. 13")

    st.session_state["festival_name"] = festival_name
    st.session_state["festival_location"] = location
    st.session_state["festival_period"] = period

# ✅ 항목별 GPT 시사점 생성
def generate_section_summary(local_2024, tourist_2024, local_2025, tourist_2025, section_id):
    total_2024 = local_2024 + tourist_2024
    total_2025 = local_2025 + tourist_2025
    local_diff = local_2025 - local_2024
    tourist_diff = tourist_2025 - tourist_2024
    total_diff = total_2025 - total_2024

    examples = load_insight_examples(section_id)
    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "축제 기간")
    location = st.session_state.get("festival_location", "")

    prompt = f"""
다음은 {name}({period}, {location})에 대한 분석입니다.

아래는 유사 항목 시사점 예시입니다:

{examples}

다음 데이터를 기반으로 2~4문장 시사점을 작성해주세요:

- 2024년: 현지인 {local_2024:,}명 / 외지인 {tourist_2024:,}명 / 전체 {total_2024:,}명
- 2025년: 현지인 {local_2025:,}명 / 외지인 {tourist_2025:,}명 / 전체 {total_2025:,}명
- 전년대비: 현지인 {local_diff:+,}명 / 외지인 {tourist_diff:+,}명 / 전체 {total_diff:+,}명
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=600
    )
    return response.choices[0].message.content

# ✅ 분석요약 or 종합의견 생성
def generate_final_text(purpose):
    examples = load_insight_examples(purpose)
    combined = "\n".join(st.session_state.get("summary_parts", []))
    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "축제 기간")
    location = st.session_state.get("festival_location", "")

    prompt = f"""
다음은 {name}({period}, {location})에 대한 전체 분석 내용을 바탕으로 {purpose.replace('_', ' ')}을 작성해주세요.

[예시]
{examples}

[분석요약]
{combined}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 지방행정 보고서를 작성하는 전문가야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1500
    )
    return response.choices[0].message.content

# ✅ 1번 분석기
def analyze_summary():
    st.subheader("📊 1. 축제 방문객 현황 분석")

    col1, col2 = st.columns(2)
    with col1:
        local_2024 = st.number_input("2024년 현지인 방문객 수", min_value=0, step=100)
        tourist_2024 = st.number_input("2024년 외지인 방문객 수", min_value=0, step=100)
        days_2024 = st.number_input("2024년 축제일 수", min_value=1, value=3)

    with col2:
        local_2025 = st.number_input("2025년 현지인 방문객 수", min_value=0, step=100)
        tourist_2025 = st.number_input("2025년 외지인 방문객 수", min_value=0, step=100)
        days_2025 = st.number_input("2025년 축제일 수", min_value=1, value=3)

    if st.button("🚀 분석 실행"):
        total_2024 = local_2024 + tourist_2024
        total_2025 = local_2025 + tourist_2025

        row_2024 = {
            "연도": "2024년",
            "현지인 방문객수": f"{local_2024:,}명 (일평균: {local_2024 // days_2024:,}명)",
            "외지인 방문객수": f"{tourist_2024:,}명 (일평균: {tourist_2024 // days_2024:,}명)",
            "전체 관광객 수": f"{total_2024:,}명 (일평균: {total_2024 // days_2024:,}명)",
            "비고": f"현지인 {local_2024 / total_2024:.1%}, 외지인 {tourist_2024 / total_2024:.1%}"
        }

        row_2025 = {
            "연도": "2025년",
            "현지인 방문객수": f"{local_2025:,}명 (일평균: {local_2025 // days_2025:,}명)",
            "외지인 방문객수": f"{tourist_2025:,}명 (일평균: {tourist_2025 // days_2025:,}명)",
            "전체 관광객 수": f"{total_2025:,}명 (일평균: {total_2025 // days_2025:,}명)",
            "비고": f"현지인 {local_2025 / total_2025:.1%}, 외지인 {tourist_2025 / total_2025:.1%}"
        }

        row_diff = {
            "연도": "전년대비 증감",
            "현지인 방문객수": f"{local_2025 - local_2024:+,}명 ({(local_2025 - local_2024) / local_2024:.1%})",
            "외지인 방문객수": f"{tourist_2025 - tourist_2024:+,}명 ({(tourist_2025 - tourist_2024) / tourist_2024:.1%})",
            "전체 관광객 수": f"{total_2025 - total_2024:+,}명 ({(total_2025 - total_2024) / total_2024:.1%})",
            "비고": ""
        }

        st.dataframe(pd.DataFrame([row_2024, row_2025, row_diff]), use_container_width=True)

        with st.spinner("🤖 GPT 시사점 생성 중..."):
            summary = generate_section_summary(local_2024, tourist_2024, local_2025, tourist_2025, "1_summary")
            st.subheader("🧠 GPT 시사점")
            st.write(summary)

            # 누적 저장
            if "summary_parts" not in st.session_state:
                st.session_state.summary_parts = []
            st.session_state.summary_parts.append(summary)

# ✅ 전체 분석기
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    # 기본정보 입력 먼저
    festival_basic_info()

    selected = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 기간 방문객 현황(총괄)",
        "📘 분석결과(요약) 작성",
        "📙 종합의견 작성"
    ])

    if selected.startswith("1."):
        analyze_summary()

    elif selected == "📘 분석결과(요약) 작성":
        if st.button("📌 분석결과 요약 생성"):
            text = generate_final_text("summary_overview")
            st.write(text)

    elif selected == "📙 종합의견 작성":
        if st.button("📌 종합의견 생성"):
            text = generate_final_text("final_opinion")
            st.write(text)

