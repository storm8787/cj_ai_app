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

def main():
    st.sidebar.title("🧰 기능 선택")

    # ✅ 기본 기능 목록
    basic_features = [
        "(생성형AI) 보도자료 생성기",
        "(생성형AI) 공적조서 생성기",
        "(생성형AI) 빅데이터 분석기",
        "(생성형AI) 업무보고 생성기(개발중)",
        "(업무자동화) 엑셀 취합기",
        "(생성형AI) 공공데이터 검증기(개발중)"
    ]
    admin_features = [
        "(관리자) 빅데이터 분석기"        
    ]

    # ✅ 선택 상태 유지
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = basic_features[0]

    # ✅ 기능 선택 라디오 버튼 먼저 출력
    selected_app = st.sidebar.radio("📂 사용할 기능을 선택하세요", basic_features)
    # ✅ 라디오 아래에 줄바꿈으로 간격 추가
    st.sidebar.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    st.session_state.selected_app = selected_app

    # ✅ 아래쪽에 공간 확보
    st.sidebar.markdown("---")
    st.sidebar.markdown(" ")

    # ✅ 최초 초기화
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False
    if "admin_expanded" not in st.session_state:
        st.session_state.admin_expanded = False
    
    with st.sidebar.expander("🔐 관리자 모드", expanded=st.session_state.admin_expanded):
        if st.session_state.admin_mode:
            st.success("✅ 관리자 모드 활성화됨")
            if st.button("🚪 관리자 모드 나가기"):
                st.session_state.admin_mode = False
                st.session_state.admin_expanded = False  # ✅ 관리자 패널 접기
                st.rerun()
        else:
            password = st.text_input("비밀번호를 입력하세요", type="password")
            if password == "wjdqh5313!":
                st.session_state.admin_mode = True
                st.session_state.admin_expanded = True  # ✅ 관리자 패널 펼치기
                st.rerun()
            elif password:
                st.error("❌ 비밀번호가 틀렸습니다")

    # ✅ 관리자 모드일 경우 기능 추가 노출
    if st.session_state.get("admin_mode", False):
        selected_app = st.sidebar.radio("🛠 관리자 기능", admin_features, key="admin_feature")
        st.session_state.selected_app = selected_app

    # ✅ 기능 실행
    if st.session_state.selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    elif st.session_state.selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()
    elif st.session_state.selected_app == "(생성형AI) 빅데이터 분석기":
        festival_analysis_app()    
    elif st.session_state.selected_app == "(생성형AI) 공공데이터 검증기(개발중)":
        data_validator_app()    
    elif st.session_state.selected_app == "(생성형AI) 공적조서 생성기":        
        create_official_merit_report()
    elif st.session_state.selected_app == "(생성형AI) 업무보고 생성기(개발중)":
        report_writer_app()        

if __name__ == "__main__":
    main()


# In[ ]:




