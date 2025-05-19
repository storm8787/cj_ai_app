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

# ✅ 2번 분석기: 축제 일자별 방문객 수 분석 (전년도 + 올해 데이터, 표 + GPT 시사점)
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

    prev_local, prev_tourist = {}, {}
    curr_local, curr_tourist = {}, {}

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

        # 데이터 저장용
        data_rows = []

        # 합계용
        total_prev_local = total_prev_tourist = 0
        total_curr_local = total_curr_tourist = 0

        for i, day in enumerate(days):
            label = day.strftime("%Y.%m.%d")

            # 값 추출
            pl = prev_local[day]
            pt = prev_tourist[day]
            cl = curr_local[day]
            ct = curr_tourist[day]

            # 합계 계산
            pl_sum = pl + pt
            cl_sum = cl + ct

            total_prev_local += pl
            total_prev_tourist += pt
            total_curr_local += cl
            total_curr_tourist += ct

            summary = f"{i+1}일차 - 올해: 현지인 {cl:,}명 / 외지인 {ct:,}명 / 전체 {cl_sum:,}명"
            if pl_sum > 0:
                summary = f"{i+1}일차 - 전년도: 현지인 {pl:,}명 / 외지인 {pt:,}명 / 전체 {pl_sum:,}명 | {summary}"
            summary_lines.append(summary)

            # 표용 데이터 정리
            data_rows.append({
                "구분": "전년도 현지인", label: pl
            })
            data_rows.append({
                "구분": "전년도 외지인", label: pt
            })
            data_rows.append({
                "구분": "전년도 전체", label: pl_sum
            })
            data_rows.append({
                "구분": "올해 현지인", label: cl
            })
            data_rows.append({
                "구분": "올해 외지인", label: ct
            })
            data_rows.append({
                "구분": "올해 전체", label: cl_sum
            })

        # 📊 표 생성
        df = pd.DataFrame(data_rows).groupby("구분").sum()
        df["합계"] = df.sum(axis=1)
        total_all = df.loc["올해 전체", "합계"]
        df["전체 대비 비율"] = df["합계"].apply(lambda x: f"{(x / total_all):.2%}" if total_all > 0 else "0.00%")
        st.markdown("### 📋 전년도 / 올해 방문객 수 비교")
        st.dataframe(df, use_container_width=True)

        # 📌 날짜별 전체 구성비
        st.markdown("### 📅 날짜별 전체 방문객 구성비 (올해 기준)")
        day_totals = [curr_local[day] + curr_tourist[day] for day in days]
        day_percent = [f"{(v / sum(day_totals)):.2%}" if sum(day_totals) else "0.00%" for v in day_totals]
        st.dataframe(pd.DataFrame({
            "날짜": day_labels,
            "전체 방문객 수": day_totals,
            "전체 대비 구성비": day_percent
        }), use_container_width=True)

        # 🤖 GPT 시사점
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            examples = load_insight_examples("2_daily")
            prompt = f"""
[유사 시사점 예시]
{examples}

[일자별 방문객 비교]
{chr(10).join(summary_lines)}

일자별 현황과 전년도 대비 특성을 반영해 3~5문장으로 시사점을 작성해주세요.
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

def analyze_time_distribution():
    st.subheader("📊 3. 시간대별 관광객 존재현황 분석")
    st.markdown("시간대별 관광객 데이터를 포함한 엑셀 파일을 업로드하세요.")

    uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file)
    df = df.dropna(how="all")  # 전체 비어 있는 행 제거

    time_groups = [
        ("06~09시", ["06시 관광객", "07시 관광객", "08시 관광객"]),
        ("09~12시", ["09시 관광객", "10시 관광객", "11시 관광객"]),
        ("12~15시", ["12시 관광객", "13시 관광객", "14시 관광객"]),
        ("15~18시", ["15시 관광객", "16시 관광객", "17시 관광객"]),
        ("18~21시", ["18시 관광객", "19시 관광객", "20시 관광객"]),
        ("21~24시", ["21시 관광객", "22시 관광객", "23시 관광객"]),
    ]

    rows = []
    ratios = []

    # 역순 재정렬: 현지인 1~N일차 → 외지인 1~N일차
    half = len(df) // 2
    local_df = df.iloc[1:half+1][::-1].reset_index(drop=True)
    tourist_df = df.iloc[half+1:][::-1].reset_index(drop=True)

    for group_name, period_labels in time_groups:
        local_counts = []
        tourist_counts = []
        for i in range(len(local_df)):
            row_l = local_df.iloc[i]
            row_t = tourist_df.iloc[i]

            local_sum = sum([
                int(str(row_l[col]).replace("명", "").replace(",", ""))
                if pd.notnull(row_l[col]) and str(row_l[col]).strip() != "" else 0
                for col in period_labels
            ])
            tourist_sum = sum([
                int(str(row_t[col]).replace("명", "").replace(",", ""))
                if pd.notnull(row_t[col]) and str(row_t[col]).strip() != "" else 0
                for col in period_labels
            ])
            local_counts.append(local_sum)
            tourist_counts.append(tourist_sum)

        rows.append((group_name, "현지인", local_counts))
        rows.append((group_name, "외지인", tourist_counts))

        total = [l + t for l, t in zip(local_counts, tourist_counts)]
        local_ratios = [f"{l/t:.2%}" if t > 0 else "-" for l, t in zip(local_counts, total)]
        tourist_ratios = [f"{t/t2:.2%}" if t2 > 0 else "-" for t, t2 in zip(tourist_counts, total)]
        ratios.append((group_name, "현지인", local_ratios))
        ratios.append((group_name, "외지인", tourist_ratios))

    # 결과표 구성
    day_labels = [f"{i+1}일차" for i in range(len(local_df))]
    result_data = []
    for row in rows:
        data = {"구분": row[1], "시간대": row[0]}
        data.update({day: f"{cnt:,}명" for day, cnt in zip(day_labels, row[2])})
        result_data.append(data)

    for r in ratios:
        data = {"구분": "", "시간대": ""}
        data.update({day: rate for day, rate in zip(day_labels, r[2])})
        result_data.append(data)

    st.subheader("📊 시간대별 관광객 현황")
    st.dataframe(pd.DataFrame(result_data), use_container_width=True)

    # GPT 시사점
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        examples = load_insight_examples("3_time")
        lines = []
        for group_name, _, values in rows:
            total = [v for v in values]
            lines.append(f"{group_name} : {', '.join([f'{v:,}명' for v in total])}")
        prompt = f"""
[유사 시사점 예시]
{examples}

[시간대별 관광객 수]
{chr(10).join(lines)}

위 데이터를 참고해 시사점을 3~5문장으로 행정 보고서 스타일로 작성해주세요.
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

# ✅ 전체 분석기 실행 함수
def festival_analysis_app():
    st.title("🎯 축제 빅데이터 분석기")

    # ✅ 축제 기본정보 입력
    festival_basic_info()

    # ✅ 분석 항목 선택
    selected = st.selectbox("📂 분석 항목 선택", [
        "1. 축제 방문객 현황 분석",
        "2. 축제 일자별 방문객 수 분석",
        "3. 시간대별 관광객 존재현황 분석"
    ])

    # ✅ 항목별 실행
    if selected.startswith("1"):
        analyze_summary()
    elif selected.startswith("2"):
        analyze_daily_visitors()
    elif selected.startswith("3"):
        analyze_time_distribution()


