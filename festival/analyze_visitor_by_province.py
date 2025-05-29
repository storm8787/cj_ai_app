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

def analyze_visitor_by_province():
    st.subheader("📊 7-1. 시도 및 시군구별 외지인 방문객 거주지 분석기")

    # ✅ 템플릿 다운로드
    template_df = pd.DataFrame(columns=["시도", "시군구", "관광객수(%)"])
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 7-1 템플릿 다운로드",
        data=buffer,
        file_name="7-1. template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ 기준 방문객 수 입력
    total_visitors = st.number_input("🔢 기준 외지인 방문객 수를 입력하세요", min_value=1, step=1)

    # ✅ 파일 업로드
    uploaded_file = st.file_uploader("📂 시도별 비율 데이터 엑셀 업로드", type=["xlsx"])
    if not uploaded_file or total_visitors <= 0:
        return

    # ✅ 데이터 로드 및 유효성 검사
    df = pd.read_excel(uploaded_file).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]
    expected_cols = ["시도", "시군구", "관광객수(%)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ '시도', '시군구', '관광객수(%)' 컬럼이 포함된 파일을 업로드해주세요.")
        return

    # ✅ 관광객 수 계산
    df["비율"] = df["관광객수(%)"].astype(str).str.replace("%", "").astype(float) / 100
    df["관광객수"] = (df["비율"] * total_visitors).round().astype(int)

    # ✅ 시도별 그룹화 및 2열 출력
    grouped = df.groupby("시도", as_index=False)["관광객수"].sum()
    # ✅ 바로 여기서 먼저 int 처리
    grouped["관광객수"] = grouped["관광객수"].astype(int)
    grouped["비율"] = (grouped["관광객수"] / total_visitors * 100)

    # 정렬 추가
    grouped = grouped.sort_values(by="관광객수", ascending=False).reset_index(drop=True)
    grouped["관광객수"] = grouped["관광객수"].astype(int)


    mid = len(grouped) // 2  # 항상 floor
    left = grouped.iloc[:mid].reset_index(drop=True)
    right = grouped.iloc[mid:].reset_index(drop=True)
    left["관광객수"] = left["관광객수"].apply(lambda x: f"{int(x):,}")
    right["관광객수"] = right["관광객수"].apply(lambda x: f"{int(x):,}")
    left["비율"] = left["비율"].round(2).astype(str) + "%"
    right["비율"] = right["비율"].round(2).astype(str) + "%"
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_df = pd.concat([left, right], axis=1)

    # ✅ 합계 행 추가
    total_row = {
        "시도_1": "", "관광객수_1": "", "비율_1": "",
        "시도_2": "합계",
        "관광객수_2": int(grouped["관광객수"].sum()),
        "비율_2": "100.00%"        
    }
    result_df = pd.concat([result_df, pd.DataFrame([total_row])], ignore_index=True)

    st.markdown("#### 📋 시도별 분석 결과")
    st.dataframe(result_df, use_container_width=True)

    # ✅ 저장
    st.session_state["summary_visitor_by_province_sido"] = result_df.copy()

    # -------------------------
    # ✅ 시군구별 외지인 방문객 분석 (full_region 기준)
    # -------------------------
    st.markdown("### 🏙️ 7-2. 시군구별 외지인 방문객 현황")

    # ✅ 구 단위를 시로 병합할 시 리스트
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
    df["full_region"] = df["시도"].str.strip() + " " + df["시군구"].str.strip()

    # ✅ full_region 기준 그룹화
    grouped_gungu = df.groupby("full_region", as_index=False)["관광객수"].sum()
    grouped_gungu["비율"] = (grouped_gungu["관광객수"] / total_visitors * 100)

    # ✅ 상위 20개 + 기타 + 합계
    top20 = grouped_gungu.sort_values(by="관광객수", ascending=False).head(20).reset_index(drop=True)
    top20_total = top20["관광객수"].sum()
    others_row = {
        "full_region": "기타",
        "관광객수": total_visitors - top20_total,
        "비율": 100 - top20["비율"].sum()
    }
    sum_row = {
        "full_region": "합계",
        "관광객수": total_visitors,
        "비율": 100.0
    }

    # ✅ 분할 및 기타/합계 오른쪽 배치
    left = top20.iloc[:10].reset_index(drop=True)
    right = top20.iloc[10:].reset_index(drop=True)
    right = pd.concat([right, pd.DataFrame([others_row, sum_row])], ignore_index=True)

    # ✅ 포맷팅 및 접미어 처리
    left["비율"] = left["비율"].round(2).astype(str) + "%"
    right["비율"] = right["비율"].round(2).astype(str) + "%"
    left.columns = [f"{col}_1" for col in left.columns]
    right.columns = [f"{col}_2" for col in right.columns]
    result_gungu = pd.concat([left, right], axis=1)

    # ✅ 시군구 분석 결과 출력
    st.dataframe(result_gungu, use_container_width=True)

    # ✅ 시군구 비율 딕셔너리 저장 (12번 소비 분석기용)
    visitor_dict = dict(zip(left["full_region_1"], left["비율_1"].str.replace("%", "").astype(float)))
    st.session_state["visitor_by_province"] = visitor_dict

    # ✅ 저장
    st.session_state["summary_visitor_by_province_gungu"] = result_gungu.copy()

    # ✅ GPT 시사점 생성
    with st.spinner("🤖 GPT 시사점 생성 중..."):
        name = st.session_state.get("festival_name", "본 축제")
        period = st.session_state.get("festival_period", "")
        location = st.session_state.get("festival_location", "")
        reference = load_insight_examples("7-1_visitor")

        # ✅ 시도 기준 요약
        summary_sido = "\n".join([
            f"- {row['시도']}: {int(row['관광객수']):,}명 ({row['비율']})"
            for _, row in grouped.iterrows()
        ])

        # ✅ 시군구 기준 요약
        summary_gungu = "\n".join([
            f"- {row['full_region']}: {int(row['관광객수']):,}명 ({row['비율']})"
            for _, row in grouped_gungu.iterrows()
        ])

        # ✅ GPT 프롬프트 (시도)
        prompt_sido = f"""다음은 {name}({period}, {location}) 축제의 시도별 외지인 방문객 분석 자료입니다.

▸ 각 문장은 ▸ 기호로 시작하되, 지나치게 짧지 않도록 자연스럽게 연결하여 행정 보고서에 적합한 흐름으로 작성할 것  
▸ 비중이 높은 시도(3~6곳)를 괄호에 수치(%)와 함께 나열하고, 해당 지역의 참여 경향과 특징을 중심으로 해석  
▸ 수도권, 인접 권역(충청권·강원권 등), 타권역에서의 유입 분포를 실제 데이터 기반으로 평가  
▸ 단일 지역 편향 없이 분포 흐름을 종합적으로 기술하고, 전국 확산성·접근성 등 긍정적 해석 포함  
▸ 마지막 문장에는 주요 유입 권역을 대상으로 한 맞춤형 홍보 전략 또는 협업 가능성 등 간단한 정책 제언 1문장을 포함  
▸ 필요시 ※ 기호로 보충 설명 가능  
▸ 참고자료는 단순 참고용이며, 해석은 반드시 데이터 요약값 기반으로 도출할 것
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**

[시도별 외지인 방문객 수 요약]
{summary_sido}+ f"\n\n[유사 시사점 예시]\n{reference}"

"""

        response_sido = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt_sido}
            ],
            temperature=0.5,
            max_tokens=700
        )
        st.subheader("🧠 GPT 시사점 (시도 기준)")
        st.write(response_sido.choices[0].message.content)

        # ✅ GPT 프롬프트 (시군구)
        prompt_gungu = f"""다음은 {name}({period}, {location}) 축제의 시군구별 외지인 방문객 분석 자료입니다.

▸ 각 문장은 ▸ 기호로 시작하되, 지나치게 짧지 않도록 자연스럽게 연결하여 행정 보고서에 적합한 흐름으로 작성할 것  
▸ 비중이 높은 시군구(상위 5~7곳 정도)를 수치와 함께 나열하고, 인접성·인구규모·접근성 등과 연결하여 해석  
▸ 충주시 인근 시군과 수도권 도시의 참여 양상을 비교하며, 권역 확산성과 접근성의 조화를 해석적으로 기술  
▸ 특정 지역 집중 현상은 긍정적으로 해석하되, 다양한 지역에서의 고른 분포가 확인된다면 전국 확산 효과로 연결  
▸ 마지막 문장에는 상위 시군구 지역을 대상으로 한 타지자체 협업 홍보 또는 연계 마케팅 전략 등의 실무 제언 포함  
▸ 필요시 ※ 기호로 보충 설명 가능  
▸ 참고자료는 문체 참고용이며, 분석은 반드시 아래 요약 데이터를 기반으로 작성할 것
▸ **각 문장은 줄바꿈(엔터)으로 구분되도록 작성**

[시군구별 외지인 방문객 수 요약]
{summary_gungu}+ f"\n\n[유사 시사점 예시]\n{reference}"


"""

        response_gungu = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 충주시 축제 데이터를 분석하는 전문가야."},
                {"role": "user", "content": prompt_gungu}
            ],
            temperature=0.5,
            max_tokens=700
        )
        st.subheader("🧠 GPT 시사점 (시군구 기준)")
        st.write(response_gungu.choices[0].message.content)

