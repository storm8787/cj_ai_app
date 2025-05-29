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
        return "계획보고는 향후 추진방향, 일정, 예산, 기대효과 등을 중심으로 작성할 것. 추진배경과 목적도 간결히 포함하되, 전체적으로 미래지향적이고 전략적인 문장을 사용할 것."
    elif report_type == "동향보고":
        return "동향보고는 최근 변화나 현황을 중심으로 작성할 것. 통계나 수치를 근거로 하며, 원인분석과 향후 전망을 중심으로 서술할 것."
    elif report_type == "행사보고":
        return "행사보고는 행사 개요(일시, 장소, 참가자, 주요내용), 주요 결과 및 시사점을 중심으로 구성할 것."
    else:
        return "행정업무용 일반 보고서 형식으로 작성할 것."

# ✅ 서식별 지시문
def get_prompt_by_format(report_format):
    if report_format == "개요 중심":
        return "개요-본론-결론 구조로 작성할 것. 첫 문단에 개요를 명확히 제시하고, 이후 문단에서 세부 내용을 구체적으로 설명할 것."
    elif report_format == "항목 나열":
        return "주요 내용을 번호 또는 기호(예: ▸, ❍) 형태로 나열하며, 각 항목은 간결하고 명확하게 서술할 것."
    elif report_format == "표 형식":
        return "표 형식 내용은 Markdown 기반 표 형태(`| 항목 | 내용 |`)로 작성할 것. 표는 정렬이 유지되도록 주의하여 작성할 것."
    elif report_format == "서술형":
        return "전체를 문단 중심으로 자연스럽게 이어지도록 서술형으로 작성할 것. 항목 구분은 하지 않아도 됨."
    else:
        return "기본적인 행정문서 구성에 따라 작성할 것."

# ✅ 길이별 지시문
def get_prompt_by_length(report_length):
    if report_length == "간략 (1~2문단)":
        return "전체 분량은 1~2문단 내외로 간결하게 작성할 것."
    elif report_length == "표준 (2~3문단)":
        return "전체 분량은 2~3문단으로 구성하며, 각 문단은 명확한 주제를 중심으로 작성할 것."
    elif report_length == "상세 (3~4문단)":
        return "전체 분량은 3~4문단 이상으로 작성하고, 항목별로 논리적인 구성을 따를 것."
    else:
        return "적절한 분량으로 구성하고, 문단마다 핵심 주제를 명확히 할 것."

# ✅ 프롬프트 생성 함수
def build_user_prompt(title, report_type, report_format, report_length, key_points):
    type_instruction = get_prompt_by_report_type(report_type)
    format_instruction = get_prompt_by_format(report_format)
    length_instruction = get_prompt_by_length(report_length)

    # 🎯 행사보고일 경우 특수 구조 지시
    timetable_instruction = ""
    if report_type == "행사보고":
        timetable_instruction = (
            "\n\n보고서 구성은 다음과 같은 4단계 구조로 작성할 것:\n"
            "0. 행사 추진배경: 해당 행사의 추진 배경을 한두 문장으로 간략하게 서술할 것.\n"
            "1. 행사 개요: 항목별로 정리 (예: 행사명, 일시, 장소, 참석자 등)\n"
            "2. 시간표(안): 아래 예시처럼 **빈 줄 없이 연속된 Markdown 표 형식**으로 정리할 것:\n\n"
            "- 표는 중간에 빈 줄 없이 연속된 줄로 작성할 것.\n"
            "- 셀 내 줄바꿈이 필요한 경우 `<br>` 태그를 사용할 것.\n"
            "- 열 정렬은 `| :--- |` 형식으로 명시할 것.\n\n"
            "| 시간    | 프로그램 항목             |\n"
            "|---------|---------------------------|\n"
            "| 00:00   | 행사일정1                 |\n"
            "| 00:00   | 행사일정2                 |\n"
            "| 00:00   | 행사일정3                 |\n\n"
            "3. 향후 계획: 후속 조치나 실무적 시사점을 포함할 것."
        )

    return f"""
너는 충주시 공무원을 위한 AI 보고서 작성기야. 반드시 아래 조건을 충실히 따를 것:

- 전체 문장은 무조건 행정문서체로 작성할 것. (예: '~되었음', '~임', '~필요함')
- 개괄식 구성으로 작성하며, 불필요한 수식어 없이 명확하고 간결한 문장으로 서술할 것.

📌 제목: {title}  
📄 보고서 유형: {report_type}  
🧩 주요 키워드: {key_points}

작성 지시사항:
1. {type_instruction}
2. {format_instruction}
3. {length_instruction}
{timetable_instruction}

📑 보고서는 다음과 같은 구조를 따를 것:
1. 제목
2. 추진배경
3. 사업개요
4. 상세내용
5. 향후 추진계획
"""

# ✅ Streamlit 앱
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
            system_prompt = "너는 지방자치단체 공무원을 위한 AI 보고서 작성기야."
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

