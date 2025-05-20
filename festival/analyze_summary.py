#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# ✅ OpenAI 클라이언트 초기화
client = OpenAI()

# ✅ 백데이터 로딩 함수
def load_summary_reference():
    path = os.path.join("press_release_app", "data", "insights", "1_summary.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 1번 분석기
def analyze_summary():
    st.subheader("📊 1. 축제 방문객 현황 분석")

    # ✅ 기본값 설정
    def get_value(key, default=0):
        return st.session_state.get(key, default)

    col1, col2 = st.columns(2)
    with col1:
        local_prev = st.number_input("전년도 현지인 방문객 수", min_value=0, step=100, value=get_value("local_prev"))
        tourist_prev = st.number_input("전년도 외지인 방문객 수", min_value=0, step=100, value=get_value("tourist_prev"))
    with col2:
        local_curr = st.number_input("올해 현지인 방문객 수", min_value=0, step=100, value=get_value("local_curr"))
        tourist_curr = st.number_input("올해 외지인 방문객 수", min_value=0, step=100, value=get_value("tourist_curr"))

    if st.button("🚀 분석 실행", key="total_btn"):
        days = st.session_state.get("festival_days", 3)
        total_prev = local_prev + tourist_prev
        total_curr = local_curr + tourist_curr

        # ✅ 8번 페이지에서 사용될 요약 데이터 저장
        st.session_state["summary_total_visitors"] = total_curr
        st.session_state["summary_local_visitors"] = local_curr
        st.session_state["summary_tourist_visitors"] = tourist_curr

        rows = []

        if total_prev > 0:
            row_prev = {
                "연도": "전년도 축제",
                "현지인 방문객수": f"{local_prev:,}명 (일평균: {local_prev // days:,}명)",
                "외지인 방문객수": f"{tourist_prev:,}명 (일평균: {tourist_prev // days:,}명)",
                "전체 관광객 수": f"{total_prev:,}명 (일평균: {total_prev // days:,}명)",
                "비고": f"현지인 {local_prev / total_prev:.1%}, 외지인 {tourist_prev / total_prev:.1%}"
            }
            rows.append(row_prev)

        row_curr = {
            "연도": "올해 축제",
            "현지인 방문객수": f"{local_curr:,}명 (일평균: {local_curr // days:,}명)",
            "외지인 방문객수": f"{tourist_curr:,}명 (일평균: {tourist_curr // days:,}명)",
            "전체 관광객 수": f"{total_curr:,}명 (일평균: {total_curr // days:,}명)",
            "비고": f"현지인 {local_curr / total_curr:.1%}, 외지인 {tourist_curr / total_curr:.1%}"
        }
        rows.append(row_curr)

        if total_prev > 0:
            row_diff = {
                "연도": "전년대비 증감",
                "현지인 방문객수": f"{local_curr - local_prev:+,}명 ({(local_curr - local_prev) / local_prev:.1%})",
                "외지인 방문객수": f"{tourist_curr - tourist_prev:+,}명 ({(tourist_curr - tourist_prev) / tourist_prev:.1%})",
                "전체 관광객 수": f"{total_curr - total_prev:+,}명 ({(total_curr - total_prev) / total_prev:.1%})",
                "비고": ""
            }
            rows.append(row_diff)

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")
            reference = load_summary_reference()

            prompt = f"""다음은 {name}({period}, {location})에 대한 방문객 분석입니다.

## 참고자료
{reference}

## 입력된 방문객 수:
"""
            if total_prev > 0:
                prompt += (
                    f"- 전년도: 현지인 {local_prev:,}명 / 외지인 {tourist_prev:,}명 / 전체 {total_prev:,}명\n"
                    f"- 올해: 현지인 {local_curr:,}명 / 외지인 {tourist_curr:,}명 / 전체 {total_curr:,}명\n"
                    f"- 전년대비: 현지인 {local_curr - local_prev:+,}명 / 외지인 {tourist_curr - tourist_prev:+,}명 / 전체 {total_curr - total_prev:+,}명\n"
                )
            else:
                prompt += (
                    f"- 올해: 현지인 {local_curr:,}명 / 외지인 {tourist_curr:,}명 / 전체 {total_curr:,}명\n"
                )

            prompt += "\n위 정보를 바탕으로 시사점을 3~5문장으로 간결하게 작성해주세요."

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)

