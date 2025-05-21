#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ✅ Streamlit용 메타 사전 기반 정밀 검증기 구조

import streamlit as st
import pandas as pd
import json
import re
from io import BytesIO
import chardet
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os

# ✅ 메타 사전 불러오기
def load_meta_dict(standard):
    path = os.path.join("meta_dicts_final_clean", f"{standard}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# ✅ 셀 검증 함수
def validate_cell(val, col, meta, row_data):
    errors = []
    val = str(val).strip()
    meta_col = meta.get(col)
    if not meta_col:
        return errors

    # 필수 여부 확인
    required = meta_col.get("필수여부") == "필수"
    조건부 = meta_col.get("조건부필수")

    if val in ["", "nan", "NaN"]:
        if required:
            errors.append("필수값 누락")
        elif 조건부:
            기준필드, 기준값들 = list(조건부.items())[0]
            기준값 = row_data.get(기준필드, "").strip()
            if 기준값 in 기준값들:
                errors.append("조건부 필수 누락")
        return errors

    # 허용값 체크
    allowed = meta_col.get("허용값")
    if allowed and val not in allowed:
        errors.append("허용값 오류")

    # 정규식 체크
    regex = meta_col.get("정규식")
    if regex and not re.fullmatch(regex, val):
        errors.append("형식 오류")

    return errors

# ✅ 검증 실행 함수
def run_meta_validation(df, meta):
    error_cells = []
    for i, row in df.iterrows():
        for col in df.columns:
            val = row[col]
            row_data = row.to_dict()
            errs = validate_cell(val, col, meta, row_data)
            if errs:
                error_cells.append((i+2, col, ", ".join(errs)))
    return error_cells

# ✅ 엑셀 오류 셀 표시

def generate_excel_with_errors(df, error_cells):
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    wb = load_workbook(output)
    ws = wb.active
    yellow = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    col_idx = {col: i+1 for i, col in enumerate(df.columns)}
    for row, col, _ in error_cells:
        ws.cell(row=row, column=col_idx[col]).fill = yellow
    final_output = BytesIO()
    wb.save(final_output)
    final_output.seek(0)
    return final_output

# ✅ Streamlit 앱

def data_validator_app():
    st.title("📑 공공데이터 정밀 검증기 (Meta 기반)")

    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])
    standard = st.selectbox("검증 기준 표준을 선택하세요", options=[f.replace(".json", "") for f in os.listdir("meta_dicts_final_clean") if f.endswith(".json")])

    if uploaded_file and standard:
        try:
            raw_bytes = uploaded_file.read()
            encoding = chardet.detect(raw_bytes)['encoding'] or 'utf-8'
            df = pd.read_csv(BytesIO(raw_bytes), encoding=encoding, dtype=str).fillna("")
            st.success(f"✅ 파일 업로드 성공 (인코딩: {encoding})")

            meta = load_meta_dict(standard)
            if not meta:
                st.error("❌ 메타 정보를 불러올 수 없습니다.")
                return

            if st.button("🔍 정밀 검증 실행"):
                error_cells = run_meta_validation(df, meta)
                st.subheader("📋 검증 결과 미리보기")

                preview_df = df.copy()
                for row, col, msg in error_cells:
                    preview_df.at[row - 2, col] += f" ⚠️ ({msg})"

                st.dataframe(preview_df, use_container_width=True)

                excel_with_errors = generate_excel_with_errors(df, error_cells)
                st.download_button(
                    label="📥 오류 표시된 엑셀 다운로드",
                    data=excel_with_errors.getvalue(),
                    file_name="검증결과_정밀표시.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"파일 처리 오류: {e}")

