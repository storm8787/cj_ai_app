#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io

def analyze_internal_spending_by_region():
    st.subheader("📊 13. 외지인 도내 소비현황 분석기")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["시군구", "소비금액(원)", "소비건수(건)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 템플릿 다운로드",
        data=buffer,
        file_name="13_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 템플릿 업로드
    uploaded_file = st.file_uploader("📂 시군구별 소비현황 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ '청주시'처럼 구 단위 시는 통합
    def merge_city(row):
        if row.startswith("청주시"):
            return "청주시"
        return row.strip()

    df["시군구"] = df["시군구"].apply(merge_city)

    # ✅ 그룹화 및 총합계
    df_grouped = df.groupby("시군구", as_index=False)[["소비금액(원)", "소비건수(건)"]].sum()

    # ✅ 소비금액 기준 정렬 (숫자 상태에서 먼저 정렬)
    df_grouped = df_grouped.sort_values(by="소비금액(원)", ascending=False).reset_index(drop=True)

    # ✅ 총합 계산
    total_amount = df_grouped["소비금액(원)"].sum()
    total_count = df_grouped["소비건수(건)"].sum()

    # ✅ 비율 계산
    df_grouped["비율(%)"] = (df_grouped["소비금액(원)"] / total_amount * 100).round(2)

    # ✅ 합계 행 추가 (정렬 전 상태 유지)
    total_row = pd.DataFrame([{
        "시군구": "합계",
        "소비금액(원)": total_amount,
        "소비건수(건)": total_count,
        "비율(%)": 100.00
    }])

    # ✅ 합계 포함 후 포맷팅
    df_final = pd.concat([total_row, df_grouped], ignore_index=True)

    df_final["소비금액(원)"] = df_final["소비금액(원)"].round().astype(int).apply(lambda x: f"{x:,}")
    df_final["소비건수(건)"] = df_final["소비건수(건)"].round().astype(int).apply(lambda x: f"{x:,}")
    df_final["비율(%)"] = df_final["비율(%)"].apply(lambda x: f"{x:.2f}%")

    # ✅ 결과 출력
    st.markdown("### 🧾 도내 소비현황 요약표")
    st.dataframe(df_final, use_container_width=True)

