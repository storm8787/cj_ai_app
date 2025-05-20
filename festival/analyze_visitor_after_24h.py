#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io
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

def analyze_visitor_after_24h():
    st.subheader("📊 7-2. 외지인 24시간 이후지역 현황")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["시도", "시군구", "관광객수(%)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 7-2 템플릿 다운로드",
        data=buffer,
        file_name="7-2. template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 기준 방문객 수 입력
    total_visitors = st.number_input("🔢 기준 외지인 수 (24시간 이후 지역 이동자 수)", min_value=1, step=1)

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("📂 외지인 24시간 이후 이동지역 엑셀 업로드", type=["xlsx"])
    if not uploaded_file or total_visitors <= 0:
        return

    # ✅ 데이터 로드 및 유효성 검사
    df = pd.read_excel(uploaded_file).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]
    expected_cols = ["시도", "시군구", "관광객수(%)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ '시도', '시군구', '관광객수(%)' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 비율 계산 및 수치 변환
    df["비율"] = df["관광객수(%)"].astype(str).str.replace("%", "").astype(float) / 100
    df["관광객수"] = (df["비율"] * total_visitors).round().astype(int)

    # ✅ 구 단위 → 시 단위 병합
    merge_target_cities = [
        "청주시", "수원시", "안양시", "천안시", "용인시",
        "성남시", "고양시", "부천시", "안산시"
    ]
    def merge_sigungu(name):
        for city in merge_target_cities:
            if name.startswith(city):
                return city
        return name
    df["시군구"] = df["시군구"].apply(merge_sigungu)

    # ✅ 시군구 기준 그룹화
    #grouped = df.groupby("시군구", as_index=False)["관광객수"].sum()
    # ✅ 시도 + 시군구 합쳐서 새로운 분석용 컬럼 생성
    df["full_region"] = df["시도"].str.strip() + " " + df["시군구"].str.strip()
    grouped = df.groupby("full_region", as_index=False)["관광객수"].sum()
    grouped["비율"] = (grouped["관광객수"] / total_visitors * 100)

    # ✅ 상위 20개 + 기타 + 합계
    top20 = grouped.sort_values(by="관광객수", ascending=False).head(20).reset_index(drop=True)
    top20_total = top20["관광객수"].sum()
    others_row = {
        "시군구": "기타",
        "관광객수": total_visitors - top20_total,
        "비율": 100 - top20["비율"].sum()
    }
    sum_row = {
        "시군구": "합계",
        "관광객수": total_visitors,
        "비율": 100.0
    }
    final_df = pd.concat([
        top20,
        pd.DataFrame([others_row]),
        pd.DataFrame([sum_row])
    ], ignore_index=True)
    final_df["비율"] = final_df["비율"].round(2).astype(str) + "%"

    # ✅ 2열 분할 및 충돌 방지
    mid = len(final_df) // 2 + len(final_df) % 2
    left = final_df.iloc[:mid].reset_index(drop=True)
    right = final_df.iloc[mid:].reset_index(drop=True)
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_df = pd.concat([left, right], axis=1)

    # ✅ 출력
    st.markdown("#### 📋 24시간 이후 이동지역 분석 결과")
    st.dataframe(result_df, use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("7-2_after")

        summary = "\n".join([
            f"- {row['full_region']}: {int(row['관광객수']):,}명 ({row['비율']:.2f}%)"
            for _, row in grouped.iterrows()
        ])


        prompt = f"""다음은 {name}({period}, {location}) 축제 방문객의 '24시간 이후 이동지역' 분석입니다.

[이동지역별 외지인 수 요약]
{summary}

[참고자료]
{reference}

위 데이터를 바탕으로, 외지인의 이동 경로 및 지역 분포의 시사점을 행정 보고서 스타일로 3~5문장 작성해주세요.
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

