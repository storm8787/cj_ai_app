#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from datetime import date
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

    festival_name = st.text_input("🎪 축제명", value="수안보온천제")
    location = st.text_input("📍 축제 장소", value="충주시 수안보면 일원")

    start_date = st.date_input("🗓 축제 시작일", value=date(2025, 4, 11))
    end_date = st.date_input("🏁 축제 종료일", value=date(2025, 4, 13))

    period = f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"
    days = (end_date - start_date).days + 1

    st.session_state["festival_name"] = festival_name
    st.session_state["festival_location"] = location
    st.session_state["festival_period"] = period
    st.session_state["festival_days"] = days

# ✅ 항목별 GPT 시사점 생성
def generate_section_summary(local_prev, tourist_prev, local_curr, tourist_curr, section_id):
    total_prev = local_prev + tourist_prev
    total_curr = local_curr + tourist_curr
    local_diff = local_curr - local_prev
    tourist_diff = tourist_curr - tourist_prev
    total_diff = total_curr - total_prev

    examples = load_insight_examples(section_id)
    name = st.session_state.get("festival_name", "본 축제")
    period = st.session_state.get("festival_period", "축제 기간")
    location = st.session_state.get("festival_location", "")

    prompt = f"""
다음은 {name}({period}, {location})에 대한 분석입니다.

아래는 유사 항목 시사점 예시입니다:

{examples}

다음 데이터를 기반으로 2~4문장 시사점을 작성해주세요:

- 전년도: 현지인 {local_prev:,}명 / 외지인 {tourist_prev:,}명 / 전체 {total_prev:,}명
- 올해: 현지인 {local_curr:,}명 / 외지인 {tourist_curr:,}명 / 전체 {total_curr:,}명
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
        local_prev = st.number_input("전년도 현지인 방문객 수", min_value=0, step=100)
        tourist_prev = st.number_input("전년도 외지인 방문객 수", min_value=0, step=100)
    with col2:
        local_curr = st.number_input("올해 현지인 방문객 수", min_value=0, step=100)
        tourist_curr = st.number_input("올해 외지인 방문객 수", min_value=0, step=100)

    if st.button("🚀 분석 실행"):
        days = st.session_state.get("festival_days", 3)
        total_prev = local_prev + tourist_prev
        total_curr = local_curr + tourist_curr

        row_prev = {
            "연도": "전년도 축제",
            "현지인 방문객수": f"{local_prev:,}명 (일평균: {local_prev // days:,}명)",
            "외지인 방문객수": f"{tourist_prev:,}명 (일평균: {tourist_prev // days:,}명)",
            "전체 관광객 수": f"{total_prev:,}명 (일평균: {total_prev // days:,}명)",
            "비고": f"현지인 {local_prev / total_prev:.1%}, 외지인 {tourist_prev / total_prev:.1%}"
        }

        row_curr = {
            "연도": "올해 축제",
            "현지인 방문객수": f"{local_curr:,}명 (일평균: {local_curr // days:,}명)",
            "외지인 방문객수": f"{tourist_curr:,}명 (일평균: {tourist_curr // days:,}명)",
            "전체 관광객 수": f"{total_curr:,}명 (일평균: {total_curr // days:,}명)",
            "비고": f"현지인 {local_curr / total_curr:.1%}, 외지인 {tourist_curr / total_curr:.1%}"
        }

        row_diff = {
            "연도": "전년대비 증감",
            "현지인 방문객수": f"{local_curr - local_prev:+,}명 ({(local_curr - local_prev) / local_prev:.1%})",
            "외지인 방문객수": f"{tourist_curr - tourist_prev:+,}명 ({(tourist_curr - tourist_prev) / tourist_prev:.1%})",
            "전체 관광객 수": f"{total_curr - total_prev:+,}명 ({(total_curr - total_prev) / total_prev:.1%})",
            "비고": ""
        }

        st.dataframe(pd.DataFrame([row_prev, row_curr, row_diff]), use_container_width=True)

        with st.spinner("🤖 GPT 시사점 생성 중..."):
            summary = generate_section_summary(local_prev, tourist_prev, local_curr, tourist_curr, "1_summary")
            st.subheader("🧠 GPT 시사점")
            st.write(summary)

            if "summary_parts" not in st.session_state:
                st.session_state.summary_parts = []
            st.session_state.summary_parts.append(summary)

# ✅ 전체 분석기
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    # 축제 기본정보 먼저 입력
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

