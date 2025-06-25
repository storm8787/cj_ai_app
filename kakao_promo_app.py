#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from openai import OpenAI
from prompt_templates import get_prompt
from google.cloud import vision
from google.oauth2 import service_account
import io

# ✅ OpenAI 클라이언트 설정
client_gpt = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Google Vision 클라이언트 설정
google_creds = service_account.Credentials.from_service_account_info(
    st.secrets["google_service_account"]
)
vision_client = vision.ImageAnnotatorClient(credentials=google_creds)

# ✅ 이미지에서 텍스트 추출 함수
def extract_text_from_image(image_file):
    try:
        # 이미지 바이트를 한 번만 읽기
        image_bytes = image_file.read()
        if not image_bytes:
            return "[OCR 오류] 이미지 파일을 읽을 수 없습니다."

        image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            return "[OCR 오류] 텍스트를 찾을 수 없습니다."
        return texts[0].description.strip()

    except Exception as e:
        return f"[OCR 오류] {str(e)}"

# ✅ 메인 기능 함수
def generate_kakao_promo():
    st.title("📢 카카오채널 홍보멘트 생성기")

    st.markdown("""
    - 텍스트만 입력하거나  
    - 이미지만 업로드하거나  
    - 텍스트 + 이미지를 함께 입력할 수 있습니다.
    """)

    category = st.selectbox("홍보 카테고리", ["시정홍보", "정책공지","문화행사", "축제", "이벤트", "재난알림"])
    user_text = st.text_area("📥 텍스트 입력 (선택사항)")
    uploaded_image = st.file_uploader("🖼️ 이미지 업로드 (선택사항)", type=["png", "jpg", "jpeg"])

    if st.button("🔍 홍보 문구 생성"):
        with st.spinner("분석 중..."):
            final_input = ""

            # 1️⃣ OCR 처리
            if uploaded_image is not None:
                st.info("📸 이미지에서 텍스트 추출 중...")
                ocr_text = extract_text_from_image(uploaded_image)
                st.markdown("**📝 OCR 결과:**")
                st.code(ocr_text)
                final_input += ocr_text + "\n"

            # 2️⃣ 사용자 입력 추가
            if user_text:
                final_input += user_text

            if not final_input.strip():
                st.error("❌ 텍스트 또는 이미지에서 입력된 내용이 없습니다.")
                return

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

# ✅ 앱 실행
if __name__ == "__main__":
    generate_kakao_promo()

