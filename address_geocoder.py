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
    direction = st.radio("변환 방향을 선택하세요", ["주소 → 좌표", "좌표 → 주소"], horizontal=True)

    # 2. 처리 방식 선택
    mode = st.radio("처리 방식을 선택하세요", ["건별 입력", "파일 업로드"], horizontal=True)

    geolocator = Nominatim(user_agent="cj_ai_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    # -------------------
    # 주소 → 좌표
    # -------------------
    if direction == "주소 → 좌표":
        if mode == "건별 입력":
            address = st.text_input("📌 주소를 입력하세요")

            if st.button("좌표 변환"):
                location, level = resolve_address(address, geolocator)
                if location:
                    st.success(f"위도: {location.latitude}, 경도: {location.longitude}")
                    st.info(f"변환정확도: {level}")
                else:
                    st.error("⚠️ 변환 실패")

        else:
            st.download_button(
                label="📥 템플릿 다운로드 (template_addr.xlsx)",
                data=generate_template("address"),
                file_name="template_addr.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            uploaded = st.file_uploader("주소 목록 파일 업로드", type=["xlsx"])
            if uploaded and st.button("📌 파일 변환 실행"):
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

                result_df = pd.DataFrame(results)
                st.success("✅ 좌표 변환 완료")
                st.dataframe(result_df)
                download = to_excel(result_df)
                st.download_button("📥 결과 다운로드", data=download, file_name="result_addr_to_coord.xlsx")

    # -------------------
    # 좌표 → 주소
    # -------------------
    elif direction == "좌표 → 주소":
        if mode == "건별 입력":
            col1, col2 = st.columns(2)
            with col1:
                lat = st.text_input("위도")
            with col2:
                lon = st.text_input("경도")

            if st.button("주소 조회"):
                try:
                    location = geolocator.reverse(f"{lat}, {lon}")
                    if location:
                        st.success(f"📍 주소: {location.address}")
                    else:
                        st.warning("결과 없음")
                except Exception as e:
                    st.error("좌표 형식을 확인해주세요.")

        else:
            st.download_button(
                label="📥 템플릿 다운로드 (template_coordi.xlsx)",
                data=generate_template("coordinate"),
                file_name="template_coordi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            uploaded = st.file_uploader("좌표 목록 파일 업로드", type=["xlsx"])
            if uploaded and st.button("📌 파일 변환 실행"):
                df = pd.read_excel(uploaded)
                results = []
                for i, row in df.iterrows():
                    lat, lon = row["위도"], row["경도"]
                    try:
                        location = geolocator.reverse(f"{lat}, {lon}")
                        results.append({
                            "위도": lat,
                            "경도": lon,
                            "주소": location.address if location else "결과 없음"
                        })
                    except:
                        results.append({
                            "위도": lat,
                            "경도": lon,
                            "주소": "오류"
                        })

                result_df = pd.DataFrame(results)
                st.success("✅ 주소 조회 완료")
                st.dataframe(result_df)
                download = to_excel(result_df)
                st.download_button("📥 결과 다운로드", data=download, file_name="result_coord_to_addr.xlsx")

# -----------------------------
# 템플릿 생성 함수
# -----------------------------
def generate_template(template_type="address"):
    if template_type == "address":
        df = pd.DataFrame({"주소": ["예: 충청북도 충주시 칠금동 123-4"]})
    elif template_type == "coordinate":
        df = pd.DataFrame({"위도": ["36.991"], "경도": ["127.925"]})
    else:
        df = pd.DataFrame()
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

# -----------------------------
# 엑셀 변환 함수
# -----------------------------
def to_excel(df):
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output

# -----------------------------
# 주소 정밀도 보정 판단
# -----------------------------
def resolve_address(address, geolocator):
    location = geolocator.geocode(address)
    if location:
        return location, "정좌표"

    try:
        # 예: '충북 충주시' 형태
        location = geolocator.geocode(" ".join(address.split()[:2]))
        if location:
            return location, "인근주소"
    except:
        pass

    try:
        # 예: '충북'만으로
        location = geolocator.geocode(address.split()[0])
        if location:
            return location, "시군구 대표좌표"
    except:
        pass

    return None, "변환 실패"

