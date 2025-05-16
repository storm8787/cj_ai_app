#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import datetime
import os
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 설정
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_FILE = "token.pkl"

def save_credentials(creds):
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)

def load_credentials():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            return pickle.load(token)
    return None

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

    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)
        else:
            if "code" not in st.experimental_get_query_params():
                flow = Flow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE,
                    scopes=SCOPES,
                    redirect_uri="http://localhost:8501/"
                )
                auth_url, _ = flow.authorization_url(prompt='consent')
                st.markdown(f"[🔐 구글 계정으로 로그인하기]({auth_url})")
                st.stop()
            else:
                code = st.experimental_get_query_params()["code"][0]
                flow = Flow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE,
                    scopes=SCOPES,
                    redirect_uri="http://localhost:8501/"
                )
                flow.fetch_token(code=code)
                creds = flow.credentials
                save_credentials(creds)
                st.success("✅ 로그인 성공! 계속 진행하세요.")
                st.experimental_rerun()

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
                st.error(f"❌ 오류 발생: {e}")

