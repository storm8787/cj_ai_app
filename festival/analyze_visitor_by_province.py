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

def analyze_visitor_by_province():
    st.subheader("📊 7-1. 시도 및 시군구별 외지인 방문객 거주지 분석기")

    # ✅ 템플릿 다운로드
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

    # ✅ 데이터 로드 및 유효성 검사
    df = pd.read_excel(uploaded_file).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]
    expected_cols = ["시도", "시군구", "관광객수(%)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ '시도', '시군구', '관광객수(%)' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 관광객 수 계산
    df["비율"] = df["관광객수(%)"].astype(str).str.replace("%", "").astype(float) / 100
    df["관광객수"] = (df["비율"] * total_visitors).round().astype(int)

    # ✅ 시도별 그룹화 및 2열 출력
    grouped = df.groupby("시도", as_index=False)["관광객수"].sum()
    grouped["비율"] = (grouped["관광객수"] / total_visitors * 100)

    # 정렬 추가
    grouped = grouped.sort_values(by="관광객수", ascending=False).reset_index(drop=True)
    grouped["관광객수"] = grouped["관광객수"].astype(int)


    left = grouped.iloc[:len(grouped)//2 + len(grouped)%2].reset_index(drop=True)
    right = grouped.iloc[len(grouped)//2 + len(grouped)%2:].reset_index(drop=True)
    left["비율"] = left["비율"].round(2).astype(str) + "%"
    right["비율"] = right["비율"].round(2).astype(str) + "%"
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_df = pd.concat([left, right], axis=1)

    # ✅ 합계 행 추가
    total_row = {
        "시도_1": "합계",
        "관광객수_1": grouped["관광객수"].sum(),
        "비율_1": "100.00%",
        "시도_2": "", "관광객수_2": "", "비율_2": ""
    }
    result_df = pd.concat([result_df, pd.DataFrame([total_row])], ignore_index=True)

    st.markdown("#### 📋 시도별 분석 결과")
    st.dataframe(result_df, use_container_width=True)

    # -------------------------
    # ✅ 시군구별 외지인 방문객 분석 (full_region 기준)
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
    df["시군구"] = df["시군구"].apply(merge_sigungu)
    df["full_region"] = df["시도"].str.strip() + " " + df["시군구"].str.strip()

    # ✅ full_region 기준 그룹화
    grouped_gungu = df.groupby("full_region", as_index=False)["관광객수"].sum()
    grouped_gungu["비율"] = (grouped_gungu["관광객수"] / total_visitors * 100)

    # ✅ 상위 20개 + 기타 + 합계
    top20 = grouped_gungu.sort_values(by="관광객수", ascending=False).head(20).reset_index(drop=True)
    top20_total = top20["관광객수"].sum()
    others_row = {
        "full_region": "기타",
        "관광객수": total_visitors - top20_total,
        "비율": 100 - top20["비율"].sum()
    }
    sum_row = {
        "full_region": "합계",
        "관광객수": total_visitors,
        "비율": 100.0
    }

    # ✅ 분할 및 기타/합계 오른쪽 배치
    left = top20.iloc[:10].reset_index(drop=True)
    right = top20.iloc[10:].reset_index(drop=True)
    right = pd.concat([right, pd.DataFrame([others_row, sum_row])], ignore_index=True)

    # ✅ 포맷팅 및 접미어 처리
    left["비율"] = left["비율"].round(2).astype(str) + "%"
    right["비율"] = right["비율"].round(2).astype(str) + "%"
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_gungu = pd.concat([left, right], axis=1)

    # ✅ 시군구 분석 결과 출력
    st.dataframe(result_gungu, use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("7-1_visitor")

        # ✅ 시도 기준 요약
        summary_sido = "\n".join([
            f"- {row['시도']}: {int(row['관광객수']):,}명 ({float(row['비율'].replace('%','')):.2f}%)"
            for _, row in grouped.iterrows()
        ])

        # ✅ 시군구 기준 요약
        summary_gungu = "\n".join([
            f"- {row['full_region']}: {int(row['관광객수']):,}명 ({row['비율']})"
            for _, row in grouped_gungu.iterrows()
        ])

        # ✅ GPT 프롬프트 (시도)
        prompt_sido = f"""다음은 {name}({period}, {location}) 축제의 시도별 외지인 방문객 분석입니다.

[시도별 외지인 방문객 수 요약]
{summary_sido}

[참고자료]
{reference}

위 데이터를 바탕으로, 시도별 분포와 특징을 행정 보고서 스타일로 3~5문장 작성해주세요.
"""
        response_sido = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt_sido}
            ],
            temperature=0.5,
            max_tokens=700
        )
        st.subheader("🧠 GPT 시사점 (시도 기준)")
        st.write(response_sido.choices[0].message.content)

        # ✅ GPT 프롬프트 (시군구)
        prompt_gungu = f"""다음은 {name}({period}, {location}) 축제의 시군구별 외지인 방문객 분석입니다.

[시군구별 외지인 방문객 수 요약]
{summary_gungu}

[참고자료]
{reference}

위 데이터를 바탕으로, 시군구별 주요 방문 분포와 특징을 행정 보고서 스타일로 3~5문장 작성해주세요.
"""
        response_gungu = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt_gungu}
            ],
            temperature=0.5,
            max_tokens=700
        )
        st.subheader("🧠 GPT 시사점 (시군구 기준)")
        st.write(response_gungu.choices[0].message.content)

