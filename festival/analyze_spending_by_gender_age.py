#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_spending_by_gender_age():
    st.subheader("📊 11. 성별/연령별 소비현황 분석기")

    # ✅ 전체 소비금액
    sales_inputs = st.session_state.get("card_sales_inputs", {})
    if not sales_inputs:
        st.warning("먼저 '8. 일자별 카드 소비 분석기'에서 데이터를 입력해주세요.")
        return

    total_sales = sum(sales_inputs.values()) * 1000  # 천원 → 원
    st.markdown(f"💰 **총 소비금액: {total_sales:,}원** (자동 계산됨)")

    TEMPLATE_PATH = os.path.join(os.getcwd(), "data", "templates", "11_template.xlsx")
    # ✅ 템플릿 다운로드
    try:
        with open("data/templates/11_template.xlsx", "rb") as f:
            st.download_button(
                label="📥 템플릿 다운로드 (성별/연령 소비비율 입력용)",
                data=f,
                file_name="11_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.error("❌ 템플릿 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")

    # ✅ 템플릿 업로드
    uploaded_file = st.file_uploader("📂 성별/연령별 소비비율 엑셀 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df_raw = pd.read_excel(uploaded_file, sheet_name="Sheet1")
    df_raw["총소비금액"] = (df_raw["상주"] + df_raw["유입"]) / 100 * total_sales

    # ✅ 10-1. 연령별 소비현황
    df_age = df_raw.groupby("연령구분", as_index=False)["총소비금액"].sum()
    df_age.columns = ["연령", "소비금액"]
    df_age["소비비율"] = (df_age["소비금액"] / df_age["소비금액"].sum() * 100)
    df_age["순위"] = df_age["소비금액"].rank(ascending=False).astype(int)
    df_age["비고"] = df_age["순위"].apply(lambda x: f"{x}위" if x <= 5 else "")

    df_age_display = df_age.copy()
    df_age_display["소비금액"] = df_age_display["소비금액"].round(0).astype(int)
    df_age_display["소비금액"] = df_age_display["소비금액"].apply(lambda x: f"{x:,}")
    df_age_display["소비비율"] = df_age["소비비율"].apply(lambda x: f"{x:.2f}%")

    df_age_final = pd.concat([
        pd.DataFrame([{
            "연령": "계",
            "소비금액": f"{int(total_sales):,}",
            "소비비율": "100%",
            "비고": ""
        }]),
        df_age_display[["연령", "소비금액", "소비비율", "비고"]]
    ], ignore_index=True)

    # ✅ 사용자 지정 순서 정렬 (계 맨 위 유지)
    df_total_row = df_age_final[df_age_final["연령"] == "계"]
    df_rest = df_age_final[df_age_final["연령"] != "계"]

    age_order = ["20대미만", "20대", "30대", "40대", "50대", "60대", "70대이상"]
    df_rest["연령"] = pd.Categorical(df_rest["연령"], categories=age_order, ordered=True)
    df_rest = df_rest.sort_values("연령").reset_index(drop=True)
    df_age_final = pd.concat([df_total_row, df_rest], ignore_index=True)

    # ✅ 10-2. 성별 소비현황
    df_gender = df_raw.groupby("성별구분", as_index=False)["총소비금액"].sum()
    df_gender.columns = ["성별", "소비금액"]
    df_gender["소비비율"] = (df_gender["소비금액"] / df_gender["소비금액"].sum() * 100)

    df_gender_display = df_gender.copy()
    df_gender_display["소비금액"] = df_gender_display["소비금액"].round(0).astype(int)
    df_gender_display["소비금액"] = df_gender_display["소비금액"].apply(lambda x: f"{x:,}")
    df_gender_display["소비비율"] = df_gender["소비비율"].apply(lambda x: f"{x:.2f}%")

    df_gender_final = pd.concat([
        pd.DataFrame([{
            "성별": "계",
            "소비금액": f"{int(total_sales):,}",
            "소비비율": "100%"
        }]),
        df_gender_display[["성별", "소비금액", "소비비율"]]
    ], ignore_index=True)

    # ✅ 결과 출력
    st.markdown("### 📊 10-1. 연령별 소비현황")
    st.dataframe(df_age_final.set_index("연령"))

    st.markdown("### 📊 10-2. 성별 소비현황")
    st.dataframe(df_gender_final.set_index("성별"))

    # ✅ GPT 시사점
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")

        top_age_rows = df_age.sort_values("순위").head(3)
        top_ages = ", ".join([
            f"{row['연령']}({row['소비비율']:.2f}%)" for _, row in top_age_rows.iterrows()
        ])

        gender_ratio = df_gender.set_index("성별")["소비비율"].to_dict()
        male_pct = gender_ratio.get("남자", 0)
        female_pct = gender_ratio.get("여자", 0)

         # ✅ 성별 시사점 포함 여부 결정
        if female_pct >= 50:
            gender_directive = "▸ 성별 소비비율 차이를 중심으로 구조적 특성 해석"
        else:
            gender_directive = "▸ 성별 소비는 남성이 소폭 높은 비중을 보였으며, 이는 동반 방문 특성으로 해석 가능함 ※ 자세한 분석은 생략"

        prompt = f"""다음은 {name}({period}, {location})의 연령별 및 성별 소비현황 분석입니다.
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~기여하고 있음', '~보임')  
▸ 각 문장은 ▸ 기호로 시작하며 3~5문장으로 작성  
▸ 모든 수치는 소비금액이 아닌 소비비율(%) 기준으로 분석  
▸ 연령별 소비금액 비율 및 중장년층(50대, 60대) 혹은 청년층(20대, 30대) 집중 여부를 중심으로 분석  
▸ 성별 소비비율은 단순 수치 전달 후 해석은 생략하거나 간단한 언급에 그칠 것
▸ 상위 연령대에는 괄호로 소비비율 표기 (예: 60대(29.51%))  
▸ 부정적 표현은 지양하고, 전략적 해석을 기반으로 서술
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**
▸ 맨마지막에 → 기호를 넣고 현재까지의 시사점을 종합한 문장을 작성(ex : 이를 통해 수안보온천제 기간 소비활동이 중장년 남성 중심으로 구성된 특징이 뚜렷하게 나타난 것으로 분석)

## 주요 수치:
- 연령별 상위 3계층: {top_ages}
- 성별 소비비율: 남성 {male_pct:.2f}%, 여성 {female_pct:.2f}%
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 소비 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )

        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

