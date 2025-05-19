#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 백데이터 로딩 함수
def load_insight_examples(section_id):
    try:
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 4번 분석기: 전·중·후 방문객 분석
def analyze_before_after():
    st.subheader("📊 4. 축제 전·중·후 방문객 분석")

    st.markdown("**축제 전 5일, 축제기간 3일, 축제 후 5일 방문객 수를 구분하여 입력해주세요.**")

    col1, col2, col3 = st.columns(3)
    with col1:
        local_before = st.number_input("현지인 - 축제 전", min_value=0, step=100)
        tourist_before = st.number_input("외지인 - 축제 전", min_value=0, step=100)
    with col2:
        local_during = st.number_input("현지인 - 축제기간", min_value=0, step=100)
        tourist_during = st.number_input("외지인 - 축제기간", min_value=0, step=100)
    with col3:
        local_after = st.number_input("현지인 - 축제 후", min_value=0, step=100)
        tourist_after = st.number_input("외지인 - 축제 후", min_value=0, step=100)

    if st.button("🚀 분석 실행", key="before_after_btn"):
        # 합계
        total_before = local_before + tourist_before
        total_during = local_during + tourist_during
        total_after = local_after + tourist_after

        # 증가율 계산
        inc_local = f"{(local_during - local_before) / local_before:.1%}" if local_before > 0 else "-"
        inc_tourist = f"{(tourist_during - tourist_before) / tourist_before:.1%}" if tourist_before > 0 else "-"
        inc_total = f"{(total_during - total_before) / total_before:.1%}" if total_before > 0 else "-"

        # 표 생성
        df = pd.DataFrame([
            ["현지인", f"{local_before:,}명", f"{local_during:,}명", inc_local, f"{local_after:,}명"],
            ["외지인", f"{tourist_before:,}명", f"{tourist_during:,}명", inc_tourist, f"{tourist_after:,}명"],
            ["합 계", f"{total_before:,}명", f"{total_during:,}명", inc_total, f"{total_after:,}명"]
        ], columns=["구분", "축제 전 (5일)", "축제기간 (3일)", "증감률", "축제 후 (5일)"])

        st.dataframe(df, use_container_width=True)

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")
            reference = load_insight_examples("4_before_after")

            prompt = f"""
다음은 {name}({period}, {location}) 축제에 대한 전·중·후 방문객 분석입니다.

[입력값 요약]
- 축제 전 (5일) 방문객: 현지인 {local_before:,}명 / 외지인 {tourist_before:,}명 / 합계 {total_before:,}명
- 축제기간 (3일): 현지인 {local_during:,}명 / 외지인 {tourist_during:,}명 / 합계 {total_during:,}명
- 축제 후 (5일): 현지인 {local_after:,}명 / 외지인 {tourist_after:,}명 / 합계 {total_after:,}명

[전 대비 축제기간 증감률]
- 현지인: {inc_local}, 외지인: {inc_tourist}, 전체: {inc_total}

[참고자료]
{reference}

위 데이터를 바탕으로, 전·중·후 방문객 패턴의 특징 및 해석 가능한 시사점을 행정 보고서 스타일로 3~5문장으로 작성해주세요.
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

