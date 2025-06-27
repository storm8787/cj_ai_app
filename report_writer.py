#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from openai import OpenAI
from report_prompt_template import get_report_prompt  # 새 템플릿 로딩

# 🔑 OpenAI API 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 보고서 유형별 서식 매핑
report_format_options = {
    "계획보고": ["사업계획서형", "예산중심형", "시행일정형"],
    "동향보고": ["주간트렌드형", "상황분석형", "이슈집중형"],
    "성과보고": ["정량지표형", "협업성과형", "성과홍보형"],
    "상황보고": ["재난상황형", "시설이상형", "민원폭증형"],
    "기타보고": ["민원회신형", "안내문형", "내부의견서형"]
}

# ✅ 앱 메인 실행 함수
def report_writer_app():
    st.title("🧠 AI 기반 보고서 생성기")

    # 보고서 유형 선택
    report_type = st.selectbox("📄 보고서 유형을 선택하세요", list(report_format_options.keys()))

    # 서식 유형 선택
    format_type = st.selectbox("🧾 서식 유형을 선택하세요", report_format_options[report_type])

    # 보고서 제목 및 키워드 입력
    title = st.text_input("📌 보고서 제목을 입력하세요", placeholder="예: 2025년 스마트행정 플랫폼 추진계획")
    keyword_input = st.text_area("🧩 주요 키워드를 입력하세요 (쉼표로 구분)", placeholder="예: 스마트행정, 6억 원, 연차별 추진, 민원 자동화")

    if st.button("📄 보고서 생성"):
        if not title or not keyword_input:
            st.warning("제목과 주요 키워드를 입력해주세요.")
            return
        
        keywords = [kw.strip() for kw in keyword_input.split(",") if kw.strip()]
        prompt = get_report_prompt(report_type, format_type, title, keywords)

        system_msg = "너는 충주시 공무원을 위한 AI 보고서 작성기야. 반드시 행정문서체와 개괄식 종결형으로 작성할 것."

        with st.spinner("📡 GPT가 보고서를 작성 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4096
            )
            content = response.choices[0].message.content.strip()
            st.success("✅ 보고서가 생성되었습니다!")
            st.markdown("### 📝 생성된 보고서")
            st.markdown(content.replace("\n", "\n\n"))

# ✅ 실행
if __name__ == "__main__":
    report_writer_app()

