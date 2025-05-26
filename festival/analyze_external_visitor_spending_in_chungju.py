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
    st.markdown("📂 업로드된 엑셀 파일의 '읍면동, 소비금액(원), 소비건수(건)' 컬럼을 기준으로 분석합니다.")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["읍면동", "소비금액(원)", "소비건수(건)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 14_template.xlsx 다운로드",
        data=buffer,
        file_name="14_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    # ✅ 데이터 로딩
    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ 숫자 정리
    df["소비금액(원)"] = df["소비금액(원)"].astype(float)
    df["소비건수(건)"] = df["소비건수(건)"].astype(int)

    # ✅ 합계 행 계산
    total_row = pd.DataFrame([{
        "읍면동": "합계",
        "소비금액(원)": df["소비금액(원)"].sum(),
        "소비건수(건)": df["소비건수(건)"].sum()
    }])

    # ✅ 합계 포함 데이터 재구성
    df = pd.concat([total_row, df], ignore_index=True)

    # ✅ 소비비율 계산
    total_amount = total_row["소비금액(원)"].values[0]
    df["소비비율"] = (df["소비금액(원)"] / total_amount * 100).round(2)
    df.loc[0, "소비비율"] = 100.00  # 합계는 무조건 100%

    # ✅ 읍면동 순서 강제 지정
    order = [
        "합계", "주덕읍", "살미면", "수안보면", "대소원면", "신니면", "노은면", "앙성면",
        "중앙탑면", "금가면", "동량면", "산척면", "엄정면", "소태면", "성내·충인동",
        "교현·안림동", "교현2동", "용산동", "지현동", "문화동", "호암·직동",
        "달천동", "봉방동", "칠금·금릉동", "연수동", "목행·용탄동"
    ]
    df["읍면동"] = pd.Categorical(df["읍면동"], categories=order, ordered=True)
    df = df.sort_values("읍면동").reset_index(drop=True)

    # ✅ 포맷팅
    df["소비금액(원)"] = df["소비금액(원)"].round().astype(int).apply(lambda x: f"{x:,}원")
    df["소비건수(건)"] = df["소비건수(건)"].astype(int).apply(lambda x: f"{x:,}건")
    df["소비비율"] = df["소비비율"].apply(lambda x: f"{x:.2f}%")

    # ✅ 출력
    st.markdown("### 🧾 읍면동별 소비현황")
    st.dataframe(df, use_container_width=True)

