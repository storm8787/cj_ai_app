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
from festival_analysis_app import festival_analysis_app  # ✅ 축제 분석 메인 함수 불러오기
from data_validator_app import data_validator_app
from official_merit_report_app import create_official_merit_report
from report_writer import report_writer_app

# ✅ 사이드바 메뉴 구성 (버튼 간 간격 포함)
def sidebar_menu():
    st.sidebar.title("🧰 기능 선택")

    # 기본 선택값 세팅
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = "(생성형AI) 보도자료 생성기"

    st.sidebar.markdown("### 🌟 생성형 AI 기능")
    if st.sidebar.button("📄 보도자료 생성기"):
        st.session_state.selected_app = "(생성형AI) 보도자료 생성기"
    st.sidebar.markdown(" ")

    if st.sidebar.button("📝 공적조서 생성기"):
        st.session_state.selected_app = "(생성형AI) 공적조서 생성기"
    st.sidebar.markdown(" ")

    if st.sidebar.button("📊 빅데이터 분석기"):
        st.session_state.selected_app = "(생성형AI) 빅데이터 분석기"
    st.sidebar.markdown(" ")

    if st.sidebar.button("📑 업무보고 생성기(개발중)"):
        st.session_state.selected_app = "(생성형AI) 업무보고 생성기(개발중)"
    st.sidebar.markdown(" ")

    if st.sidebar.button("🧪 공공데이터 검증기(개발중)"):
        st.session_state.selected_app = "(생성형AI) 공공데이터 검증기(개발중)"
    st.sidebar.markdown(" ")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 업무 자동화")
    if st.sidebar.button("📂 엑셀 취합기"):
        st.session_state.selected_app = "(업무자동화) 엑셀 취합기"
    st.sidebar.markdown(" ")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 관리자 모드")

    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False
    if "admin_expanded" not in st.session_state:
        st.session_state.admin_expanded = False

    with st.sidebar.expander("관리자 설정", expanded=st.session_state.admin_expanded):
        if st.session_state.admin_mode:
            st.success("✅ 관리자 모드 활성화됨")
            if st.button("🚪 관리자 모드 나가기"):
                st.session_state.admin_mode = False
                st.session_state.admin_expanded = False
                st.rerun()
        else:
            password = st.text_input("비밀번호를 입력하세요", type="password")
            if password == "wjdqh5313!":
                st.session_state.admin_mode = True
                st.session_state.admin_expanded = True
                st.rerun()
            elif password:
                st.error("❌ 비밀번호가 틀렸습니다")

        if st.session_state.admin_mode:
            if st.sidebar.button("🛠 (관리자) 빅데이터 분석기"):
                st.session_state.selected_app = "(관리자) 빅데이터 분석기"
            st.sidebar.markdown(" ")

# ✅ 메인 함수
def main():
    sidebar_menu()

    selected_app = st.session_state.selected_app

    if selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    elif selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()
    elif selected_app == "(생성형AI) 빅데이터 분석기":
        festival_analysis_app()
    elif selected_app == "(생성형AI) 공공데이터 검증기(개발중)":
        data_validator_app()
    elif selected_app == "(생성형AI) 공적조서 생성기":
        create_official_merit_report()
    elif selected_app == "(생성형AI) 업무보고 생성기(개발중)":
        report_writer_app()
    elif selected_app == "(관리자) 빅데이터 분석기":
        festival_analysis_app()  # 또는 별도 관리자용 함수

if __name__ == "__main__":
    main()


# In[ ]:




