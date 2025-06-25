#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from gradio_client import Client, handle_file
from openai import OpenAI
from prompt_templates import get_prompt
import requests
import tempfile

# ✅ OpenAI 클라이언트 설정
client_gpt = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Hugging Face OCR 클라이언트 설정
client_ocr = Client("prithivMLmods/Multimodal-OCR2")

def extract_text_from_image(image_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image_file.read())
            tmp_path = tmp.name

        result = client_ocr.predict(
            model_name="Nanonets-OCR-s",
            text="추출해줘",
            image=handle_file(tmp_path),
            max_new_tokens=1024,
            temperature=0.6,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2,
            api_name="/generate_image"
        )
        return result
    except Exception as e:
        return f"[OCR 오류] {str(e)}"

def generate_kakao_promo():
    st.title("📢 카카오채널 홍보멘트 생성기")

    st.markdown("""
    - 텍스트만 입력하거나
    - 이미지만 업로드하거나
    - 텍스트 + 이미지를 함께 입력할 수 있습니다.
    """)

    category = st.selectbox("홍보 카테고리", ["시정홍보", "정책공지", "축제", "이벤트", "재난알림"])
    user_text = st.text_area("📥 텍스트 입력 (선택사항)")
    uploaded_image = st.file_uploader("🖼️ 이미지 업로드 (선택사항)", type=["png", "jpg", "jpeg"])

    if st.button("🔍 홍보 문구 생성"):
        with st.spinner("분석 중..."):
            final_input = ""

            # 1️⃣ OCR 처리
            if uploaded_image is not None:
                ocr_text = extract_text_from_image(uploaded_image)
                st.markdown("**📝 OCR 결과:**")
                st.info(ocr_text)
                final_input += ocr_text + "\n"

            # 2️⃣ 사용자 입력 추가
            if user_text:
                final_input += user_text

            # 3️⃣ 프롬프트 구성 및 GPT 호출
            prompt = get_prompt(category, final_input)
            completion = client_gpt.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = completion.choices[0].message.content
            st.success("✅ 홍보 문구 생성 완료!")
            st.markdown("---")
            st.markdown(result_text)

        st.markdown("""---
        ✨ *충주시 홍보부서의 톤앤매너를 기반으로 작성되었습니다.*
        """)

