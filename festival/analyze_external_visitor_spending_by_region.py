#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_external_visitor_spending_by_region():
    st.subheader("📊 12. 외지인 방문객 축제장 주변 소비현황")

    # ✅ 외지인 소비금액 (10번 분석기에서 저장)
    external_total_sales = st.session_state.get("external_total_sales", None)
    if not external_total_sales:
        st.warning("먼저 '10. 방문유형별 소비현황'에서 외지인 소비금액을 확인해주세요.")
        return

    # ✅ 외지인 방문객 비율 정보 (7번 분석기에서 저장)
    visitor_share = st.session_state.get("visitor_by_province", {})

    TEMPLATE_PATH = "data/templates/12_template.xlsx"
    try:
        with open(TEMPLATE_PATH, "rb") as f:
            st.download_button(
                label="📥 템플릿 다운로드 (외지인 소비지역 입력용)",
                data=f,
                file_name="12_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.error("❌ 템플릿 파일이 없습니다. 경로를 확인해주세요.")

    uploaded_file = st.file_uploader("📂 외지인 소비지역 데이터 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file)
    if not all(col in df.columns for col in ["한글시도명", "한글시군구명", "매출금액"]):
        st.error("❌ '한글시도명', '한글시군구명', '매출금액' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 병합 대상 설정
    exclude_cities = ["충주시", "포천시"]
    merge_target_cities = [
        "청주시", "수원시", "안양시", "천안시", "용인시",
        "성남시", "고양시", "부천시", "안산시"
    ]
    merge_metros = {
        "서울": "서울시", "부산": "부산시", "대구": "대구시",
        "인천": "인천시", "광주": "광주시", "대전": "대전시",
        "울산": "울산시", "세종": "세종시"
    }

    def merge_sigungu(sigungu, sido):
        for prefix, merged in merge_metros.items():
            if sido.startswith(prefix):
                return merged
        for city in merge_target_cities:
            if sigungu.startswith(city):
                return city
        return sigungu

    df["시군구"] = df.apply(lambda row: merge_sigungu(row["한글시군구명"], row["한글시도명"]), axis=1)
    df = df[~df["시군구"].isin(exclude_cities)]

    df_grouped = df.groupby("시군구", as_index=False)["매출금액"].sum()
    df_grouped = df_grouped.sort_values("매출금액", ascending=False).reset_index(drop=True)

    df_grouped["비중(%)"] = df_grouped["매출금액"] / external_total_sales * 100
    df_grouped["매출금액"] = df_grouped["매출금액"].round(0).astype(int)
    df_grouped["매출금액"] = df_grouped["매출금액"].apply(lambda x: f"{x:,}")
    df_grouped["비중(%)"] = df_grouped["비중(%)"].apply(lambda x: f"{x:.2f}%")

    df_top10 = df_grouped.head(10)

    st.markdown("### 📊 외지인 소비지역 상위 10개 시군구")
    st.dataframe(df_top10.reset_index(drop=True))

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")

        top_str = "\n".join([f"- {row['시군구']}: {row['비중(%)']}" for _, row in df_top10.iterrows()])
        visitor_str = "\n".join([
            f"{row['시군구']}: 방문객 {visitor_share.get(row['시군구'], 0):.2f}% / 소비 {row['비중(%)']}"
            for _, row in df_top10.iterrows()
            if row["시군구"] in visitor_share
        ])

        prompt = f"""다음은 {name}({period}, {location})의 외지인 소비지역 분석입니다.
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ ▸ 기호로 시작하여 3~5문장으로 작성  
▸ 시군구별 소비금액 비중을 중심으로 분석하며, 전체 외지인 소비금액 대비 각 지역의 기여도를 해석할 것  
▸ 소비 비중이 높은 지역이 방문객 비중과 일치하는지 비교하고, 편중 여부 해석  
▸ 소비금액 상위 시군구(10개)의 기여도와 지역 분포를 기반으로 전략적 정책 제언 포함  
▸ 수도권 또는 인접 지역 집중 여부도 평가  
▸ 각 문장은 ▸ 기호로 시작하며, 보고서 문체로 자연스럽게 연결

## 소비지역 TOP10
{top_str}

## 방문객 대비 소비 비교 (상위 10)
{visitor_str}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 소비 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=700
        )

        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

