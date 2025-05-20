#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import re
import unicodedata
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# === 정규식 추론 함수 ===
def infer_regex(expression, column_name=None):
    expr = str(expression).lower()
    col = str(column_name).lower() if column_name else ""
    if "전화번호" in expr or "연락처" in col:
        return r"^(?!010$)(0[2-9][2-9]?[0-9]?)-\d{3,4}-\d{4}$"
    elif "일자" in col or "날짜" in col:
        return r"^\d{4}[-\.]\d{2}[-\.]\d{2}$"
    elif "이메일" in expr or "email" in expr:
        return r"^[\w\.-]+@[\w\.-]+\.\w+$"
    elif "숫자" in expr or "정수" in expr or col.endswith("수"):
        return r"^\d+$"
    elif "소수" in expr:
        return r"^-?\d+\.\d+$"
    return None

# === 특수문자 포함 여부 확인 함수 ===
def contains_forbidden_chars(val_str, col):
    col_lower = col.lower()
    forbidden = [",", "'", '"', ";", "?"]
    return any(c in val_str for c in forbidden)

# === 셀 유효성 검사 함수 ===
def validate_cell(val_str, col, regex):
    errors = []
    val_str = unicodedata.normalize('NFC', val_str.strip())
    if regex and not re.fullmatch(regex, val_str):
        errors.append("형식 오류")
    if contains_forbidden_chars(val_str, col):
        errors.append("특수문자 포함")
    return errors

# === 검증 실행 함수 ===
def run_validation(df):
    error_cells = []
    for col in df.columns:
        regex = infer_regex(col, col)
        for i, val in enumerate(df[col]):
            val_str = str(val).strip()
            if val_str not in ["", "nan", "NaN"]:
                cell_errors = validate_cell(val_str, col, regex)
                if cell_errors:
                    error_cells.append((i + 2, col))  # Excel은 2행부터 시작
    return error_cells

# === 오류 표시된 엑셀 생성 함수 ===
def generate_excel_with_errors(df, error_cells):
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    wb = load_workbook(output)
    ws = wb.active
    yellow = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    col_idx = {col: i + 1 for i, col in enumerate(df.columns)}
    for row, col in error_cells:
        ws.cell(row=row, column=col_idx[col]).fill = yellow
    final_output = BytesIO()
    wb.save(final_output)
    final_output.seek(0)
    return final_output

st.title("📑 공공데이터 표준 간이 검증기 (CSV 전용)")

uploaded_file = st.file_uploader("✅ CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8", dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="cp949", dtype=str)

    df.fillna("", inplace=True)
    st.success("✅ 파일 업로드 성공")

    if st.button("🔍 검증 실행"):
        error_cells = run_validation(df)
        st.subheader("📋 검증 결과 미리보기")

        if error_cells:
            preview_df = df.copy()
            for row, col in error_cells:
                preview_df.at[row - 2, col] += " ⚠️"

            st.dataframe(preview_df, use_container_width=True)

            excel_with_errors = generate_excel_with_errors(df, error_cells)
            st.download_button(
                label="📥 오류 표시된 엑셀 다운로드",
                data=excel_with_errors.getvalue(),
                file_name="검증결과_노란색표시.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.success("🎉 형식 오류나 특수문자 문제 없이 정상입니다!")
else:
    st.info("좌측 또는 위에서 CSV 파일을 업로드해주세요.")

