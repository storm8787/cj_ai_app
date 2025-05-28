#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from openai import OpenAI

# 🔑 OpenAI API 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def report_writer_app():
    st.title("🧠 AI 기반 업무보고 생성기")

    # 1. 보고서 유형 선택
    report_type = st.selectbox("📌 보고서 유형을 선택하세요", ["업무보고", "동향보고", "행사보고"])

    # 2. 공통 입력
    department = st.text_input("🏢 부서명")
    writer = st.text_input("✍️ 작성자 이름")
    key_points = st.text_area("🧩 주요 내용 키워드 (쉼표로 구분)", placeholder="예: 민원처리, 주차장 조성, 주민설명회")

    # 3. 생성 버튼
    if st.button("📄 보고서 자동 생성"):
        if not department or not writer or not key_points:
            st.warning("모든 항목을 입력해주세요.")
            return

        system_prompt = "너는 지방자치단체 공무원이 작성하는 행정보고서를 대신 작성해주는 AI야. 모든 보고서는 '개괄식' 항목 구분 형식으로 작성하고, 문체는 행정문서체를 따를 것."

        user_prompts = {
            "업무보고": f"""
다음 조건을 바탕으로 '업무보고' 형식의 보고서를 아래 항목 구조로 작성해줘:

- 보고유형: 업무보고
- 부서명: {department}
- 작성자: {writer}
- 주요 키워드: {key_points}

보고서 항목 구성:
- 업무명:
- 추진일정:
- 추진내용:
- 관련부서:
- 향후계획:
""",
            "동향보고": f"""
다음 조건을 바탕으로 '동향보고' 형식의 보고서를 아래 항목 구조로 작성해줘:

- 보고유형: 동향보고
- 부서명: {department}
- 작성자: {writer}
- 주요 키워드: {key_points}

보고서 항목 구성:
- 사건일시:
- 사건장소:
- 사건내역:
- 대응조치:
- 향후계획:
""",
            "행사보고": f"""
다음 조건을 바탕으로 '행사보고' 형식의 보고서를 아래 항목 구조로 작성해줘:

- 보고유형: 행사보고
- 부서명: {department}
- 작성자: {writer}
- 주요 키워드: {key_points}

보고서 항목 구성:
- 행사명:
- 행사일시:
- 행사장소:
- 주요내용:
- 참석자:
- 향후계획:
"""
        }

        with st.spinner("📡 GPT가 보고서를 작성 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompts[report_type]}
                ],
                temperature=0.4
            )

            content = response.choices[0].message.content.strip()

        st.success("✅ 보고서가 생성되었습니다!")
        st.markdown("### 📝 생성된 보고서")
        st.markdown(f"**보고서 유형:** {report_type}")
        st.markdown(f"**부서명:** {department}  |  **작성자:** {writer}")
        st.markdown("---")
        st.markdown(content.replace("\n", "\n\n"))

