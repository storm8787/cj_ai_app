#!/usr/bin/env python
# coding: utf-8

# In[10]:


import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
#import openai
import os
import pandas as pd
import io
import uuid
from io import BytesIO

st.set_page_config(
    page_title="더 가까이, 충주시 AI 연구",  # 크롬 탭 제목
    page_icon="logo.png",  # 또는 아래처럼 이미지 favicon도 가능
    layout="wide"
)


# ✅ OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
#openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ PDF 텍스트 추출
def extract_text_from_pdf(file_obj):
    reader = PdfReader(file_obj)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"
    return full_text

# ✅ 유사 보도자료 검색
def find_similar_docs(query, documents, vectorizer, tfidf_matrix, top_n=3):
    query_vec = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarity_scores.argsort()[::-1][:top_n]
    return [documents[i] for i in top_indices]

# ✅ 보도자료 생성
def generate_press_release(user_request, similar_examples):
    system_prompt = "너는 지방정부 보도자료 작성 전문가야. 아래 유사 사례를 참고해, 행정기관 스타일로 공공 보도자료를 작성해줘."

    examples_combined = "\n\n---\n\n".join(similar_examples)
    joined_points = "\n- ".join(user_request['내용포인트'])

    길이지시 = {
        "짧게": 400,
        "중간": 600,
        "길게": 800
    }.get(user_request['길이'], 600)

    문단지시 = "" if user_request['문단수'] == "상관없음" else f"전체 글은 {user_request['문단수']}개의 문단으로 구성해주세요.\n"

    추가지시 = (
        f"보도자료에는 상단의 보도일자, 담당자 정보, 연락처는 포함하지 말고 본문만 작성해주세요.\n"
        f"담당자 인용문이 나올 경우, 담당자 이름은 '{user_request['담당자']}'이고, 직책은 '{user_request['담당부서']}장'으로 표기해주세요.\n"
        f"담당자 인용문이 나올 경우, '{user_request['담당자']}' 한칸띠고'{user_request['담당부서']}장'으로 표기해주세요.ex : 김태균 자치행정과장\n"
        f"전체 문체는 보도자료 스타일의 간접화법을 사용해주세요. 예: '~했다', '~라고 밝혔다' 등.\n"
        f"{문단지시}"
        f"보도자료는 반드시 '[제목] 본문제목'으로 시작한 후, 한 줄 아래에 부제목 형태의 요약 문장을 넣어주세요. 부제목은 '-' 기호로 시작하세요.\n"
        f"전체 보도자료 분량은 약 {길이지시}자 내외로 작성해주세요. 필요 시 최대 토큰 수를 늘려도 괜찮습니다."
        f"전체 보도자료는 반드시 {길이지시}자 안팎(±10자 이내)로 작성해주세요."
    )

    user_query_prompt = (
        f"입력한 제목 후보: {user_request['제목']}\n\n"
        f"아래 내용 포인트를 반영하여 보도자료에 어울리는 제목을 새로 작성하고, "
        f"그 제목을 '[제목]'에 반영해줘. 입력한 제목은 참고만 하고 그대로 쓰지 않아도 돼.\n\n"
        f"내용 포인트:\n- {joined_points}\n\n"
        f"요청사항:\n- {user_request['기타요청']}\n\n"
        f"{추가지시}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""아래는 참고용 보도자료 예시입니다:

{examples_combined}

위 스타일을 참고하여 아래 요청사항에 맞는 새로운 보도자료를 작성해줘:

{user_query_prompt}
"""}
    ]

    response = client.chat.completions.create(
#    response = openai.ChatCompletion.create(    
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=1500
    )

    return response.choices[0].message.content

# ✅ 보도자료 생성기 앱 함수
def press_release_app():
    st.title("📰 GPT 기반 보도자료 자동 생성기")
    st.info("본 생성기는 충주시의 보도자료 4,000건을 기반으로 학습한 GPT 모델을 활용하여,\n" 
            "충주시 스타일의 보도자료 초안을 자동으로 생성합니다.")

    txt_path = "data/corpus.txt"
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            corpus_text = f.read()
        documents = [doc.strip() for doc in corpus_text.split("---") if len(doc.strip()) > 50]
        if not documents:
            st.error("❌ corpus.txt에서 유효한 보도자료를 추출하지 못했습니다.")
            return
    else:
        st.error(f"❌ 텍스트 파일을 찾을 수 없습니다: {txt_path}")
        return

    제목 = st.text_input("📝 보도자료 제목을 입력하세요")
    담당부서 = st.text_input("🏢 담당 부서명을 입력하세요")
    담당자 = st.text_input("🧑‍🏫 관리자 이름을 입력하세요")
    문단수 = st.selectbox("📑 문단 수를 선택하세요", ["상관없음", "1개", "2개", "3개"])
    길이 = st.selectbox("📏 보도자료 길이", ["짧게", "중간", "길게"])
    내용포인트 = st.text_area("📌 내용 포인트 (한 줄에 하나씩 입력)", height=150)
    기타요청 = st.text_area("🔧 기타 요청사항", height=100)

    if st.button("🚀 보도자료 생성하기"):
        if 제목 and 내용포인트:
            user_request = {
                "제목": 제목,
                "내용포인트": [line.strip() for line in 내용포인트.strip().split("\n") if line.strip()],
                "기타요청": 기타요청.strip(),
                "담당부서": 담당부서.strip(),
                "담당자": 담당자.strip(),
                "문단수": 문단수,
                "길이": 길이
            }

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(documents)
            similar_examples = find_similar_docs(제목, documents, vectorizer, tfidf_matrix)

            with st.spinner("🤖 GPT가 보도자료를 작성 중입니다..."):
                press_release = generate_press_release(user_request, similar_examples)
                st.success("✅ 보도자료가 생성되었습니다!")
                st.text_area("📄 생성된 보도자료", press_release, height=500)
        else:
            st.warning("⚠️ 제목과 내용 포인트는 반드시 입력해야 합니다.")

def excel_merger():
    st.title("📊 엑셀 취합기")
    st.info("여러 개의 엑셀(.xlsx) 파일을 업로드하고 선택한 시트와 제목행을 기준으로 병합합니다.")

    header_row = st.number_input("📌 제목행은 몇 번째 행인가요? (1부터 시작)", min_value=1, value=1, step=1)
    sheet_option = st.selectbox("📄 병합할 시트를 선택하세요", [f"{i+1}번째 시트" for i in range(10)] + ["모든 시트"])

    uploaded_files = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx"], accept_multiple_files=True)
    st.warning("⚠️ *Streamlit Cloud에서는 한글 파일명을 업로드할 경우 오류가 발생할 수 있습니다.*\n"
           "👉 업로드 전에 **파일명을 영문 또는 숫자로 변경**해 주세요.")


    if uploaded_files:
        combined_df = pd.DataFrame()

        for idx, file in enumerate(uploaded_files):
            try:
                file_bytes = file.read()
                file_io = BytesIO(file_bytes)
                file_io.seek(0)

                if sheet_option == "모든 시트":
                    xls = pd.read_excel(file_io, sheet_name=None, header=header_row - 1)
                    for sheet_df in xls.values():
                        combined_df = pd.concat([combined_df, sheet_df], ignore_index=True)
                else:
                    sheet_index = int(sheet_option.split("번째 시트")[0]) - 1
                    df = pd.read_excel(file_io, sheet_name=sheet_index, header=header_row - 1)
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

                st.success(f"✅ 파일 {idx + 1} 처리 완료")

            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

        if not combined_df.empty:
            combined_df.reset_index(drop=True, inplace=True)
            combined_df.index = combined_df.index + 1
            combined_df.index.name = "순번"

            st.dataframe(combined_df.head(30))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='통합결과')
            output.seek(0)

            st.download_button(
                label="📥 통합 엑셀 다운로드",
                data=output.getvalue(),
                file_name="통합결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )   


# In[ ]:




