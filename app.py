#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st

st.set_page_config(
    page_title="더 가까이, 충주시 AI 연구",
    page_icon="logo.png",
    layout="wide"
)

from press_release_app import press_release_app
from excel_merger import excel_merger

def main():
    st.sidebar.title("🧰 기능 선택")
    selected_app = st.sidebar.radio("아래 기능 중 선택하세요", [
        "(생성형AI) 보도자료 생성기",
        "(업무자동화) 일정등록",
        "(업무자동화) 엑셀 취합기"
    ])

    if selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    elif selected_app == "(업무자동화) 일정등록":
        calendar_app()
    elif selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()        

if __name__ == "__main__":
    main()

