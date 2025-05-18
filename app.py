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

    # ✅ 기본 기능 목록
    basic_features = [
        "(생성형AI) 보도자료 생성기",
        "(업무자동화) 엑셀 취합기"
    ]
    admin_features = [
        "(관리자) 테스트 페이지",
        "(관리자) 데이터 초기화"
    ]

    # ✅ 선택 상태 유지
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = basic_features[0]

    # ✅ 기능 선택 라디오 버튼 먼저 출력
    selected_app = st.sidebar.radio("📂 사용할 기능을 선택하세요", basic_features)
    st.session_state.selected_app = selected_app

    # ✅ 아래쪽에 공간 확보
    st.sidebar.markdown("---")
    st.sidebar.markdown(" ")

    # ✅ 관리자 모드 UI는 맨 아래에 배치
    with st.sidebar.expander("🔐 관리자 모드", expanded=False):
        password = st.text_input("비밀번호를 입력하세요", type="password", key="admin_pw")
        if password == "cjadmin123":
            st.session_state.admin_mode = True
            st.success("✅ 관리자 모드 활성화됨")
        elif password:
            st.session_state.admin_mode = False
            st.error("❌ 비밀번호가 틀렸습니다")
        else:
            st.session_state.admin_mode = False

    # ✅ 관리자 모드일 경우 기능 추가 노출
    if st.session_state.get("admin_mode", False):
        selected_app = st.sidebar.radio("🛠 관리자 기능", admin_features, key="admin_feature")
        st.session_state.selected_app = selected_app

    # ✅ 기능 실행
    if st.session_state.selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    elif st.session_state.selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()
    elif st.session_state.selected_app == "(관리자) 테스트 페이지":
        st.title("👨‍💻 관리자용 테스트 페이지")
        st.write("관리자 전용 기능입니다.")
    elif st.session_state.selected_app == "(관리자) 데이터 초기화":
        st.title("🗑 데이터 초기화")
        st.warning("이 기능은 관리자만 사용할 수 있습니다.")

if __name__ == "__main__":
    main()

