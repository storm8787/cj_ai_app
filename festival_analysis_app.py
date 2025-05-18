#!/usr/bin/env python
# coding: utf-8

# In[3]:


import streamlit as st
import pandas as pd
from datetime import date, timedelta
from openai import OpenAI

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
            prompt = f"""
다음은 {st.session_state.get('festival_name', '본 축제')}({st.session_state.get('festival_period', '')}, {st.session_state.get('festival_location', '')})에 대한 분석입니다.

- 전년도: 현지인 {local_prev:,}명 / 외지인 {tourist_prev:,}명 / 전체 {total_prev:,}명
- 올해: 현지인 {local_curr:,}명 / 외지인 {tourist_curr:,}명 / 전체 {total_curr:,}명
- 전년대비: 현지인 {local_curr - local_prev:+,}명 / 외지인 {tourist_curr - tourist_prev:+,}명 / 전체 {total_curr - total_prev:+,}명

시사점을 3~5문장으로 간결하게 작성해주세요.
"""
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )
            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

# ✅ 2번 분석기
def analyze_daily_visitors():
    st.subheader("📊 2. 축제 일자별 방문객 수 분석")
    st.markdown("현지인과 외지인의 일자별 방문객 수를 입력하세요.")

    start_date = st.session_state.get("festival_start_date")
    end_date = st.session_state.get("festival_end_date")

    if not start_date or not end_date:
        st.error("❌ 먼저 축제 기본정보(시작일~종료일)를 입력해주세요.")
        return

    days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    day_labels = [day.strftime("%Y.%m.%d") for day in days]

    local = {}
    tourist = {}

    for day_label in day_labels:
        col1, col2 = st.columns(2)
        with col1:
            local[day_label] = st.number_input(f"{day_label} 현지인", min_value=0, step=100, key=f"local_{day_label}")
        with col2:
            tourist[day_label] = st.number_input(f"{day_label} 외지인", min_value=0, step=100, key=f"tourist_{day_label}")

    if st.button("🚀 일자별 분석 실행"):
        data = {
            "구분": ["현지인", "외지인", "전체"],
        }
        total_by_day = {}

        for day_label in day_labels:
            total = local[day_label] + tourist[day_label]
            total_by_day[day_label] = total
            data[day_label] = [local[day_label], tourist[day_label], total]

        total_local = sum(local.values())
        total_tourist = sum(tourist.values())
        total_all = total_local + total_tourist
        data["합계"] = [total_local, total_tourist, total_all]
        data["전체 대비 비율"] = [f"{total_local/total_all:.2%}", f"{total_tourist/total_all:.2%}", "100.00%"]

        df = pd.DataFrame(data).set_index("구분")
        st.dataframe(df, use_container_width=True)

        st.markdown("\n### 📅 날짜별 전체 방문객 구성비")
        date_table = {
            "날짜": day_labels,
            "전체 방문객 수": [total_by_day[day] for day in day_labels],
            "전체 대비 구성비": [f"{(total_by_day[day]/total_all):.2%}" for day in day_labels]
        }
        st.dataframe(pd.DataFrame(date_table), use_container_width=True)

        with st.spinner("🤖 GPT 시사점 생성 중..."):
            prompt_lines = [f"- {day}: 현지인 {local[day]:,}명, 외지인 {tourist[day]:,}명" for day in day_labels]
            prompt = f"""
다음은 축제 기간 중 일자별 현지인 및 외지인 방문객 수입니다.

{chr(10).join(prompt_lines)}

총 방문객 수는 {total_all:,}명이며, 일자별 구성비와 방문객 특성을 고려해 시사점을 3~5문장으로 행정문서 스타일로 작성해주세요.
"""
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )
            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

# ✅ 전체 분석기 실행 함수
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    # 축제 기본정보 먼저 입력
    festival_basic_info()

    selected = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 방문객 현황 분석",
        "2. 축제 일자별 방문객 수 분석"
    ])

    if selected.startswith("1"):
        analyze_summary()
    elif selected.startswith("2"):
        analyze_daily_visitors()

