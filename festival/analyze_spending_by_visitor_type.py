#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
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

def analyze_spending_by_visitor_type():
    st.subheader("📊 10. 방문유형별 소비현황 분석기")

    st.markdown("🎫 **8번 분석 결과에서 도출된 전체 소비금액과 건수를 입력하고, 유형별 비율을 입력하세요**")

    total_amount = st.number_input("💰 전체 소비금액 (천원)", min_value=0, step=1000, key="type_total_amount")
    total_count = st.number_input("🧾 전체 소비건수 (건)", min_value=0, step=1, key="type_total_count")

    col1, col2 = st.columns(2)
    with col1:
        local_ratio_amt = st.number_input("🏠 현지인 소비금액 비율 (%)", min_value=0.0, max_value=100.0, step=0.1)
    with col2:
        local_ratio_cnt = st.number_input("🏠 현지인 소비건수 비율 (%)", min_value=0.0, max_value=100.0, step=0.1)

    if st.button("📊 분석 실행", key="btn_type_analysis"):
        # 역산
        local_amount = int(total_amount * local_ratio_amt / 100)
        tourist_amount = total_amount - local_amount

        local_count = int(total_count * local_ratio_cnt / 100)
        tourist_count = total_count - local_count

        # 단가 계산
        local_unit = int(local_amount * 1000 / local_count) if local_count else 0
        tourist_unit = int(tourist_amount * 1000 / tourist_count) if tourist_count else 0
        total_unit = int(total_amount * 1000 / total_count) if total_count else 0

        # 비율 문자열
        local_amt_str = f"{local_amount:,}천원 ({local_ratio_amt:.2f}%)"
        tourist_amt_str = f"{tourist_amount:,}천원 ({100 - local_ratio_amt:.2f}%)"
        local_cnt_str = f"{local_count:,}건 ({local_ratio_cnt:.2f}%)"
        tourist_cnt_str = f"{tourist_count:,}건 ({100 - local_ratio_cnt:.2f}%)"

        # 출력 테이블
        df = pd.DataFrame({
            "유입유형": ["현지인", "외지인", "합계"],
            "소비금액": [local_amt_str, tourist_amt_str, f"{total_amount:,}천원 (100%)"],
            "소비건수": [local_cnt_str, tourist_cnt_str, f"{total_count:,}건 (100%)"],
            "소비단가": [f"{local_unit:,}원", f"{tourist_unit:,}원", f"{total_unit:,}원"]
        })

        st.subheader("📊 소비현황 요약표")
        st.dataframe(df.set_index("유입유형"))

        # ✅ GPT 시사점
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")

            prompt = f"""다음은 {name}({period}, {location})의 방문유형별 소비현황 분석입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~기여하고 있음', '~보임')  
▸ 각 문장은 ▸ 기호로 시작하며 3~5문장으로 작성  
▸ 현지인/외지인의 소비금액, 소비건수, 소비단가 차이를 분석  
▸ 외지인의 단가가 높다면 체류소비 및 관광효과 가능성 언급  
▸ 필요 시 ※ 표시로 부가 설명 포함  
▸ 부정적인 표현은 피하고 중립·긍정적 흐름 유지

## 입력 정보:
- 총 소비금액: {total_amount:,}천원 / 소비건수: {total_count:,}건 / 평균 소비단가: {total_unit:,}원
- 현지인: {local_amount:,}천원 / {local_count:,}건 / {local_unit:,}원
- 외지인: {tourist_amount:,}천원 / {tourist_count:,}건 / {tourist_unit:,}원

위 정보를 바탕으로 방문유형별 소비 특성을 중심으로 시사점을 작성해주세요.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 소비데이터 분석 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

