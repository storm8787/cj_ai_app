#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_external_visitor_spending_in_chungju():
    st.subheader("📊 14. 축제방문 외지인의 충주 관내 소비현황")
    st.markdown("엑셀 파일을 업로드하여 외지인의 행정동별 소비 현황을 분석하세요.")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["읍면동", "소비금액(원)", "소비건수(건)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 템플릿 다운로드",
        data=buffer,
        file_name="14_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("📂 행정동별 소비현황 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    # ✅ 데이터 로드 및 처리
    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ 정제
    df["읍면동"] = df["읍면동"].astype(str).str.strip()
    df["소비금액(원)"] = df["소비금액(원)"].astype(int)
    df["소비건수(건)"] = df["소비건수(건)"].astype(int)

    # ✅ 합계 계산
    total_amount = df["소비금액(원)"].sum()
    total_count = df["소비건수(건)"].sum()

    # ✅ 비율 계산
    df["소비비율"] = (df["소비금액(원)"] / total_amount * 100).round(2)

    # ✅ 합계 행 추가
    total_row = pd.DataFrame([{
        "읍면동": "합계",
        "소비금액(원)": total_amount,
        "소비건수(건)": total_count,
        "소비비율": 100.00
    }])

    df_final = pd.concat([total_row, df], ignore_index=True)

    # ✅ 포맷팅
    df_final["소비금액(원)"] = df_final["소비금액(원)"].apply(lambda x: f"{x:,}원")
    df_final["소비건수(건)"] = df_final["소비건수(건)"].apply(lambda x: f"{x:,}건")
    df_final["소비비율"] = df_final["소비비율"].apply(lambda x: f"{x:.2f}%")

    # ✅ 출력
    st.markdown("### 🧾 외지인 충주 관내 소비현황 요약표")
    st.dataframe(df_final, use_container_width=True)

