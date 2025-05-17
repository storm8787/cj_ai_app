#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
import json

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def build_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": st.secrets["GOOGLE_CLIENT_ID"],
                "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri="https://pressreleaseapp-4fkk9ezm2byjmcj7ltkgzc.streamlit.app/"  # 배포 시 수정 필요
    )

def create_event(creds, title, location, description, start_dt, end_dt):
    service = build("calendar", "v3", credentials=creds)
    event = {
        'summary': title,
        'location': location,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Seoul'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Seoul'},
    }
    event_result = service.events().insert(calendarId='primary', body=event).execute()
    return event_result.get("htmlLink")

def calendar_app():
    st.title("📅 일정 등록기 (구글 캘린더)")

    creds = None

   
    if "code" in st.query_params:
        code = st.query_params.get("code")
        st.write("🔐 code:", code)
        st.write("📎 redirect_uri:", build_flow().redirect_uri)
        st.write("📌 client_id:", st.secrets["GOOGLE_CLIENT_ID"][:10] + "...")

        flow = build_flow()
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state["creds"] = creds.to_json()
            st.success("✅ 로그인 성공!")

            # ✅ 로그인 성공 후 다시 돌아갈 기능 기억해둔 곳으로 이동
            if "return_to" in st.session_state:
                st.session_state.selected_app = st.session_state["return_to"]
                del st.session_state["return_to"]

            st.rerun()
        except Exception as e:
            st.error("❌ 로그인 실패. 다시 로그인해 주세요.")
            st.session_state.clear()
            st.stop()

    elif "creds" in st.session_state:
        creds = Credentials.from_authorized_user_info(json.loads(st.session_state["creds"]), SCOPES)

    else:
        flow = build_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')

        # ✅ 현재 기능 위치 기억
        st.session_state["return_to"] = "(업무자동화) 구글 일정등록"

        # ✅ 로그인 버튼 (같은 탭 이동)
        st.markdown(
            f'''
            <a href="{auth_url}" target="_self">
                <button style="font-size:18px;padding:10px 20px;">🔐 구글 계정으로 로그인하기</button>
            </a>
            ''',
            unsafe_allow_html=True
        )

        st.stop()

    with st.form("calendar_form"):
        title = st.text_input("일정 제목", "충주시 간담회")
        location = st.text_input("장소", "충주시청 상황실")
        description = st.text_area("설명", "정책 논의 간담회입니다.")
        date = st.date_input("날짜", datetime.date.today())
        start_time = st.time_input("시작 시간", datetime.time(10, 0))
        end_time = st.time_input("종료 시간", datetime.time(11, 0))
        submitted = st.form_submit_button("📌 내 캘린더에 등록하기")

        if submitted:
            start_dt = datetime.datetime.combine(date, start_time)
            end_dt = datetime.datetime.combine(date, end_time)
            try:
                url = create_event(creds, title, location, description, start_dt, end_dt)
                st.success("✅ 등록 완료! 아래 링크에서 확인 가능:")
                st.markdown(f"[📅 일정 확인하기]({url})")
            except Exception as e:
                st.error(f"❌ 오류 발생!: {e}")

