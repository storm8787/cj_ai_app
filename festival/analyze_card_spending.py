#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd

def analyze_card_spending():
    st.subheader("💳 일자별 카드 소비 분석기")

    st.markdown("축제 기간 동안의 일자별 매출금액(천원)과 매출건수 데이터를 입력하세요.")

    # ✅ 기본값 입력
    with st.form("card_spending_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            sales_day1 = st.number_input("4월 11일 매출금액(천원)", min_value=0, value=155071)
            count_day1 = st.number_input("4월 11일 매출건수", min_value=0, value=5497)
        with col2:
            sales_day2 = st.number_input("4월 12일 매출금액(천원)", min_value=0, value=251318)
            count_day2 = st.number_input("4월 12일 매출건수", min_value=0, value=7469)
        with col3:
            sales_day3 = st.number_input("4월 13일 매출금액(천원)", min_value=0, value=157956)
            count_day3 = st.number_input("4월 13일 매출건수", min_value=0, value=5139)

        submitted = st.form_submit_button("분석 실행")

    if submitted:
        df = pd.DataFrame({
            "일자": ["4월11일(금)", "4월12일(토)", "4월13일(일)"],
            "매출금액(천원)": [sales_day1, sales_day2, sales_day3],
            "매출건수": [count_day1, count_day2, count_day3]
        })

        # 건단가 계산
        df["건단가(원)"] = (df["매출금액(천원)"] * 1000 / df["매출건수"]).round(0).astype(int)

        # 합계 및 비율
        total_sales = df["매출금액(천원)"].sum()
        total_count = df["매출건수"].sum()
        total_unit_price = int((total_sales * 1000 / total_count).round())

        df["매출금액 비율(%)"] = (df["매출금액(천원)"] / total_sales * 100).round(2)
        df["매출건수 비율(%)"] = (df["매출건수"] / total_count * 100).round(2)

        df.loc["합계"] = [
            "합계", total_sales, total_count, total_unit_price, 100.0, 100.0
        ]

        # ✅ 분석 결과 출력
        st.dataframe(df)

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            prompt = f"""다음은 {name}({period}, {location})에 대한 카드 소비 분석입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 항목은 ▸ 기호로 구분하여 3~5문장으로 간결하게 작성  
▸ 각 문장은 ▸ 기호로 시작하되, 지나치게 짧지 않도록 자연스럽게 연결하여 행정 보고서에 적합한 흐름으로 작성할 것  
▸ **일자별 매출금액 비율, 건수 비율, 건단가 차이**에 주목  
▸ **특정일 매출 집중 여부**, **평균 결제금액 추이**, **축제 소비 패턴 변화** 등을 분석  
▸ **부정적인 표현은 지양**, 변화가 있는 경우 중립적 서술(예: ‘소폭 감소’) 또는 단순 수치 전달  
▸ 필요 시 ※ 표시로 부가 설명 포함  
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**  

## 입력된 소비 지표:
- 4월 11일(금): 매출 {sales_day1:,}천원 / {count_day1:,}건 / 건단가 {df.loc[0, "건단가(원)"]:,}원
- 4월 12일(토): 매출 {sales_day2:,}천원 / {count_day2:,}건 / 건단가 {df.loc[1, "건단가(원)"]:,}원
- 4월 13일(일): 매출 {sales_day3:,}천원 / {count_day3:,}건 / 건단가 {df.loc[2, "건단가(원)"]:,}원
- 총합: 매출 {total_sales:,}천원 / {total_count:,}건 / 평균 건단가 {total_unit_price:,}원

위 정보를 바탕으로 카드 소비 시사점을 3~5문장으로 간결하게 작성해주세요.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부의 지역 축제 카드 소비 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)


