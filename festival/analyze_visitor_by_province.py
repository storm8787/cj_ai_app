#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io

def analyze_visitor_by_province():
    st.subheader("📊 7-1. 시도별 외지인 방문객 거주지 분석기")

    # ✅ 템플릿 생성
    template_df = pd.DataFrame(columns=["시도", "시군구", "관광객수(%)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)

    # ✅ 템플릿 다운로드 버튼
    st.download_button(
        label="📥 7-1 템플릿 다운로드",
        data=buffer,
        file_name="7-1. template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 기준 외지인 방문객 수 입력
    total_visitors = st.number_input("🔢 기준 외지인 방문객 수를 입력하세요", min_value=1, step=1)

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("📂 시도별 비율 데이터 엑셀 업로드", type=["xlsx"])
    if not uploaded_file or total_visitors <= 0:
        return

    # ✅ 데이터 읽기 및 유효성 검사
    df = pd.read_excel(uploaded_file).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]

    expected_cols = ["시도", "시군구", "관광객수(%)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ '시도', '시군구', '관광객수(%)' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 퍼센트 비율 → 숫자로 변환
    df["비율"] = df["관광객수(%)"].astype(str).str.replace("%", "").astype(float) / 100
    df["관광객수"] = (df["비율"] * total_visitors).round().astype(int)

    # ✅ 시도 기준 집계
    grouped = df.groupby("시도", as_index=False)["관광객수"].sum()
    grouped["비율"] = (grouped["관광객수"] / total_visitors * 100).round(2).astype(str) + "%"

    # ✅ 내림차순 정렬
    grouped = grouped.sort_values(by="관광객수", ascending=False).reset_index(drop=True)

    # ✅ 2열 테이블로 분할
    midpoint = len(grouped) // 2 + len(grouped) % 2
    left = grouped.iloc[:midpoint].reset_index(drop=True)
    right = grouped.iloc[midpoint:].reset_index(drop=True)
    result_df = pd.concat([left, right], axis=1)

    # ✅ 합계 행 추가 (좌우 열수 맞춰서)
    total_row = pd.DataFrame([{
        "시도": "합계",
        "관광객수": grouped["관광객수"].sum(),
        "비율": "100.00%"
    }])
    while total_row.shape[1] < result_df.shape[1]:
        total_row[f"빈열{total_row.shape[1]}"] = ""

    result_df = pd.concat([result_df, total_row], ignore_index=True)

    # ✅ 출력
    st.markdown("#### 📋 시도별 분석 결과")
    st.dataframe(result_df, use_container_width=True)

