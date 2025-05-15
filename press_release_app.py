#!/usr/bin/env python
# coding: utf-8

# In[10]:


import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os

# ✅ OpenAI API 키 설정
#openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


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

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # 키는 secrets에서 불러온다고 가정

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=1500
    )

    return response.choices[0].message.content

# ✅ Streamlit 앱 시작
st.title("📰 GPT 기반 보도자료 자동 생성기")

# 📂 corpus.txt 자동 로딩
txt_path = "data/corpus.txt"
if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        corpus_text = f.read()
    documents = [doc.strip() for doc in corpus_text.split("---") if len(doc.strip()) > 50]
    if not documents:
        st.error("❌ corpus.txt에서 유효한 보도자료를 추출하지 못했습니다.")
else:
    st.error(f"❌ 텍스트 파일을 찾을 수 없습니다: {txt_path}")
    st.stop()


# 📥 사용자 입력값 수집
제목 = st.text_input("📝 보도자료 제목을 입력하세요")
담당부서 = st.text_input("🏢 담당 부서명을 입력하세요")
담당자 = st.text_input("🧑‍🏫 담당자 이름을 입력하세요")

문단수 = st.selectbox("📑 문단 수를 선택하세요", ["상관없음", "1개", "2개", "3개"])
길이 = st.selectbox("📏 보도자료 길이", ["짧게", "중간", "길게"])  # 400, 600, 800자
내용포인트 = st.text_area("📌 내용 포인트 (한 줄에 하나씩 입력)", height=150)
기타요청 = st.text_area("🔧 기타 요청사항", height=100)


# ✅ 실행 버튼
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


# In[ ]:




