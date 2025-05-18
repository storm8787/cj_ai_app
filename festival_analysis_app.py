#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from io import BytesIO

def bigdata_analyzer_app():
    st.title("📊 축제 빅데이터 분석기")
    st.info("축제 방문객 데이터를 업로드하면, 자동으로 현지인/외지인 구분과 증감률 등을 분석합니다.")

    uploaded_file = st.file_uploader("🎯 분석할 엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        st.subheader("1️⃣ 주요 컬럼 지정")
        date_col = st.selectbox("📅 날짜 컬럼", df.columns)
        visitor_type_col = st.selectbox("👥 방문객 구분 컬럼", df.columns)  # 예: '현지인', '외지인'
        count_col = st.selectbox("📌 방문객 수 컬럼", df.columns)

        if st.button("🚀 분석 실행"):
            try:
                grouped = df.groupby([date_col, visitor_type_col])[count_col].sum().unstack().fillna(0)
                grouped["전체"] = grouped.sum(axis=1)
                grouped["전일 대비 증감률(%)"] = grouped["전체"].pct_change().fillna(0) * 100
                grouped = grouped.round(2)

                st.success("✅ 분석 완료")
                st.dataframe(grouped)

                # 엑셀로 다운로드
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    grouped.to_excel(writer, sheet_name="분석결과")
                output.seek(0)

                st.download_button(
                    label="📥 분석결과 다운로드",
                    data=output,
                    file_name="축제_분석결과.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"❌ 분석 중 오류 발생: {e}")

