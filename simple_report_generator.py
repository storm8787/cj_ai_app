#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from openai import OpenAI
import io

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🚀 앱 제목
st.header("📈 간단 통계 보고서 생성기")

# 1. 분석 유형 선택
analysis_type = st.selectbox(
    "🔍 분석 유형을 선택하세요",
    ["단순 분석", "시계열 분석", "지역별 분석", "계층별 분석"]
)

# 2. 제목 및 분석 방향 입력
title = st.text_input("📌 분석 제목을 입력하세요", placeholder="예: 2025년 충주시 세대별 인구현황")
direction = st.text_area("🧭 분석 방향을 입력하세요 (선택)", placeholder="예: 세대별 구성 특징 및 고령층 비율 중심")

# 3. 파일 업로드
uploaded_files = []
if analysis_type == "시계열 분석":
    st.markdown("📁 시계열 분석은 연도별 데이터 비교를 위해 최대 2개의 엑셀 파일 업로드를 권장합니다.")
    uploaded_files = st.file_uploader("📤 엑셀 파일을 업로드하세요", accept_multiple_files=True, type=["xlsx"])
else:
    file = st.file_uploader("📤 분석에 사용할 엑셀 파일을 업로드하세요", type=["xlsx"])
    if file:
        uploaded_files = [file]

# 4. GPT 분석 실행 버튼
if uploaded_files and title and st.button("🧠 GPT 분석 시작"):
    dfs = []
    for uploaded_file in uploaded_files:
        df = pd.read_excel(uploaded_file)
        dfs.append(df)

    # ✅ 분석 표 텍스트 생성
    table_text = ""
    for i, df in enumerate(dfs):
        table_text += f"\n\n📄 [표{i+1}] 미리보기:\n"
        table_text += df.head(10).to_markdown(index=False)

    # ✅ 분석 방향 기본값 보완
    if not direction:
        direction = f"{analysis_type} 관점에서 {title} 데이터를 중심으로 분석"

    # ✅ GPT 프롬프트
    prompt = f"""
📊 제목: {title}

다음 표는 공공데이터 기반 행정분석 보고서 초안입니다.  
문서는 항목 중심으로 구성하며, 전체 문장은 행정문서체 및 개괄식 종결형으로 작성할 것.  
분석 유형: {analysis_type}  
분석 방향: {direction}  

📌 데이터 표는 다음과 같습니다.
{table_text}
"""

    with st.spinner("GPT가 보고서를 생성 중입니다..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        st.subheader("📝 GPT 분석 요약 결과")
        st.write(response.choices[0].message.content)

    # ✅ 시각화 미리보기
    st.subheader("📊 데이터 시각화 미리보기")
    for i, df in enumerate(dfs):
        st.markdown(f"✅ [표{i+1}]")
        st.dataframe(df)

