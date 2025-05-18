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

    # ✅ 관리자 모드 인증
    admin_mode = False
    if st.sidebar.checkbox("🔐 관리자 모드"):
        password = st.sidebar.text_input("비밀번호를 입력하세요", type="password")
        if password == "wjdqh5313!":  # ✅ 비밀번호 설정
            st.sidebar.success("✅ 관리자 모드 활성화됨")
            admin_mode = True
        else:
            if password:  # 비밀번호 입력했는데 틀린 경우
                st.sidebar.error("❌ 비밀번호가 틀렸습니다")
    # ✅ 선택한 기능을 세션에 저장해서 로그인 후에도 유지
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = "(생성형AI) 보도자료 생성기"  # 기본값 (또는 보도자료 생성기)

     # ✅ 선택된 기능 상태 기억
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = "(생성형AI) 보도자료 생성기"

    # ✅ 기능 목록 구성
    basic_features = [
        "(생성형AI) 보도자료 생성기",
        "(업무자동화) 엑셀 취합기"
    ]
    admin_features = [
        "(관리자) 테스트 페이지",
        "(관리자) 데이터 초기화"
    ]

    all_features = basic_features + admin_features if admin_mode else basic_features

    # ✅ 사이드바에서 기능 선택
    selected_app = st.sidebar.radio("🛠 기능을 선택하세요", all_features, index=0)
    st.session_state.selected_app = selected_app

    # ✅ 기능 실행
    if selected_app == "(생성형AI) 보도자료 생성기":
        press_release_app()
    elif selected_app == "(업무자동화) 엑셀 취합기":
        excel_merger()
    elif selected_app == "(관리자) 테스트 페이지" and admin_mode:
        st.title("👨‍💻 관리자용 테스트 페이지")
        st.write("관리자 전용 기능입니다.")
    elif selected_app == "(관리자) 데이터 초기화" and admin_mode:
        st.title("🗑 데이터 초기화")
        st.warning("이 기능은 관리자만 사용할 수 있습니다.")

if __name__ == "__main__":
    main()

