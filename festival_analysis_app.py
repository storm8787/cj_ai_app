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

    if st.button("🚀 분석 실행", key="total_btn"):
        days = st.session_state.get("festival_days", 3)
        total_prev = local_prev + tourist_prev
        total_curr = local_curr + tourist_curr

        rows = []

        if total_prev > 0:
            row_prev = {
                "연도": "전년도 축제",
                "현지인 방문객수": f"{local_prev:,}명 (일평균: {local_prev // days:,}명)",
                "외지인 방문객수": f"{tourist_prev:,}명 (일평균: {tourist_prev // days:,}명)",
                "전체 관광객 수": f"{total_prev:,}명 (일평균: {total_prev // days:,}명)",
                "비고": f"현지인 {local_prev / total_prev:.1%}, 외지인 {tourist_prev / total_prev:.1%}"
            }
            rows.append(row_prev)

        row_curr = {
            "연도": "올해 축제",
            "현지인 방문객수": f"{local_curr:,}명 (일평균: {local_curr // days:,}명)",
            "외지인 방문객수": f"{tourist_curr:,}명 (일평균: {tourist_curr // days:,}명)",
            "전체 관광객 수": f"{total_curr:,}명 (일평균: {total_curr // days:,}명)",
            "비고": f"현지인 {local_curr / total_curr:.1%}, 외지인 {tourist_curr / total_curr:.1%}"
        }
        rows.append(row_curr)

        if total_prev > 0:
            row_diff = {
                "연도": "전년대비 증감",
                "현지인 방문객수": f"{local_curr - local_prev:+,}명 ({(local_curr - local_prev) / local_prev:.1%})",
                "외지인 방문객수": f"{tourist_curr - tourist_prev:+,}명 ({(tourist_curr - tourist_prev) / tourist_prev:.1%})",
                "전체 관광객 수": f"{total_curr - total_prev:+,}명 ({(total_curr - total_prev) / total_prev:.1%})",
                "비고": ""
            }
            rows.append(row_diff)

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        with st.spinner("🤖 GPT 시사점 생성 중..."):
            prompt = f"""
다음은 {st.session_state.get('festival_name', '본 축제')}({st.session_state.get('festival_period', '')}, {st.session_state.get('festival_location', '')})에 대한 분석입니다.

"""
            if total_prev > 0:
                prompt += (
                    f"- 전년도: 현지인 {local_prev:,}명 / 외지인 {tourist_prev:,}명 / 전체 {total_prev:,}명\n"
                    f"- 올해: 현지인 {local_curr:,}명 / 외지인 {tourist_curr:,}명 / 전체 {total_curr:,}명\n"
                    f"- 전년대비: 현지인 {local_curr - local_prev:+,}명 / 외지인 {tourist_curr - tourist_prev:+,}명 / 전체 {total_curr - total_prev:+,}명\n"
                )
            else:
                prompt += (
                    f"- 올해: 현지인 {local_curr:,}명 / 외지인 {tourist_curr:,}명 / 전체 {total_curr:,}명\n"
                )

            prompt += "\n시사점을 3~5문장으로 간결하게 작성해주세요."

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

# ✅ 2번 분석기: 축제 일자별 방문객 수 분석 (전년도 + 올해 + 결과 테이블 포함)
def analyze_daily_visitors():
    st.subheader("📊 2. 축제 일자별 방문객 수 분석")
    st.markdown("전년도 및 올해 현지인/외지인의 일자별 방문객 수를 입력하세요.")

    start_date = st.session_state.get("festival_start_date")
    end_date = st.session_state.get("festival_end_date")

    if not start_date or not end_date:
        st.error("❌ 먼저 축제 기본정보(시작일~종료일)를 입력해주세요.")
        return

    days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    day_labels = [day.strftime("%Y.%m.%d") for day in days]

    prev_local = {}
    prev_tourist = {}
    curr_local = {}
    curr_tourist = {}

    for i, day in enumerate(days):
        st.markdown(f"### 📅 {i+1}일차 ({day_labels[i]})")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            prev_local[day] = st.number_input("전년도 현지인", key=f"prev_local_{i}", min_value=0)
        with col2:
            prev_tourist[day] = st.number_input("전년도 외지인", key=f"prev_tourist_{i}", min_value=0)
        with col3:
            curr_local[day] = st.number_input("올해 현지인", key=f"curr_local_{i}", min_value=0)
        with col4:
            curr_tourist[day] = st.number_input("올해 외지인", key=f"curr_tourist_{i}", min_value=0)

    if st.button("🚀 일자별 분석 실행", key="daily_btn"):
        summary_lines = []
        total_prev = 0
        total_curr = 0

        total_by_day = []
        curr_local_row = []
        curr_tourist_row = []
        curr_total_row = []

        for i, day in enumerate(days):
            pl = prev_local[day]
            pt = prev_tourist[day]
            cl = curr_local[day]
            ct = curr_tourist[day]
            t_prev = pl + pt
            t_curr = cl + ct
            total_prev += t_prev
            total_curr += t_curr

            summary_line = f"{i+1}일차 - 올해: 현지인 {cl:,}명 / 외지인 {ct:,}명 / 전체 {t_curr:,}명"
            if t_prev > 0:
                summary_line = f"{i+1}일차 - 전년도: 현지인 {pl:,}명 / 외지인 {pt:,}명 / 전체 {t_prev:,}명 | {summary_line}"
            summary_lines.append(summary_line)

            total_by_day.append(t_curr)
            curr_local_row.append(cl)
            curr_tourist_row.append(ct)
            curr_total_row.append(t_curr)

        # ✅ 1. 날짜별 전체 방문객수 + 전체 대비 구성비
        st.markdown("### 📅 날짜별 전체 방문객 구성비")
        percent_by_day = [f"{(v/total_curr):.2%}" for v in total_by_day]
        df_day = pd.DataFrame({
            "날짜": day_labels,
            "전체 방문객 수": total_by_day,
            "전체 대비 구성비": percent_by_day
        })
        st.dataframe(df_day, use_container_width=True)

        # ✅ 2. 현지인/외지인 일자별 구성 + 전체 합계 + 비율
        st.markdown("### 👥 구분별 일자별 방문객 수 및 비율")
        total_local = sum(curr_local_row)
        total_tourist = sum(curr_tourist_row)
        total_all = total_local + total_tourist
        local_ratio = f"{total_local / total_all:.2%}"
        tourist_ratio = f"{total_tourist / total_all:.2%}"

        df_type = pd.DataFrame({
            "구분": ["현지인", "외지인", "전체"],
            **{label: [curr_local_row[i], curr_tourist_row[i], curr_total_row[i]] for i, label in enumerate(day_labels)},
            "합계": [total_local, total_tourist, total_all],
            "전체 대비 비율": [local_ratio, tourist_ratio, "100.00%"]
        }).set_index("구분")
        st.dataframe(df_type, use_container_width=True)

        # ✅ 3. GPT 시사점
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            examples = load_insight_examples("2_daily")
            prompt = f"""
[유사 시사점 예시]
{examples}

[일자별 방문객 비교]
{chr(10).join(summary_lines)}

일자별 현황과 변화 양상을 반영해 3~5문장으로 시사점을 작성해주세요.
"""
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=700
            )
            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)


# ✅ 전체 분석기 실행 함수
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    festival_basic_info()

    selected = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 방문객 현황 분석",
        "2. 축제 일자별 방문객 수 분석"
    ])

    if selected.startswith("1"):
        analyze_summary()
    elif selected.startswith("2"):
        analyze_daily_visitors()

