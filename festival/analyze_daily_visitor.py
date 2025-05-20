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
            "비율(%)": [f"{(count / total_sum) * 100:.1f}%" if total_sum > 0 else "-" for count in total_counts]
        })

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

            daily_summary = "\n".join([
                f"- {row['날짜']}: 현지인 {row['현지인 방문객']:,}명 / 외지인 {row['외지인 방문객']:,}명 / 전체 {row['전체 방문객']:,}명"
                for _, row in df.iterrows()
            ])

            prompt = f"""다음은 {name}({period}, {location}) 축제의 일자별 방문객 분석입니다.

## 참고자료
{reference}

## 일자별 방문객 수 요약
{daily_summary}

이 데이터를 기반으로, 방문 패턴이나 특이사항을 포함하여 시사점을 3~5문장으로 간결하게 작성해주세요.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=700
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

