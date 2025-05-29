#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
import datetime
from openai import OpenAI

client = OpenAI()

# ✅ 시사점 예시 로딩
def load_daily_reference():
    path = os.path.join("press_release_app", "data", "insights", "2_daily.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ✅ 날짜 문자열 → 요일 한글 반환
def get_weekday_kor(date_str):
    try:
        date_obj = pd.to_datetime(date_str)
        day_kor = ["월", "화", "수", "목", "금", "토", "일"]
        return day_kor[date_obj.weekday()]
    except:
        return "요일없음"

def analyze_daily_visitor():
    st.subheader("📊 2. 일자별 방문객 수 분석")

    start_date = st.session_state.get("festival_start_date")
    end_date = st.session_state.get("festival_end_date")
    if not start_date or not end_date:
        st.warning("먼저 축제 기본정보를 입력해주세요.")
        return

    date_range = pd.date_range(start=start_date, end=end_date)
    date_strs = [d.strftime("%Y-%m-%d") for d in date_range]
    day_labels = [f"{i+1}일차" for i in range(len(date_strs))]

    local_counts, tourist_counts = [], []

    st.markdown("🎫 **일자별 현지인/외지인 방문객 수를 입력하세요**")
    for d in date_strs:
        col1, col2 = st.columns(2)
        with col1:
            local = st.number_input(f"{d} - 현지인", min_value=0, key=f"local_{d}")
        with col2:
            tourist = st.number_input(f"{d} - 외지인", min_value=0, key=f"tourist_{d}")
        local_counts.append(local)
        tourist_counts.append(tourist)

    if st.button("📊 분석 실행"):
        # ✅ 원본 DF 구성
        df = pd.DataFrame({
            "일자": date_strs,
            "현지인": local_counts,
            "외지인": tourist_counts
        })
        df["합계"] = df["현지인"] + df["외지인"]

        # ✅ 합계 계산
        total_local = df["현지인"].sum()
        total_tourist = df["외지인"].sum()
        total_all = df["합계"].sum()

        # ✅ 비율 계산
        df["현지인비율(%)"] = (df["현지인"] / total_local * 100).round(2)
        df["외지인비율(%)"] = (df["외지인"] / total_tourist * 100).round(2)
        df["합계비율(%)"] = (df["합계"] / total_all * 100).round(2)

        # ✅ 요약표 형태로 재구성 (전치)
        df_summary = pd.DataFrame({
            day_labels[i]: [local_counts[i], tourist_counts[i], local_counts[i]+tourist_counts[i]]
            for i in range(len(day_labels))
        }, index=["현지인", "외지인", "합계"])

        df_summary["합계"] = df_summary.sum(axis=1)

        df_ratio = pd.DataFrame({
            day_labels[i]: [
                df.loc[i, "현지인비율(%)"],
                df.loc[i, "외지인비율(%)"],
                df.loc[i, "합계비율(%)"]
            ]
            for i in range(len(day_labels))
        }, index=["현지인비율(%)", "외지인비율(%)", "합계비율(%)"])
        df_ratio["합계"] = 100.0

        df_final = pd.concat([df_summary, df_ratio])
        df_final.index.name = "구분"

        st.subheader("📊 방문객 수 요약표")
        st.dataframe(df_final, use_container_width=True)

        # ✅ 요일 분석
        df["요일"] = df["일자"].apply(get_weekday_kor)
        df["비율_전체"] = df["합계"] / total_all
        top_all_row = df.loc[df["비율_전체"].idxmax()]
        top_day_all = f"{top_all_row['요일']}({top_all_row['비율_전체'] * 100:.2f}%)"+ "%"

        df["비율_현지인"] = df["현지인"] / total_local
        top_local_row = df.loc[df["비율_현지인"].idxmax()]
        top_day_local = f"{top_local_row['요일']}({top_local_row['비율_현지인'] * 100:.2f}%)"+ "%"

        df["비율_외지인"] = df["외지인"] / total_tourist
        top_tourist_row = df.loc[df["비율_외지인"].idxmax()]
        top_day_tourist = f"{top_tourist_row['요일']}({top_tourist_row['비율_외지인'] * 100:.2f}%)"+ "%"

        # ✅ 요약값 저장
        st.session_state["summary_top_day_all"] = top_day_all
        st.session_state["summary_top_day_local"] = top_day_local
        st.session_state["summary_top_day_tourist"] = top_day_tourist
        st.session_state["summary_daily_total_local"] = total_local
        st.session_state["summary_daily_total_tourist"] = total_tourist
        st.session_state["summary_daily_total_all"] = total_all
        st.session_state["summary_daily_df"] = df_final

        # ✅ GPT 시사점 생성
        with st.spinner("🤖 GPT 시사점 생성 중..."):
            name = st.session_state.get("festival_name", "본 축제")
            period = st.session_state.get("festival_period", "")
            location = st.session_state.get("festival_location", "")
            summary = f"- 올해: 현지인 {total_local:,}명 / 외지인 {total_tourist:,}명 / 전체 {total_all:,}명"

            prompt = f"""다음은 {name}({period}, {location})에 대한 방문객 수 분석입니다.

▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 각 문장은 ▸ 기호로 시작하며, 3~5문장으로 구성  
▸ 방문객 총합 및 일자별/유형별 차이 강조  
▸ 수치 변화 중심으로 서술하되 부정 표현은 중립적으로 처리  
▸ 필요 시 ※ 표시로 부가 설명  
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**  

## 방문객 수 요약:
{summary}

위 정보를 바탕으로 방문객 분석 시사점을 작성해주세요.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 지방정부의 지역 축제 데이터를 분석하는 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=900
            )

            st.subheader("🧠 GPT 시사점")
            st.write(response.choices[0].message.content)


