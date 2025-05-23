#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI()

# ✅ 백데이터 로딩
def load_daily_reference():
    path = os.path.join("press_release_app", "data", "insights", "2_daily.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def analyze_card_spending():
    st.subheader("📊 6. 일자별 카드 소비 분석기")

    # ✅ 기본 정보
    start_date = st.session_state.get("festival_start_date")
    end_date = st.session_state.get("festival_end_date")

    if not start_date or not end_date:
        st.warning("먼저 축제 기본정보를 입력해주세요.")
        return

    date_range = pd.date_range(start=start_date, end=end_date)
    date_strs = [d.strftime("%Y-%m-%d") for d in date_range]

    # ✅ 입력부
    st.markdown("🎫 **축제 기간 동안 일자별 매출금액(천원)과 매출건수를 입력하세요**")

    sales_inputs = {}
    count_inputs = {}

    for d_str in date_strs:
        col1, col2 = st.columns(2)
        with col1:
            sales = st.number_input(f"{d_str} 매출금액 (천원)", min_value=0, key=f"{d_str}_sales")
        with col2:
            count = st.number_input(f"{d_str} 매출건수", min_value=0, key=f"{d_str}_count")
        sales_inputs[d_str] = sales
        count_inputs[d_str] = count

    if st.button("📊 분석 실행"):
        # ✅ 결과 계산
        sales_list = [sales_inputs[d] for d in date_strs]
        count_list = [count_inputs[d] for d in date_strs]
        unit_price_list = [
            int(sales_inputs[d] * 1000 / count_inputs[d]) if count_inputs[d] > 0 else 0
            for d in date_strs
        ]

        total_sales = sum(sales_list)
        total_count = sum(count_list)
        total_unit_price = int(total_sales * 1000 / total_count) if total_count > 0 else 0

        # ✅ 결과 표 구성
        df_t = pd.DataFrame({
            "구분": ["매출금액", "매출건수", "건단가"]
        })
        for i, d in enumerate(date_strs):
            df_t[d] = [sales_list[i], count_list[i], unit_price_list[i]]
        df_t["합계"] = [total_sales, total_count, total_unit_price]

        st.subheader("📊 결과 테이블")
        st.dataframe(df_t.set_index("구분"))

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            spending_summary = ""
            for i, d_str in enumerate(date_strs):
                spending_summary += f"- {d_str}: 매출 {sales_list[i]:,}천원 / {count_list[i]:,}건 / 건단가 {unit_price_list[i]:,}원\n"
            spending_summary += f"- 총합: 매출 {total_sales:,}천원 / {total_count:,}건 / 평균 건단가 {total_unit_price:,}원"

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
{spending_summary}

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

