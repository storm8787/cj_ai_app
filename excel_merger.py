#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
#import openai
import os
import pandas as pd
import io
import uuid
from io import BytesIO

def excel_merger():
    st.title("📊 엑셀 취합기")
    st.info("여러 개의 엑셀(.xlsx) 파일을 업로드하고 선택한 시트와 제목행을 기준으로 병합합니다.")

    header_row = st.number_input("📌 제목행은 몇 번째 행인가요? (1부터 시작)", min_value=1, value=1, step=1)
    sheet_option = st.selectbox("📄 병합할 시트를 선택하세요", [f"{i+1}번째 시트" for i in range(10)] + ["모든 시트"])

    uploaded_files = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx"], accept_multiple_files=True)
    st.warning("⚠️ *Streamlit Cloud에서는 한글 파일명을 업로드할 경우 오류가 발생할 수 있습니다.*\n"
           "👉 업로드 전에 **파일명을 영문 또는 숫자로 변경**해 주세요.")


    if uploaded_files:
        combined_df = pd.DataFrame()

        for idx, file in enumerate(uploaded_files):
            try:
                file_bytes = file.read()
                file_io = BytesIO(file_bytes)
                file_io.seek(0)

                if sheet_option == "모든 시트":
                    xls = pd.read_excel(file_io, sheet_name=None, header=header_row - 1)
                    for sheet_df in xls.values():
                        combined_df = pd.concat([combined_df, sheet_df], ignore_index=True)
                else:
                    sheet_index = int(sheet_option.split("번째 시트")[0]) - 1
                    df = pd.read_excel(file_io, sheet_name=sheet_index, header=header_row - 1)
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

                st.success(f"✅ 파일 {idx + 1} 처리 완료")

            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

        if not combined_df.empty:
            combined_df.reset_index(drop=True, inplace=True)
            combined_df.index = combined_df.index + 1
            combined_df.index.name = "순번"

            st.dataframe(combined_df.head(30))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='통합결과')
            output.seek(0)

            st.download_button(
                label="📥 통합 엑셀 다운로드",
                data=output.getvalue(),
                file_name="통합결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

