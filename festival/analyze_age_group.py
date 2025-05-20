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
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 5번 분석기: 연령별 방문객 분석
def analyze_age_group():
    st.subheader("📊 5. 연령별 방문객 분석")

    template_path = "data/templates/5_template.xlsx"
    os.makedirs(os.path.dirname(template_path), exist_ok=True)

    if not os.path.exists(template_path):
        columns = ["구분", "날짜", "10대미만", "10대", "20대", "30대", "40대", "50대", "60대", "70대이상"]
        rows = []
        for group in ["현지인", "외지인"]:
            for i in range(3, 0, -1):
                row = [group, f"{i}일차"] + [0] * (len(columns) - 2)
                rows.append(row)
        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(template_path, index=False)

    # ✅ 다운로드 버튼 with 에러 핸들링
    try:
        with open(template_path, "rb") as f:
            st.download_button(
                label="📥 템플릿 다운로드: 연령별 방문객 분석",
                data=f,
                file_name="5_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ 다운로드 버튼 오류: {e}")

    uploaded_file = st.file_uploader("📂 연령대별 방문객 엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    # ✅ 데이터 로드
    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ 필수 컬럼 확인
    age_columns = ["10대미만", "10대", "20대", "30대", "40대", "50대", "60대", "70대이상"]
    required_cols = {"구분", "날짜", *age_columns}
    if not required_cols.issubset(set(df.columns)):
        st.error("❌ 업로드한 엑셀 파일에 필수 컬럼이 누락되어 있습니다.")
        return

    # ✅ 수치 정제
    df[age_columns] = df[age_columns].applymap(lambda x: int(str(x).replace("명", "").replace(",", "")) if pd.notnull(x) else 0)

    # ✅ 날짜 오름차순 정렬
    df["날짜정렬"] = df["날짜"].str.extract(r"(\d+)")[0]
    df = df[pd.notnull(df["날짜정렬"])].copy()  # 소계/비율 같은 행 제거
    df["날짜정렬"] = df["날짜정렬"].astype(int)
    df = df.sort_values(by=["구분", "날짜정렬"]).drop(columns="날짜정렬")

    # ✅ 합계 계산
    df["합계"] = df[age_columns].sum(axis=1)

    # ✅ 현지인/외지인 분리
    local_df = df[df["구분"] == "현지인"].copy()
    tourist_df = df[df["구분"] == "외지인"].copy()

    # ✅ 소계 및 비율 계산
    local_sum = local_df[age_columns + ["합계"]].sum().astype(int)
    tourist_sum = tourist_df[age_columns + ["합계"]].sum().astype(int)
    total_sum = local_sum + tourist_sum

    local_total = local_sum["합계"]
    tourist_total = tourist_sum["합계"]
    grand_total = total_sum["합계"]

    local_ratio = (local_sum[age_columns] / local_total).apply(lambda x: f"{x:.1%}")
    tourist_ratio = (tourist_sum[age_columns] / tourist_total).apply(lambda x: f"{x:.1%}")
    total_ratio = (total_sum[age_columns] / grand_total).apply(lambda x: f"{x:.1%}")

    # ✅ 소계 및 비율 행 생성
    local_sum_row = pd.DataFrame([["현지인", "소계"] + local_sum[age_columns].tolist() + [local_total]], columns=df.columns)
    local_ratio_row = pd.DataFrame([["현지인", "비율"] + local_ratio.tolist() + ["100%"]], columns=df.columns)

    tourist_sum_row = pd.DataFrame([["외지인", "소계"] + tourist_sum[age_columns].tolist() + [tourist_total]], columns=df.columns)
    tourist_ratio_row = pd.DataFrame([["외지인", "비율"] + tourist_ratio.tolist() + ["100%"]], columns=df.columns)

    total_sum_row = pd.DataFrame([["합계", ""] + total_sum[age_columns].tolist() + [grand_total]], columns=df.columns)
    total_ratio_row = pd.DataFrame([["비율", ""] + total_ratio.tolist() + ["100%"]], columns=df.columns)

    # ✅ 최종 테이블 구성
    final_df = pd.concat([
        local_df,
        local_sum_row,
        local_ratio_row,
        tourist_df,
        tourist_sum_row,
        tourist_ratio_row,
        total_sum_row,
        total_ratio_row
    ], ignore_index=True)

    st.dataframe(final_df, use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("5_age")

        summary = "\n".join([
            f"- {age}: 현지인 {local_sum[age]:,}명 / 외지인 {tourist_sum[age]:,}명 / 전체 {total_sum[age]:,}명"
            for age in age_columns
        ])

        prompt = f"""다음은 {name}({period}, {location}) 축제의 연령대별 방문객 분석입니다.

[연령대별 방문객 수 요약]
{summary}

[참고자료]
{reference}

위 데이터를 참고하여, 연령대별 방문 패턴과 주요 특징을 행정 보고서 스타일로 3~5문장 작성해주세요.
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

