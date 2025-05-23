#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_spending_by_gender_age():
    st.subheader("📊 11. 성별/연령별 소비현황 분석기")

    # ✅ 전체 소비금액 가져오기 (8번 분석기에서 저장된 값)
    sales_inputs = st.session_state.get("card_sales_inputs", {})
    if not sales_inputs:
        st.warning("먼저 '8. 일자별 카드 소비 분석기'에서 데이터를 입력해주세요.")
        return

    total_sales = sum(sales_inputs.values()) * 1000  # 천원 → 원
    st.markdown(f"💰 **총 소비금액: {total_sales:,}원** (자동 계산됨)")

    # ✅ 템플릿 업로드
    uploaded_file = st.file_uploader("📂 성별/연령별 소비비율 엑셀 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df_raw = pd.read_excel(uploaded_file, sheet_name="Sheet1")

    # ✅ 소비금액 계산
    df_raw["총소비금액"] = (df_raw["상주"] + df_raw["유입"]) / 100 * total_sales

    # ✅ 10-1. 연령별 소비현황
    df_age = df_raw.groupby("연령구분", as_index=False)["총소비금액"].sum()
    df_age.columns = ["연령", "소비금액"]
    df_age["소비비율"] = (df_age["소비금액"] / df_age["소비금액"].sum() * 100).round(2)
    df_age["순위"] = df_age["소비금액"].rank(ascending=False).astype(int)
    df_age["비고"] = df_age["순위"].apply(lambda x: f"{x}위" if x <= 5 else "")

    df_age_final = pd.concat([
        pd.DataFrame([{
            "연령": "계",
            "소비금액": df_age["소비금액"].sum(),
            "소비비율": "100%",
            "비고": ""
        }]),
        df_age[["연령", "소비금액", "소비비율", "비고"]]
    ], ignore_index=True)

    # ✅ 10-2. 성별 소비현황
    df_gender = df_raw.groupby("성별구분", as_index=False)["총소비금액"].sum()
    df_gender.columns = ["성별", "소비금액"]
    df_gender["소비비율"] = (df_gender["소비금액"] / df_gender["소비금액"].sum() * 100).round(2)

    df_gender_final = pd.concat([
        pd.DataFrame([{
            "성별": "계",
            "소비금액": df_gender["소비금액"].sum(),
            "소비비율": "100%"
        }]),
        df_gender[["성별", "소비금액", "소비비율"]]
    ], ignore_index=True)

    # ✅ 출력
    st.markdown("### 📊 10-1. 연령별 소비현황")
    st.dataframe(df_age_final.set_index("연령"))

    st.markdown("### 📊 10-2. 성별 소비현황")
    st.dataframe(df_gender_final.set_index("성별"))

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")

        age_insight = df_age.sort_values("소비금액", ascending=False).head(3)
        top_ages = ", ".join(age_insight["연령"].tolist())
        gender_ratio = df_gender.set_index("성별")["소비비율"].to_dict()
        male_pct = gender_ratio.get("남자", 0)
        female_pct = gender_ratio.get("여자", 0)

        prompt = f"""다음은 {name}({period}, {location})의 연령별 및 성별 소비현황 분석입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~기여하고 있음', '~보임')  
▸ 각 문장은 ▸ 기호로 시작하여 3~5문장 구성  
▸ 연령별 상위 계층 비중과 소비 집중도 중심으로 작성  
▸ 성별 비율 차이를 구체적으로 제시하고, 소비 패턴 차이를 정책적으로 해석  
▸ 필요 시 ※ 표시로 부가 설명 포함  
▸ 부정적 표현은 지양하고, 중립 또는 전략적 표현 사용

## 주요 수치:
- 총 소비금액: {total_sales:,}원
- 연령별 상위 3계층: {top_ages}
- 성별 비율: 남성 {male_pct:.2f}%, 여성 {female_pct:.2f}%

위 정보를 바탕으로 소비 특성 시사점을 작성해주세요.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 소비 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )

        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

