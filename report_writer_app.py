#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from openai import OpenAI

# 🔑 OpenAI 키 설정 (Streamlit Secrets or 직접 입력)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def report_writer_app():
    st.title("🧠 AI 기반 업무보고 생성기")

    # 1. 보고서 유형 선택
    report_type = st.selectbox("📌 보고서 유형을 선택하세요", ["업무보고", "동향보고", "행사보고"])

    # 2. 공통 입력값 받기
    department = st.text_input("🏢 부서명")
    writer = st.text_input("✍️ 작성자 이름")
    key_points = st.text_area("🧩 주요 내용 키워드 (쉼표로 구분)", placeholder="예: 스마트시티, 협업회의, 추진일정")

    # 3. 생성 버튼
    if st.button("📄 보고서 자동 생성"):
        if not department or not writer or not key_points:
            st.warning("모든 항목을 입력해주세요.")
        else:
            # 프롬프트 구성
            system_prompt = "너는 지방자치단체 공무원이 작성하는 행정보고서를 대신 작성해주는 AI야. 문체는 행정문서 형식을 따르고, 간결하고 구체적으로 작성해."

            report_type_prompt = {
                "업무보고": f"""
다음 조건을 기반으로 4~5문단 분량의 업무보고 형식 문서를 작성해줘.
- 보고서 유형: 업무보고
- 부서명: {department}
- 작성자: {writer}
- 주요 내용 키워드: {key_points}
""",
                "동향보고": f"""
다음 조건을 기반으로 4문단 분량의 동향보고 형식 문서를 작성해줘.
- 보고서 유형: 동향보고
- 부서명: {department}
- 작성자: {writer}
- 주요 키워드: {key_points}
""",
                "행사보고": f"""
다음 조건을 기반으로 4문단 분량의 행사보고 형식 문서를 작성해줘.
- 보고서 유형: 행사보고
- 부서명: {department}
- 작성자: {writer}
- 주요 키워드: {key_points}
"""
            }

            with st.spinner("📡 GPT가 보고서를 작성 중입니다..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": report_type_prompt[report_type]}
                    ],
                    temperature=0.5
                )

                content = response.choices[0].message.content.strip()
                st.success("✅ 보고서가 생성되었습니다!")

                st.markdown("### 📝 생성된 보고서")
                st.markdown(f"**보고서 유형:** {report_type}")
                st.markdown(f"**부서명:** {department}  |  **작성자:** {writer}")
                st.markdown("---")
                st.markdown(content.replace("\n", "\n\n"))

