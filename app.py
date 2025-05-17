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
from calendar_app import calendar_app

def main():
    st.sidebar.title("🧰 기능 선택")

    # ✅ 선택한 기능을 세션에 저장해서 로그인 후에도 유지
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = "(생성형AI) 보도자료 생성기"  # 기본값 (또는 보도자료 생성기)

    # ✅ 선택 상태 유지되는 라디오 버튼
    selected_app = st.sidebar.radio(
        "아래 기능 중 선택하세요", 
        [
            "(생성형AI) 보도자료 생성기",
            #"(업무자동화) 구글 일정등록",
            "(업무자동화) 엑셀 취합기"
        ],
        index=["(생성형AI) 보도자료 생성기", "(업무자동화) 구글 일정등록", "(업무자동화) 엑셀 취합기"].index(
            st.session_state.selected_app
        )
    )

    # ✅ 현재 선택 저장
    st.session_state.selected_app = selected_app

    # ✅ 기능 실행
    if selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    #elif selected_app == "(업무자동화) 구글 일정등록":
        #calendar_app()
    elif selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()        

if __name__ == "__main__":
    main()

