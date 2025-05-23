#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_external_visitor_spending_by_region():
    st.subheader("📊 12. 외지인 방문객 축제장 주변 소비현황")

    # ✅ 외지인 소비금액 (10번 분석기에서 저장)
    external_total_sales = st.session_state.get("external_total_sales", None)
    if not external_total_sales:
        st.warning("먼저 '10. 방문유형별 소비현황'에서 외지인 소비금액을 분석해주세요.")
        return

    # ✅ 외지인 방문객 비율 정보 (7번 분석기에서 저장)
    visitor_share = st.session_state.get("visitor_by_province", {})

    TEMPLATE_PATH = os.path.join(os.getcwd(), "data", "templates", "12_template.xlsx")
    # ✅ 템플릿 다운로드 버튼
    try:
        with open("data/templates/12_template.xlsx", "rb") as f:
            st.download_button(
                label="📥 템플릿 다운로드 (외지인 소비지역 입력용)",
                data=f,
                file_name="12_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.error("❌ 템플릿 파일이 없습니다. 경로를 확인해주세요.")

    # ✅ 업로드
    uploaded_file = st.file_uploader("📂 외지인 소비지역 데이터 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file)
    if not all(col in df.columns for col in ["한글시도명", "한글시군구명", "매출금액"]):
        st.error("❌ '한글시도명', '한글시군구명', '매출금액' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 구 단위를 시로 병합
    merge_target_cities = [
        "청주시", "수원시", "안양시", "천안시", "용인시",
        "성남시", "고양시", "부천시", "안산시"
    ]

    def merge_sigungu(name):
        for city in merge_target_cities:
            if name.startswith(city):
                return city
        return name

    df["시군구"] = df["한글시군구명"].apply(merge_sigungu)

    # ✅ 시군구 기준 그룹화
    df_grouped = df.groupby("시군구", as_index=False)["매출금액"].sum()
    df_grouped = df_grouped.sort_values("매출금액", ascending=False).reset_index(drop=True)

    df_grouped["비중(%)"] = df_grouped["매출금액"] / external_total_sales * 100
    df_grouped["매출금액"] = df_grouped["매출금액"].round(0).astype(int)
    df_grouped["매출금액"] = df_grouped["매출금액"].apply(lambda x: f"{x:,}")
    df_grouped["비중(%)"] = df_grouped["비중(%)"].apply(lambda x: f"{x:.2f}%")

    df_top10 = df_grouped.head(10)

    # ✅ 결과 출력
    st.markdown("### 📊 외지인 소비지역 상위 10개 시군구")
    st.dataframe(df_top10.reset_index(drop=True))

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")

        # 요약 텍스트 구성
        top_lines = []
        for _, row in df_top10.iterrows():
            top_lines.append(f"- {row['시군구']}: {row['비중(%)']}")
        top_str = "\n".join(top_lines)

        visitor_compare_lines = []
        for _, row in df_top10.iterrows():
            region = row["시군구"]
            visitor_ratio = visitor_share.get(region, None)
            if visitor_ratio:
                visitor_compare_lines.append(f"{region}: 방문객 {visitor_ratio:.2f}% / 소비 {row['비중(%)']}")

        visitor_str = "\n".join(visitor_compare_lines)

        prompt = f"""다음은 {name}({period}, {location})의 외지인 소비지역 분석입니다.

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

