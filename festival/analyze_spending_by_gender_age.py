#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_spending_by_gender_age():
    st.subheader("📊 11. 성별/연령별 소비현황 분석기")

    # ✅ 총 소비금액 불러오기
    sales_inputs = st.session_state.get("card_sales_inputs", {})
    if not sales_inputs:
        st.warning("먼저 '8. 일자별 카드 소비 분석기'에서 데이터를 입력해주세요.")
        return

    total_sales = sum(sales_inputs.values()) * 1000  # 천원 → 원
    st.markdown(f"💰 **총 소비금액: {total_sales:,}원** (자동 계산됨)")

    # ✅ 기본 입력 구조
    age_groups = ["20대미만", "20대", "30대", "40대", "50대", "60대", "70대이상"]
    genders = ["남자", "여자"]

    input_rows = []
    st.markdown("### 📝 연령대/성별별 소비비율(%)을 입력해주세요")
    for age in age_groups:
        st.markdown(f"#### 📅 {age}")
        for gender in genders:
            col1, col2, col3 = st.columns([2, 2, 3])
            with col1:
                st.markdown(f"- **{gender}**")
            with col2:
                resident = st.number_input(f"{age}-{gender} 상주 (%)", min_value=0.0, max_value=100.0, key=f"{age}_{gender}_res")
            with col3:
                tourist = st.number_input(f"{age}-{gender} 유입 (%)", min_value=0.0, max_value=100.0, key=f"{age}_{gender}_tour")
            input_rows.append({
                "연령": age,
                "성별": gender,
                "상주": resident,
                "유입": tourist
            })

    if st.button("📊 분석 실행", key="btn_analyze_gender_age"):
        df_raw = pd.DataFrame(input_rows)
        df_raw["총비율"] = df_raw["상주"] + df_raw["유입"]
        df_raw["소비금액"] = df_raw["총비율"] / 100 * total_sales

        # ✅ 연령별 집계
        df_age = df_raw.groupby("연령", as_index=False)["소비금액"].sum()
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

        # ✅ 성별 집계
        df_gender = df_raw.groupby("성별", as_index=False)["소비금액"].sum()
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

        # ✅ GPT 시사점
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            age_top = df_age.sort_values("소비금액", ascending=False).head(3)
            age_names = ", ".join(age_top["연령"].tolist())

            gender_ratio = df_gender.set_index("성별")["소비비율"].to_dict()
            male_pct = gender_ratio.get("남자", 0)
            female_pct = gender_ratio.get("여자", 0)

            prompt = f"""다음은 {name}({period}, {location})의 연령별 및 성별 소비현황 분석입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~기여하고 있음', '~보임')  
▸ 각 문장은 ▸ 기호로 시작하며 3~5문장으로 작성  
▸ 연령별 소비금액 비율 및 중장년층 집중 여부를 중심으로 분석  
▸ 성별 소비비율 차이를 중심으로 구조적 특성 해석  
▸ 필요 시 ※ 표시로 부가 설명 포함  
▸ 부정적 표현은 지양하고, 전략적 해석을 기반으로 서술

## 주요 수치:
- 총 소비금액: {total_sales:,}원
- 연령별 상위 3계층: {age_names}
- 성별 비율: 남성 {male_pct:.2f}%, 여성 {female_pct:.2f}%

위 정보를 바탕으로 시사점을 작성해주세요.
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

