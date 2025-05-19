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

def extract_day_number(text):
    try:
        return int(str(text).strip().replace("일차", ""))
    except:
        return 0

# ✅ 3번 분석기:  시간대별 관광객 존재현황 분석 (표 + GPT 시사점)
def analyze_time_distribution():
    st.subheader("📊 3. 시간대별 관광객 존재현황 분석")
    st.markdown("시간대별 관광객 데이터를 포함한 엑셀 파일을 업로드하세요.")

    uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ 시간대 그룹 정의
    time_groups = [
        ("06~09시", ["06시 관광객", "07시 관광객", "08시 관광객"]),
        ("09~12시", ["09시 관광객", "10시 관광객", "11시 관광객"]),
        ("12~15시", ["12시 관광객", "13시 관광객", "14시 관광객"]),
        ("15~18시", ["15시 관광객", "16시 관광객", "17시 관광객"]),
        ("18~21시", ["18시 관광객", "19시 관광객", "20시 관광객"]),
        ("21~24시", ["21시 관광객", "22시 관광객", "23시 관광객"]),
    ]

    def extract_day_number(text):
        try:
            return int(str(text).strip().replace("일차", ""))
        except:
            return 0

    # ✅ 현지인과 외지인 구분 및 역순 정렬 (엑셀이 4일차 → 1일차 순으로 되어 있다는 전제)
    local_df = df[df.iloc[:, 0] == "현지인"].iloc[::-1].reset_index(drop=True)
    tourist_df = df[df.iloc[:, 0] == "외지인"].iloc[::-1].reset_index(drop=True)

    n_days = len(local_df)
    day_labels = [f"{i+1}일차" for i in range(n_days)]

    result_rows = []

    # ✅ 시간대 합계 생성
    def process_group(df_group):
        group_data = []
        for _, row in df_group.iterrows():
            day_data = {}
            for group_name, cols in time_groups:
                total = sum([
                    int(str(row[col]).replace(",", "").replace("명", "")) if pd.notnull(row[col]) else 0
                    for col in cols
                ])
                day_data[group_name] = total
            group_data.append(day_data)
        return group_data

    local_data = process_group(local_df)
    tourist_data = process_group(tourist_df)

    # ✅ 방문객 수 행 생성
    def make_visitor_rows(group_data, label):
        rows = []
        for i, day in enumerate(day_labels):
            row = {"구분": label, "날짜": day}
            for group_name in time_groups:
                col = group_name[0]
                row[col] = f"{group_data[i][col]:,}명"
            rows.append(row)
        return rows

    result_rows.extend(make_visitor_rows(local_data, "현지인"))
    result_rows.extend(make_visitor_rows(tourist_data, "외지인"))

    # ✅ 빈 행
    result_rows.append({"구분": "", "날짜": ""})

    # ✅ 비율 행 생성
    def make_ratio_rows(group_data, label):
        rows = []
        for i, day in enumerate(day_labels):
            row = {"구분": label, "날짜": ""}
            total = sum(group_data[i].values())
            for group_name in time_groups:
                col = group_name[0]
                ratio = group_data[i][col] / total if total > 0 else 0
                row[col] = f"{ratio:.2%}"
            rows.append(row)
        return rows

    result_rows.extend(make_ratio_rows(local_data, "현지인"))
    result_rows.extend(make_ratio_rows(tourist_data, "외지인"))

    # ✅ 출력
    st.subheader("📊 시간대별 관광객 현황 (방문객 수 + 비율)")
    st.dataframe(pd.DataFrame(result_rows), use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        examples = load_insight_examples("3_time")
        lines = []
        for i, group_name in enumerate([g[0] for g in time_groups]):
            local_line = f"{group_name} - 현지인: " + ", ".join(
                f"{d[group_name]:,}명" for d in local_data
            )
            tourist_line = f"{group_name} - 외지인: " + ", ".join(
                f"{d[group_name]:,}명" for d in tourist_data
            )
            lines.extend([local_line, tourist_line])
        prompt = f"""
[유사 시사점 예시]
{examples}

[시간대별 관광객 수]
{chr(10).join(lines)}

위 데이터를 참고하여 시간대별 특성과 변화 양상을 행정 보고서 스타일로 3~5문장 작성해주세요.
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


