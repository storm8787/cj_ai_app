#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import io
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 시사점 예시 불러오기
def load_insight_examples(section_id):
    try:
        path = os.path.join("press_release_app", "data", "insights", f"{section_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def analyze_visitor_after_24h():
    st.subheader("📊 7-3. 외지인 24시간 이후지역 현황")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["시도", "시군구", "관광객수(%)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 7-3 템플릿 다운로드",
        data=buffer,
        file_name="7-3. template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 기준 방문객 수 입력
    total_visitors = st.number_input("🔢 기준 외지인 수 (24시간 이후 지역 이동자 수)", min_value=1, step=1)

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("📂 외지인 24시간 이후 이동지역 엑셀 업로드", type=["xlsx"])
    if not uploaded_file or total_visitors <= 0:
        return

    # ✅ 데이터 로드 및 유효성 검사
    df = pd.read_excel(uploaded_file).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]
    expected_cols = ["시도", "시군구", "관광객수(%)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ '시도', '시군구', '관광객수(%)' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 비율 계산 및 수치 변환
    df["비율"] = df["관광객수(%)"].astype(str).str.replace("%", "").astype(float) / 100
    df["관광객수"] = (df["비율"] * total_visitors).round().astype(int)

    # ✅ 구 단위 → 시 단위 병합
    merge_target_cities = [
        "청주시", "수원시", "안양시", "천안시", "용인시",
        "성남시", "고양시", "부천시", "안산시"
    ]
    def merge_sigungu(name):
        for city in merge_target_cities:
            if name.startswith(city):
                return city
        return name
    df["시군구"] = df["시군구"].apply(merge_sigungu)

    # ✅ 시도 + 시군구 병합
    df["full_region"] = df["시도"].str.strip() + " " + df["시군구"].str.strip()

    # ✅ full_region 기준 그룹화
    grouped = df.groupby("full_region", as_index=False)["관광객수"].sum()
    grouped["비율"] = (grouped["관광객수"] / total_visitors * 100)

    # ✅ 상위 20개 추출
    top20 = grouped.sort_values(by="관광객수", ascending=False).head(20).reset_index(drop=True)
    top20_total = top20["관광객수"].sum()

    # ✅ 기타/합계 행 구성
    others_row = {"full_region": "기타", "관광객수": total_visitors - top20_total, "비율": 100 - top20["비율"].sum()}
    sum_row = {"full_region": "합계", "관광객수": total_visitors, "비율": 100.0}

    # ✅ 왼쪽/오른쪽 분할 (기타/합계는 오른쪽에만 넣음)
    left = top20.iloc[:10].reset_index(drop=True)
    right = top20.iloc[10:].reset_index(drop=True)
    right = pd.concat([right, pd.DataFrame([others_row, sum_row])], ignore_index=True)

    # ✅ 비율 포맷팅
    left["비율"] = left["비율"].round(2).astype(str) + "%"
    right["비율"] = right["비율"].round(2).astype(str) + "%"

    # ✅ 컬럼명 접미어
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_df = pd.concat([left, right], axis=1)

    # ✅ 출력
    st.markdown("#### 📋 24시간 이후 이동지역 분석 결과")
    st.dataframe(result_df, use_container_width=True)

    # ✅ 세션 저장 (8번에서 활용)
    st.session_state["summary_visitor_after_24h"] = result_df.copy()
    st.session_state["summary_visitor_after_24h_grouped"] = grouped.copy()

    # ✅ 최다 체류 지역 1곳 추출
    top1_row = grouped.sort_values(by="관광객수", ascending=False).iloc[0]

    # ✅ 세션 상태 저장 (GPT 시사점 생성기에서 활용 예정)
    st.session_state["summary_visitor_after_24h_top1_region"] = top1_row["full_region"]
    st.session_state["summary_visitor_after_24h_top1_count"] = int(top1_row["관광객수"])
    st.session_state["summary_visitor_after_24h_top1_ratio"] = round(top1_row["비율"], 2)
    
    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("7-2_after")

        summary = "\n".join([
            f"- {row['full_region']}: {int(row['관광객수']):,}명 ({row['비율']:.2f}%)"
            for _, row in grouped.iterrows()
        ])

        prompt = f"""다음은 {name}({period}, {location}) 축제의 외지인 방문객에 대한 축제 종료 후 24시간 이내 체류지 분석 자료입니다.
▸ 문체는 행정보고서 형식(예: '~로 분석됨', '~한 것으로 판단됨')  
▸ 각 문장은 ▸ 기호로 시작하되, 지나치게 짧지 않도록 자연스럽게 연결하여 행정 보고서에 적합한 흐름으로 작성할 것  
▸ 전체 외지인 중 충주 내에 머무른 방문객 수와 비율을 수치로 제시하고, '단순 방문'이 아닌 '체류 관광'으로 이어졌다는 해석 중심으로 작성  
▸ 충주의 관광자원(온천, 벚꽃, 자연경관 등)이 외지인 체류에 기여했을 가능성을 언급  
▸ 가능하다면 추가콘텐츠(각종체험등), 숙박연계형 프로그램에 대한 정책 제언 1문장 포함  
▸ 단정적인 개선 제안은 피하고, 긍정적 흐름 중심으로 기술  
▸ 필요시 ※ 기호로 보충 설명 가능  
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**

[24시간 이내 충주 체류 외지인 수 요약]
{summary}
"""


        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 지방정부 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=700
        )

        st.subheader("🧠 GPT 시사점")
        st.write(response.choices[0].message.content)

