#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from openai import OpenAI

# 🔑 OpenAI 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def report_writer_app():
    st.title("🧠 AI 기반 보고서 생성기")

    # 1. 보고서 유형 선택
    report_type = st.selectbox("📄 보고서 유형을 선택하세요", ["계획", "대책", "상황", "분석", "기타"])

    # 2. 보고서 서식 선택
    report_format = st.selectbox("📝 보고서 서식을 선택하세요", ["개요 중심", "항목 나열", "표 형식", "서술형"])

    # 3. 보고서 길이 선택
    report_length = st.selectbox("📏 보고서 길이를 선택하세요", ["간략 (1~2문단)", "표준 (2~3문단)", "상세 (3~4문단)"])

    # 4. 제목 입력
    title = st.text_input("📌 보고서 제목을 입력하세요", placeholder="예: 스마트시티 추진계획")

    # 5. 주요 키워드 입력
    key_points = st.text_area("🧩 주요 키워드를 입력하세요 (쉼표로 구분)", placeholder="예: 지역연계, 예산확보, 타당성 검토")

    # 6. 보고서 생성 버튼
    if st.button("📄 보고서 생성"):
        if not title or not key_points:
            st.warning("제목과 주요 키워드를 입력해주세요.")
        else:
            # 프롬프트 구성
            system_prompt = "너는 지방자치단체 공무원을 위한 AI 보고서 작성기야. 행정문서체와 개괄식 구성을 따르며, 명확하고 간결하게 작성해줘."

            user_prompt = f"""
다음 정보를 바탕으로 보고서를 작성해줘:

- 제목: {title}
- 유형: {report_type}
- 서식: {report_format}
- 길이: {report_length}
- 주요 키워드: {key_points}

보고서는 다음과 같은 구조로 작성해줘:
1. 제목
2. 개요
3. 주요 내용 (번호 또는 항목으로 정리)
4. 향후 계획 또는 시사점
"""

            with st.spinner("📡 GPT가 보고서를 작성 중입니다..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5
                )

                content = response.choices[0].message.content.strip()
                st.success("✅ 보고서가 생성되었습니다!")

                st.markdown("### 📝 생성된 보고서")
                st.markdown(content.replace("\n", "\n\n"))

# 앱 실행
if __name__ == "__main__":
    generate_report()

