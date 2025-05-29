#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from openai import OpenAI

# 🔑 OpenAI 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 유형별 지시문
def get_prompt_by_report_type(report_type):
    if report_type == "계획보고":
        return "계획보고는 향후 추진방향, 일정, 예산, 기대효과 등을 중심으로 작성해줘. 추진배경과 목적도 간결히 포함하되, 전체적으로 미래지향적이고 전략적인 문장을 사용해."
    elif report_type == "동향보고":
        return "동향보고는 최근 변화나 현황을 중심으로 작성해줘. 통계나 수치를 근거로 하며, 원인분석과 향후 전망을 중심으로 작성해. 과거와 비교하는 분석적 시각도 포함해줘."
    elif report_type == "행사보고":
        return "행사보고는 행사 개요(일시, 장소, 참가자, 내용), 주요 결과와 성과, 시사점 순으로 구성해줘. 보고서는 행사 요약과 행정적 기록에 중점을 두고 작성해."
    else:
        return "일반적인 행정보고 형식으로 작성하되, 핵심 내용을 간결하고 체계적으로 정리해줘."

# ✅ 서식별 지시문
def get_prompt_by_format(report_format):
    if report_format == "개요 중심":
        return "개요-본론-결론 구조로 작성해줘. 첫 문단에 요약 개요를 넣고, 주요 내용은 문단별로 자연스럽게 이어지게 구성해."
    elif report_format == "항목 나열":
        return "각 주요 내용을 번호 또는 기호(예: ▸)로 나열하는 방식으로 작성해줘. 항목마다 짧고 명확하게 요약해."
    elif report_format == "표 형식":
        return "내용을 표 형식으로 요약 정리해줘. 항목별로 행정문서에 맞게 표로 구성하되 필요한 문장 설명도 포함해."
    elif report_format == "서술형":
        return "전체를 문단 중심으로 구성하되 자연스럽게 이어지는 서술형 보고서로 작성해줘. 항목 구분은 하지 않아도 돼."
    else:
        return "기본 행정문서 형식으로 간결하게 정리해줘."

# ✅ 길이별 지시문
def get_prompt_by_length(report_length):
    if report_length == "간략 (1~2문단)":
        return "전체 분량은 1~2문단으로 간략하게 구성해줘. 핵심 사항 위주로 압축 정리해."
    elif report_length == "표준 (2~3문단)":
        return "전체 분량은 2~3문단으로 구성해줘. 각 문단마다 주요 내용을 구분해 작성해."
    elif report_length == "상세 (3~4문단)":
        return "전체 분량은 3~4문단 이상으로 구성해줘. 추진배경, 주요내용, 향후계획 등 단계별로 나눠 서술해줘."
    else:
        return "적절한 분량으로 행정문서체로 작성해줘."

def build_user_prompt(title, report_type, report_format, report_length, key_points):
    type_instruction = get_prompt_by_report_type(report_type)
    format_instruction = get_prompt_by_format(report_format)
    length_instruction = get_prompt_by_length(report_length)

    # 📌 특별 조건 1: '표 형식'일 경우 - Markdown 표 형식 사용
    markdown_instruction = ""
    if report_format == "표 형식":
        markdown_instruction = "보고서 내 모든 표는 마크다운(Markdown) 표 형식으로 작성할 것. 예: `| 항목 | 내용 |` 구조를 따름."

    # 📌 특별 조건 2: '행사보고'일 경우 - 타임테이블 포함
    timetable_instruction = ""
    if report_type == "행사보고":
        timetable_instruction = "특히 '행사 일정표(타임테이블)'는 반드시 포함할 것. 시간대별 프로그램(예: 10:00 개회식, 10:20 지정서 수여 등)을 표 형태로 정리할 것."

    return f"""
너는 지방자치단체 공무원을 위한 AI 보고서 생성기야. 행정문서체와 개괄식 구성을 따르며, 명확하고 간결하게 작성해줘.

📌 제목: {title}  
📄 유형: {report_type}  
🧩 주요 키워드: {key_points}

작성 지시:
1. {type_instruction}
2. {format_instruction}
3. {length_instruction}
4. {markdown_instruction}
5. {timetable_instruction}

보고서 구성은 다음 순서를 따라:
1. 제목
2. 개요
3. 주요 내용 (필요 시 항목 나열 또는 표 포함)
4. 향후 계획 또는 시사점
"""

# ✅ Streamlit 앱 본체
def report_writer_app():
    st.title("🧠 AI 기반 보고서 생성기")

    report_type = st.selectbox("📄 보고서 유형을 선택하세요", ["계획보고", "동향보고", "행사보고"])
    report_format = st.selectbox("📝 보고서 서식을 선택하세요", ["개요 중심", "항목 나열", "표 형식", "서술형"])
    report_length = st.selectbox("📏 보고서 길이를 선택하세요", ["간략 (1~2문단)", "표준 (2~3문단)", "상세 (3~4문단)"])
    title = st.text_input("📌 보고서 제목을 입력하세요", placeholder="예: 스마트시티 추진계획")
    key_points = st.text_area("🧩 주요 키워드를 입력하세요 (쉼표로 구분)", placeholder="예: 지역연계, 예산확보, 타당성 검토")

    if st.button("📄 보고서 생성"):
        if not title or not key_points:
            st.warning("제목과 주요 키워드를 입력해주세요.")
        else:
            system_prompt = "너는 지방자치단체 공무원을 위한 AI 보고서 작성기야. 행정문서체와 개괄식 구성을 따르며, 명확하고 간결하게 작성해줘."
            user_prompt = build_user_prompt(title, report_type, report_format, report_length, key_points)

            with st.spinner("📡 GPT가 보고서를 작성 중입니다..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=2000
                )

                content = response.choices[0].message.content.strip()
                st.success("✅ 보고서가 생성되었습니다!")
                st.markdown("### 📝 생성된 보고서")
                st.markdown(content.replace("\n", "\n\n"))

# ✅ 실행
if __name__ == "__main__":
    report_writer_app()

