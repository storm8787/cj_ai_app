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

    # ✅ 초기화
    for k in ["local_prev", "tourist_prev", "local_curr", "tourist_curr"]:
        if k not in st.session_state:
            st.session_state[k] = 0

    col1, col2 = st.columns(2)
    with col1:
        local_prev = st.number_input("전년도 현지인 방문객 수", min_value=0, step=100, key="local_prev")
        tourist_prev = st.number_input("전년도 외지인 방문객 수", min_value=0, step=100, key="tourist_prev")
    with col2:
        local_curr = st.number_input("올해 현지인 방문객 수", min_value=0, step=100, key="local_curr")
        tourist_curr = st.number_input("올해 외지인 방문객 수", min_value=0, step=100, key="tourist_curr")

    if st.button("🚀 분석 실행", key="total_btn"):
        # ✅ 값은 session_state에서 자동으로 관리되므로 별도 저장 필요 없음
        local_prev = st.session_state["local_prev"]
        tourist_prev = st.session_state["tourist_prev"]
        local_curr = st.session_state["local_curr"]
        tourist_curr = st.session_state["tourist_curr"]
        
        days = st.session_state.get("festival_days", 3)
        total_prev = local_prev + tourist_prev
        total_curr = local_curr + tourist_curr

        # ✅ 8번 페이지에서 사용될 요약 데이터 저장
        st.session_state["summary_total_visitors"] = total_curr
        st.session_state["summary_local_visitors"] = local_curr
        st.session_state["summary_tourist_visitors"] = tourist_curr

        # ✅ 전년도 데이터도 함께 저장
        st.session_state["summary_total_visitors_prev"] = total_prev
        st.session_state["summary_local_visitors_prev"] = local_prev
        st.session_state["summary_tourist_visitors_prev"] = tourist_prev
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

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 항목은 ▸ 기호로 구분하여 3~5문장으로 간결하게 작성
▸ 각 문장은 ▸ 기호로 시작하되, 지나치게 짧지 않도록 자연스럽게 연결하여 행정 보고서에 적합한 흐름으로 작성할 것  
▸ 주요 수치 변화(현지인/외지인/전체)의 의미를 분석  
▸ 주요 수치 변화를 표기할때 단순 관광객수 뿐 아니라 증감율을 반드시 표기할것
▸ **부정적인 평가나 비판은 피하고**, 긍정적인 요소를 중심으로 작성  
▸ 부정적인 변화가 있는 경우에도 **중립적 표현(예: ‘소폭 감소’, ‘다소 감소’) 또는 단순 수치 전달**로 처리  
▸ 필요 시 ※ 표시로 부가 설명 포함 가능
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**


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

