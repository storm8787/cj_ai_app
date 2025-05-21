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

# ✅ 2번 분석기
def analyze_daily_visitor():
    st.subheader("📊 2. 일자별 방문객 수 분석")

    start_date = st.session_state.get("festival_start_date")
    end_date = st.session_state.get("festival_end_date")

    if not start_date or not end_date:
        st.warning("먼저 축제 기본정보를 입력해주세요.")
        return

    date_range = pd.date_range(start=start_date, end=end_date)
    local_counts = []
    tourist_counts = []

    st.markdown("🎫 **일자별 현지인/외지인 방문객 수를 입력하세요**")
    for date in date_range:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            local = st.number_input(f"{date.strftime('%Y-%m-%d')} - 현지인", min_value=0, key=f"local_{date}")
        with col2:
            tourist = st.number_input(f"{date.strftime('%Y-%m-%d')} - 외지인", min_value=0, key=f"tourist_{date}")
        local_counts.append(local)
        tourist_counts.append(tourist)

    if st.button("🚀 분석 실행", key="daily_btn"):
        total_counts = [l + t for l, t in zip(local_counts, tourist_counts)]
        total_sum = sum(total_counts)
        local_sum = sum(local_counts)
        tourist_sum = sum(tourist_counts)

        # ✅ 8번에서 자동 활용할 수 있도록 세션에 저장
        st.session_state["summary_total_visitors"] = total_sum
        st.session_state["summary_local_visitors"] = local_sum
        st.session_state["summary_tourist_visitors"] = tourist_sum

        df = pd.DataFrame({
            "날짜": [d.strftime("%Y-%m-%d") for d in date_range],
            "현지인 방문객": local_counts,
            "외지인 방문객": tourist_counts,
            "전체 방문객": total_counts,
            #"비율(%)": [f"{(count / total_sum) * 100:.1f}%" if total_sum > 0 else "-" for count in total_counts]
        })
        
        # 비율은 숫자 그대로 유지 (계산용)
        df["전체 비율"] = df["전체 방문객"] / total_sum * 100 if total_sum > 0 else 0
        df["현지인 비율"] = df["현지인 방문객"] / local_sum * 100 if local_sum > 0 else 0
        df["외지인 비율"] = df["외지인 방문객"] / tourist_sum * 100 if tourist_sum > 0 else 0

        # 표시용만 따로 문자열 변환
        df["전체 비율(%)"] = df["전체 비율"].map(lambda x: f"{x:.2f}%" if total_sum > 0 else "-")
        df["현지인 비율(%)"] = df["현지인 비율"].map(lambda x: f"{x:.2f}%" if local_sum > 0 else "-")
        df["외지인 비율(%)"] = df["외지인 비율"].map(lambda x: f"{x:.2f}%" if tourist_sum > 0 else "-")


        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown(f"""
        ✅ 총 방문객: **{total_sum:,}명**
        - 현지인: {local_sum:,}명 ({local_sum / total_sum:.1%})
        - 외지인: {tourist_sum:,}명 ({tourist_sum / total_sum:.1%})
        """)

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")
            reference = load_daily_reference()

            # ✅ 비율 포함된 daily_summary 생성
            daily_summary = "\n".join([
                f"- {row['날짜']}: 현지인 {row['현지인 방문객']:,}명 ({row['현지인 비율']:.1f}%) / "
                f"외지인 {row['외지인 방문객']:,}명 ({row['외지인 비율']:.1f}%) / "
                f"전체 {row['전체 방문객']:,}명 ({row['전체 비율']:.1f}%)"
                for _, row in df.iterrows()
            ])
            
            prompt = f"""다음은 {name}({period}, {location}) 축제의 일자별 방문객 분석 자료입니다. 아래 정보를 바탕으로 공공기관 보고서에 포함할 '시사점'을 작성해주세요.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 항목은 ▸ 기호로 구분하여 3~5문장으로 간결하게 작성
▸ 각 문장은 ▸ 기호로 시작하되, 지나치게 짧지 않도록 자연스럽게 연결하여 행정 보고서에 적합한 흐름으로 작성할 것  
▸ 각 날짜별 방문객 수 및 전체/현지인/외지인 비율 변화를 기반으로 특징적인 패턴이나 의미를 도출할 것  
▸ 수치는 괄호 안에 %와 함께 병기하여 서술할 것 (예: '6월 12일은 전체 방문객 수(30.2%)가 가장 높았으며')  
▸ 부정적인 평가는 피하고, 긍정적 해석을 중심으로 작성하며 단순 수치는 중립적으로 전달  
▸ 필요 시 ※ 표시로 보충 설명 가능
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**

## 일자별 방문객 수 요약:
{daily_summary}

위 내용을 바탕으로 시사점을 작성해주세요.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 충주시 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=700
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

