#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI

# ✅ OpenAI API 키 설정 (Streamlit Secrets에 저장된 값 사용)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ✅ 시사점 생성 함수 (ChatGPT API 호출)
def generate_insights(local_2024, tourist_2024, local_2025, tourist_2025):
    total_2024 = local_2024 + tourist_2024
    total_2025 = local_2025 + tourist_2025

    local_diff = local_2025 - local_2024
    tourist_diff = tourist_2025 - tourist_2024
    total_diff = total_2025 - total_2024

    prompt = f"""
    다음은 충주시의 축제 방문객 데이터입니다. 이를 바탕으로 행정기관 보도자료 스타일의 시사점을 3~5문장으로 작성해주세요.

    - 2024년: 현지인 {local_2024:,}명, 외지인 {tourist_2024:,}명, 전체 {total_2024:,}명
    - 2025년: 현지인 {local_2025:,}명, 외지인 {tourist_2025:,}명, 전체 {total_2025:,}명
    - 전년대비: 현지인 {local_diff:+,}명, 외지인 {tourist_diff:+,}명, 전체 {total_diff:+,}명

    시사점은 수치를 해석하며, 긍정적/부정적 측면을 함께 고려하고 행정적 해석이 담기도록 해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 축제 데이터 분석에 특화된 지방행정 보고서 작성 전문가야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )

    return response.choices[0].message.content


# ✅ 1번 항목: 축제 방문객 현황 분석 함수
def analyze_summary():
    st.subheader("📌 1. 축제 기간 방문객 현황 (총괄)")

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
            "연도": "2024년 (4.12~4.14)",
            "현지인 방문객수": f"{local_2024:,}명 (일평균: {local_2024 // days_2024:,}명)",
            "외지인 방문객수": f"{tourist_2024:,}명 (일평균: {tourist_2024 // days_2024:,}명)",
            "전체 관광객 수": f"{total_2024:,}명 (일평균: {total_2024 // days_2024:,}명)",
            "비고": f"현지인 {local_2024 / total_2024:.1%}, 외지인 {tourist_2024 / total_2024:.1%}"
        }

        row_2025 = {
            "연도": "2025년 (4.11~4.13)",
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

        result_df = pd.DataFrame([row_2024, row_2025, row_diff])
        st.subheader("📊 분석 결과표")
        st.dataframe(result_df, use_container_width=True)

        # ✅ 시사점 도출
        with st.spinner("🤖 ChatGPT가 시사점을 작성 중입니다..."):
            insight = generate_insights(local_2024, tourist_2024, local_2025, tourist_2025)
            st.subheader("🧠 GPT 시사점")
            st.write(insight)


# ✅ 전체 분석기 앱 (1~6번 항목 선택 UI 포함)
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    st.markdown("아래에서 분석하고자 하는 항목을 선택하세요. 각 항목은 수치 입력 또는 엑셀 업로드를 기반으로 자동 분석되며, GPT를 통해 시사점까지 도출됩니다.")

    selected_section = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 기간 방문객 현황(총괄)",
        "2. 축제 일자별 방문객 수 (준비중)",
        "3. 시간대별 관광객 존재 현황 (준비중)",
        "4. 전·중·후 일평균 방문객 현황 (준비중)",
        "5. 연령별 현황 (준비중)",
        "6-1. 외지인 거주지 (시도별) (준비중)",
        "6-2. 외지인 거주지 (시군별) (준비중)",
        "6-3. 방문 후 이동지역 (준비중)"
    ])

    if selected_section.startswith("1."):
        analyze_summary()
    else:
        st.info("⏳ 해당 항목은 추후 개발 예정입니다.")


