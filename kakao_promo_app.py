#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from gradio_client import Client, handle_file
from openai import OpenAI
import os

# ✅ OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# Hugging Face OCR 설정
client_ocr = Client("prithivMLmods/Multimodal-OCR2")

def run_ocr_from_image(image_path):
    result = client_ocr.predict(
        model_name="Nanonets-OCR-s",
        text="Extract text",
        image=handle_file(image_path),
        max_new_tokens=1024,
        temperature=0.6,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.2,
        api_name="/generate_image"
    )
    return result

def generate_promo(text):
    prompt = f"""다음 내용을 바탕으로 홍보 문구를 작성해줘:\n\n{text}\n\n형식은 간결한 한 문장으로 부탁해."""
    response = client_gpt.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("📢 홍보 문구 생성기")

uploaded_image = st.file_uploader("이미지를 업로드하세요", type=["png", "jpg", "jpeg"])
input_text = st.text_area("추가 텍스트 입력 (선택)", placeholder="홍보하고 싶은 문구나 키워드를 입력하세요")

if st.button("홍보 문구 생성"):
    final_text = ""

    # 1. 이미지 있으면 OCR 실행
    if uploaded_image is not None:
        with open("temp_img.jpg", "wb") as f:
            f.write(uploaded_image.read())
        ocr_text = run_ocr_from_image("temp_img.jpg")
        st.markdown("📝 OCR 결과:\n" + ocr_text)
        final_text += ocr_text + " "

    # 2. 입력 텍스트 있으면 결합
    if input_text:
        final_text += input_text.strip()

    if final_text.strip() == "":
        st.warning("텍스트나 이미지를 입력해야 홍보 문구를 만들 수 있어요.")
    else:
        with st.spinner("GPT가 홍보 문구를 작성 중입니다..."):
            promo = generate_promo(final_text)
            st.success("✅ 홍보 문구 생성 완료!")
            st.markdown(f"**🗣️ 홍보 문구:**\n> {promo}")

