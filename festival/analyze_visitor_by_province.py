#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io
from openai import OpenAI
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 시사점 예시 불러오기
def load_insight_examples(section_id):
    try:
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def analyze_visitor_by_province():
    st.subheader("📊 7-1. 시도 및 시군구별 외지인 방문객 거주지 분석기")

    # ✅ 템플릿 다운로드 제공
    template_df = pd.DataFrame(columns=["시도", "시군구", "관광객수(%)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 7-1 템플릿 다운로드",
        data=buffer,
        file_name="7-1. template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 기준 방문객 수 입력
    total_visitors = st.number_input("🔢 기준 외지인 방문객 수를 입력하세요", min_value=1, step=1)

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("📂 시도별 비율 데이터 엑셀 업로드", type=["xlsx"])
    if not uploaded_file or total_visitors <= 0:
        return

    # ✅ 데이터 로드 및 유효성 확인
    df = pd.read_excel(uploaded_file).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]

    expected_cols = ["시도", "시군구", "관광객수(%)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ '시도', '시군구', '관광객수(%)' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 비율 변환 및 관광객 수 계산
    df["비율"] = df["관광객수(%)"].astype(str).str.replace("%", "").astype(float) / 100
    df["관광객수"] = (df["비율"] * total_visitors).round().astype(int)

    # ✅ 시도 기준 그룹화
    grouped = df.groupby("시도", as_index=False)["관광객수"].sum()
    grouped["비율"] = (grouped["관광객수"] / total_visitors * 100).round(2).astype(str) + "%"

    # ✅ 정렬 후 2열 분할
    grouped = grouped.sort_values(by="관광객수", ascending=False).reset_index(drop=True)
    midpoint = len(grouped) // 2 + len(grouped) % 2
    left = grouped.iloc[:midpoint].reset_index(drop=True)
    right = grouped.iloc[midpoint:].reset_index(drop=True)

    # ✅ 접미어 붙이기 (컬럼명 중복 방지)
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    
    result_df = pd.concat([left, right], axis=1)

    # ✅ 결과 DataFrame 구조 복제
    empty_row = pd.DataFrame(columns=result_df.columns)

    # ✅ 딕셔너리 형태로 값 채우기
    last_row_values = {}
    for col in result_df.columns:
        if "시도" in col:
            last_row_values[col] = "합계"
        elif "관광객수" in col:
            last_row_values[col] = grouped["관광객수"].sum()
        elif "비율" in col:
            last_row_values[col] = "100.00%"
        else:
            last_row_values[col] = ""

    # ✅ DataFrame으로 변환, result_df와 동일한 구조로 보장
    total_row_df = pd.DataFrame([last_row_values], columns=result_df.columns)

    # ✅ 안전하게 붙이기
    result_df = pd.concat([result_df, total_row_df], ignore_index=True)

    # ✅ 출력
    st.markdown("#### 📋 시도별 분석 결과")
    st.dataframe(result_df, use_container_width=True)

# -------------------------
# ✅ 7-2. 시군구별 방문객 분석
# -------------------------

    st.markdown("### 🏙️ 7-2. 시군구별 외지인 방문객 현황")

    # ✅ 구 단위를 시로 병합할 시 리스트
    merge_target_cities = [
        "청주시", "수원시", "안양시", "천안시", "용인시",
        "성남시", "고양시", "부천시", "안산시"
    ]

    def merge_sigungu(name):
        for city in merge_target_cities:
            if name.startswith(city):
                return city
        return name

    # ✅ 병합 적용
    df["시군구"] = df["시군구"].apply(merge_sigungu)

    # ✅ 시군구 기준으로 그룹화
    gungu_grouped = df.groupby("시군구", as_index=False)["관광객수"].sum()
    gungu_grouped["비율"] = (gungu_grouped["관광객수"] / total_visitors * 100)

    # ✅ 상위 20개 추출
    top20 = gungu_grouped.sort_values(by="관광객수", ascending=False).head(20).reset_index(drop=True)

    # ✅ 기타 계산
    top20_total = top20["관광객수"].sum()
    others_row = {
        "시군구": "기타",
        "관광객수": total_visitors - top20_total,
        "비율": 100 - top20["비율"].sum()
    }
    gungu_final = pd.concat([
        top20,
        pd.DataFrame([others_row]),
        pd.DataFrame([{
            "시군구": "합계",
            "관광객수": total_visitors,
            "비율": 100.0
        }])
    ], ignore_index=True)

    # ✅ 비율 포맷팅
    gungu_final["비율"] = gungu_final["비율"].round(2).astype(str) + "%"

    # ✅ 2열 분할
    mid = len(gungu_final) // 2 + len(gungu_final) % 2
    left = gungu_final.iloc[:mid].reset_index(drop=True)
    right = gungu_final.iloc[mid:].reset_index(drop=True)

    # ✅ 접미어로 열 충돌 방지
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_gungu = pd.concat([left, right], axis=1)

    # ✅ 시군구 분석 결과 출력
    st.dataframe(result_gungu, use_container_width=True)

    # ✅ GPT 시사점 생성 (시도 + 시군구 각각)
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("7-1_visitor")

        # ✅ [1] 시도별 요약 텍스트
        grouped_summary = "\n".join([
            f"- {row['시도']}: {int(row['관광객수']):,}명 ({row['비율']})"
            for _, row in grouped.iterrows()
        ])

        grouped_prompt = f"""다음은 {name}({period}, {location}) 축제의 시도별 외지인 방문객 분석입니다.

[시도별 외지인 방문객 수 요약]
{grouped_summary}

[참고자료]
{reference}

위 데이터를 바탕으로, 시도별 분포와 특징을 행정 보고서 스타일로 3~5문장 작성해주세요.
"""

        grouped_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": grouped_prompt}
            ],
            temperature=0.5,
            max_tokens=700
        )

        st.subheader("🧠 GPT 시사점 (시도 기준)")
        st.write(grouped_response.choices[0].message.content)

        # ✅ [2] 시군구별 요약 텍스트
        gungu_summary = "\n".join([
            f"- {row['시군구']}: {int(row['관광객수']):,}명 ({row['비율']})"
            for _, row in gungu_final.iterrows() if row["시군구"] not in ["기타", "합계"]
        ])

        gungu_prompt = f"""다음은 {name}({period}, {location}) 축제의 시군구별 외지인 방문객 분석입니다.

[시군구별 외지인 방문객 수 요약]
{gungu_summary}

[참고자료]
{reference}

위 데이터를 바탕으로, 주요 시군구 방문 분포와 특징을 행정 보고서 스타일로 3~5문장 작성해주세요.
"""

        gungu_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": gungu_prompt}
            ],
            temperature=0.5,
            max_tokens=700
        )

        st.subheader("🧠 GPT 시사점 (시군구 기준)")
        st.write(gungu_response.choices[0].message.content)

