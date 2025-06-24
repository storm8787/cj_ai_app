#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import requests
from PIL import Image
from PyPDF2 import PdfReader
import os
from prompt_templates import get_prompt
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")  # 환경변수로부터 카카오 API 키 불러오기

# ✅ 카카오 OCR API 호출 함수
def extract_text_via_kakao(file):
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    try:
        files = {"image": (file.name, file, file.type)}
        response = requests.post(
            "https://dapi.kakao.com/v2/vision/text/ocr",
            headers=headers,
            files=files
        )
        response.raise_for_status()
        result = response.json()

        words = [item['recognition_words'] for item in result.get("result", [])]
        flat_text = "\n".join([" ".join(word_list) for word_list in words if word_list])
        return flat_text

    except Exception as e:
        return f"OCR 오류: {e}"

# ✅ GPT 호출 함수
def call_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 충주시 카카오 채널 홍보 담당 비서야. 시민이 이해하기 쉬운 홍보멘트를 정제해줘."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# ✅ Streamlit 앱 메인
def generate_kakao_promo():
    st.header("💬 카카오톡 홍보멘트 생성기")

    category = st.radio("📌 홍보 컨셉을 선택하세요", ["시정홍보", "정책공지", "축제", "이벤트", "재난알림"])
    uploaded_file = st.file_uploader("🖼️ 포스터 이미지 또는 PDF 업로드", type=["pdf", "jpg", "jpeg", "png"])
    text_input = st.text_area("📝 홍보문구 입력 (선택사항)", placeholder="복붙하거나 비워두셔도 됩니다.")

    if st.button("📢 홍보문구 생성"):
        with st.spinner("GPT가 문구를 정리하는 중입니다..."):
            ocr_text = extract_text_via_kakao(uploaded_file) if uploaded_file else ""
            st.write("🔍 OCR 결과 (앞부분):", ocr_text[:100])

            final_text = (text_input.strip() + "\n\n" + ocr_text).strip() if text_input else ocr_text

            if not final_text:
                st.warning("텍스트 입력 또는 포스터 업로드 중 하나는 반드시 필요합니다.")
                return

            prompt = get_prompt(category, final_text)
            result = call_gpt(prompt)

            st.success("✅ 홍보 멘트 생성 완료!")
            st.text_area("🎯 생성된 홍보멘트", value=result, height=300)


# In[ ]:




