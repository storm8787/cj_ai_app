#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import io

def run_geocoding_tool():
    st.header("📍 (업무지원) 주소-좌표 변환기")

    # 1. 변환 방향 선택
    direction = st.radio("변환 방향을 선택하세요", ["주소 → 좌표", "좌표 → 주소"])

    # 2. 처리 방식 선택
    mode = st.radio("처리 방식을 선택하세요", ["건별 입력", "파일 업로드"])

    geolocator = Nominatim(user_agent="cj_ai_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    if direction == "주소 → 좌표":
        if mode == "건별 입력":
            address = st.text_input("주소를 입력하세요")

            if st.button("좌표 변환"):
                location, level = resolve_address(address, geolocator)
                if location:
                    st.success(f"위도: {location.latitude}, 경도: {location.longitude}")
                    st.info(f"변환정확도: {level}")
                else:
                    st.error("변환 실패")
        else:
            st.download_button(
                label="📥 템플릿1 다운로드",
                data=generate_template(example_col="주소"),
                file_name="template1_주소입력.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            uploaded = st.file_uploader("주소 목록 파일 업로드", type=["xlsx"])
            if uploaded and st.button("파일 변환 실행"):
                df = pd.read_excel(uploaded)
                results = []
                for addr in df["주소"]:
                    location, level = resolve_address(addr, geolocator)
                    results.append({
                        "주소": addr,
                        "위도": location.latitude if location else None,
                        "경도": location.longitude if location else None,
                        "변환정확도": level
                    })
                st.success("✅ 변환 완료")
                st.dataframe(results)
                download = pd.DataFrame(results).to_excel(index=False)
                st.download_button("📥 결과 다운로드", data=download, file_name="변환결과.xlsx")

# 주소 해석 로직 (정확도 레벨 판정 포함)
def resolve_address(address, geolocator):
    # 1. 정확히 변환 시
    location = geolocator.geocode(address)
    if location:
        return location, "정좌표"
    # 2. 인근 주소 시도
    location = geolocator.geocode(address.split()[0:2])  # 예: "충청북도 충주시"
    if location:
        return location, "인근주소"
    # 3. 시군구 대표
    location = geolocator.geocode(address.split()[0])
    if location:
        return location, "시군구 대표좌표"
    return None, "변환 실패"

# 템플릿 생성
def generate_template(example_col="주소"):
    df = pd.DataFrame({example_col: ["예: 충청북도 충주시 칠금동 123-4"]})
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

