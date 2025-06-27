#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st

# ✅ 페이지 설정
st.set_page_config(
    page_title="더 가까이, 충주시 AI 연구",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ 기능 모듈 import
from press_release_app import press_release_app
from excel_merger import excel_merger
from festival_analysis_app import festival_analysis_app
from data_validator_app import data_validator_app
from official_merit_report_app import create_official_merit_report
from report_writer import report_writer_app
from address_geocoder import run_geocoding_tool
from kakao_promo_app import generate_kakao_promo
from main_dashboard import run as main_dashboard_run  # ✅ 메인페이지 모듈 추가
from simple_report_generator import simple_report_generator

def main():
    st.sidebar.title("🧰 기능 선택")

    # ✅ 기본 기능 목록 (메인페이지 항목 추가됨)
    basic_features = [
        "🏠 충주시 AI 연구",
        "(생성형AI) 보도자료 생성기",
        "(생성형AI) 공적조서 생성기",
        "(생성형AI) 빅데이터 분석기",
        "(생성형AI) 카카오톡 홍보멘트 생성기",
        "(생성형AI) 업무보고 생성기",
        "(생성형AI) 간단통계 보고서 생성기",
        "(업무자동화) 엑셀 취합기",
        "(업무지원) 주소-좌표 변환기",        
        "(생성형AI) 공공데이터 검증기(개발중)"
    ]
    admin_features = [
        "(관리자) 빅데이터 분석기"
    ]

    # ✅ 초기 선택 상태 유지 (기본값: 메인페이지)
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = basic_features[0]

    selected_app = st.sidebar.radio("📂 사용할 기능을 선택하세요", basic_features)
    st.session_state.selected_app = selected_app

    st.sidebar.markdown("---")
    st.sidebar.markdown(" ")

    # ✅ 관리자 모드 상태 초기화
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False
    if "admin_expanded" not in st.session_state:
        st.session_state.admin_expanded = False

    with st.sidebar.expander("🔐 관리자 모드", expanded=st.session_state.admin_expanded):
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

    # ✅ 관리자 기능 선택
    if st.session_state.get("admin_mode", False):
        selected_app = st.sidebar.radio("🛠 관리자 기능", admin_features, key="admin_feature")
        st.session_state.selected_app = selected_app

    # ✅ 기능 실행 분기
    if st.session_state.selected_app == "🏠 충주시 AI 연구":
        main_dashboard_run()
    elif st.session_state.selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    elif st.session_state.selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()
    elif st.session_state.selected_app == "(생성형AI) 빅데이터 분석기":
        festival_analysis_app()
    elif st.session_state.selected_app == "(생성형AI) 공공데이터 검증기(개발중)":
        data_validator_app()
    elif st.session_state.selected_app == "(생성형AI) 공적조서 생성기":
        create_official_merit_report()
    elif st.session_state.selected_app == "(생성형AI) 업무보고 생성기":
        report_writer_app()
    elif st.session_state.selected_app == "(업무지원) 주소-좌표 변환기":
        run_geocoding_tool()
    elif st.session_state.selected_app == "(생성형AI) 카카오톡 홍보멘트 생성기":
        generate_kakao_promo()
    elif st.session_state.selected_app == "(생성형AI) 간단통계 보고서 생성기":
        simple_report_generator()

if __name__ == "__main__":
    main()


# In[ ]:




