#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_external_visitor_spending_in_chungju():
    st.subheader("📊 14. 축제방문 외지인의 충주 관내 소비현황")
    st.markdown("📂 업로드된 엑셀 파일의 '읍면동, 소비금액(원), 소비건수(건)' 컬럼을 기준으로 분석합니다.")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["읍면동", "소비금액(원)", "소비건수(건)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 14_template.xlsx 다운로드",
        data=buffer,
        file_name="14_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
    if not uploaded_file:
        return

    # ✅ 데이터 로딩
    df = pd.read_excel(uploaded_file).dropna(how="all")

    # ✅ 숫자 정리
    df["소비금액(원)"] = df["소비금액(원)"].astype(float)
    df["소비건수(건)"] = df["소비건수(건)"].astype(int)

    # ✅ 합계 행 계산
    total_row = pd.DataFrame([{
        "읍면동": "합계",
        "소비금액(원)": df["소비금액(원)"].sum(),
        "소비건수(건)": df["소비건수(건)"].sum()
    }])

    # ✅ 합계 포함 데이터 재구성
    df = pd.concat([total_row, df], ignore_index=True)

    # ✅ 소비비율 계산
    total_amount = total_row["소비금액(원)"].values[0]
    df["소비비율"] = (df["소비금액(원)"] / total_amount * 100).round(2)
    df.loc[0, "소비비율"] = 100.00  # 합계는 무조건 100%

    # ✅ 읍면동 순서 강제 지정
    order = [
        "합계", "주덕읍", "살미면", "수안보면", "대소원면", "신니면", "노은면", "앙성면",
        "중앙탑면", "금가면", "동량면", "산척면", "엄정면", "소태면", "성내·충인동",
        "교현·안림동", "교현2동", "용산동", "지현동", "문화동", "호암·직동",
        "달천동", "봉방동", "칠금·금릉동", "연수동", "목행·용탄동"
    ]
    df["읍면동"] = pd.Categorical(df["읍면동"], categories=order, ordered=True)
    df = df.sort_values("읍면동").reset_index(drop=True)

    # ✅ 포맷팅
    df["소비금액(원)"] = df["소비금액(원)"].round().astype(int).apply(lambda x: f"{x:,}원")
    df["소비건수(건)"] = df["소비건수(건)"].astype(int).apply(lambda x: f"{x:,}건")
    df["소비비율"] = df["소비비율"].apply(lambda x: f"{x:.2f}%")

    # ✅ 출력
    st.markdown("### 🧾 읍면동별 소비현황")
    st.dataframe(df, use_container_width=True)

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        top5 = df[df["읍면동"] != "합계"].copy()
        top5["금액수치"] = top5["소비금액(원)"].str.replace(",", "").str.replace("원", "").astype(int)
        top5 = top5.sort_values(by="금액수치", ascending=False).drop(columns="금액수치").head(5)

        lines = [f"- {row['읍면동']}: {row['소비금액(원)']} / {row['소비건수(건)']} ({row['소비비율']})" for _, row in top5.iterrows()]
        summary = "\n".join(lines)

        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")

        summary_text = "\n".join([
            f"- {row['읍면동']}: {row['소비금액']} / {row['소비건수']} / {row['소비비율']}"
            for _, row in df_summary.iterrows()
        ])

        prompt = f"""다음은 {name}({period}, {location})의 축제방문 외지인에 대한 충주 관내 소비현황 분석 자료입니다.
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~기여하고 있음')  
▸ 각 문장은 ▸ 기호로 시작하고 2문장 이상 연결하여 자연스럽게 작성  
▸ 소비가 집중된 지역(예: 수안보면, 교현·안림동, 중앙탑면 등)은 소비금액·건수 기준으로 분석하고, 보조 소비거점으로서의 역할을 중심으로 해석  
▸ 지역별 소비 집중의 배경에 대해 숙박/관광지/상권 등의 특징을 추론하여 자연스럽게 녹여낼 것  
▸ 충주시 내 소비 분산 현상을 긍정적으로 평가하며, 체류형 소비 확대의 시사점을 제시  
▸ 마지막 문장은 실무적 제언 포함 (예: 축제장 외 연계 상권과의 협력 필요 등)  
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**

[충주시 읍면동별 외지인 소비현황 요약]
{summary_text}

※ 지역 특징 자동 추론: 각 읍면동의 특성(예: 숙박지 밀집, 관광명소, 시외 접근성 등)을 상식적 수준에서 판단하여 기술
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 소비 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )

        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

