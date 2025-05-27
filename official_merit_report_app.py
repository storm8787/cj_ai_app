#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# official_merit_report_app.py

import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_merit_report(name, position, start_date, career_list, merit_points):
    career_str = "\n".join([f"- {item}" for item in career_list])
    merit_str = "\n".join([f"{i+1}. {point}" for i, point in enumerate(merit_points)])

    prompt = f"""
당신은 공무원의 공적심사 의결서를 작성하는 역할을 맡고 있습니다.

다음은 공무원 정보입니다:
- 성명: {name}
- 직급: {position}
- 임용일: {start_date}
- 주요경력:
{career_str}

공적요지 목록:
{merit_str}

위 내용을 기반으로 아래 조건에 맞는 공적사항 보고서를 작성하세요.

[요구 형식]
1. 서론: 임용일 이후 공직자로서의 태도, 충실도 등을 1~2문단으로 기술
2. 요약: 전체 공적요지를 포괄하여 간략한 공헌 내용 기술 (1문단)
3. 본문: 공적요지 항목별로 상세한 실적과 성과를 단락별로 작성 (1~2문단씩)
4. 마무리: 모범공무원으로서의 자세, 공로 요약 등으로 마무리

문장은 행정 보고서 형식을 따르며, 공직자 문서답게 자연스럽고 정중하게 서술할 것.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


def create_official_merit_report():
    st.title("🏅 공적심사의결서 생성기")
    st.markdown("공무원 정보를 입력하면 GPT가 공적사항 보고서를 자동으로 생성합니다.")

    with st.form("merit_form"):
        name = st.text_input("성명")
        position = st.text_input("직급")
        start_date = st.date_input("임용일").strftime("%Y년 %m월 %d일")
        
        st.markdown("### 주요경력 (연월일/이력 형식, 줄 단위)")
        career_raw = st.text_area("주요경력", height=150)
        career_list = [line.strip() for line in career_raw.splitlines() if line.strip()]

        st.markdown("### 공적요지 (한 줄에 하나씩 입력)")
        merit_raw = st.text_area("공적요지", height=200)
        merit_points = [line.strip() for line in merit_raw.splitlines() if line.strip()]

        submitted = st.form_submit_button("📄 공적사항 생성하기")
    
    if submitted:
        with st.spinner("GPT가 공적조서를 작성 중입니다..."):
            result = generate_merit_report(name, position, start_date, career_list, merit_points)
            st.subheader("📄 생성된 공적사항")
            st.write(result)
            st.download_button(
                label="📥 결과 다운로드 (TXT)",
                data=result,
                file_name=f"{name}_공적조서.txt",
                mime="text/plain"
            )

