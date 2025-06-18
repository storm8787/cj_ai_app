#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import io

KAKAO_API_KEY = st.secrets["KAKAO_API_KEY"]

def run_geocoding_tool():
    st.header("📍 (업무지원) 주소-좌표 변환기")
    st.write("🔐 카카오 API Key:", KAKAO_API_KEY)


    # 1. 변환 방향 선택
    direction = st.radio("변환 방향을 선택하세요", ["주소 → 좌표", "좌표 → 주소"], horizontal=True)

    # 2. 처리 방식 선택
    mode = st.radio("처리 방식을 선택하세요", ["건별 입력", "파일 업로드"], horizontal=True)

    # -------------------
    # 주소 → 좌표
    # -------------------
    if direction == "주소 → 좌표":
        if mode == "건별 입력":
            address = st.text_input("📌 주소를 입력하세요", placeholder="예: 충청북도 충주시 호암수청1로 29")

            if st.button("좌표 변환"):
                result = get_coords_from_address(address)
                if result["위도"] and result["경도"]:
                    st.success(f"📌 위도: {result['위도']} / 경도: {result['경도']}")
                    st.info(f"정확도구분: {result['정확도구분']}")
                else:
                    st.error("⚠️ 변환 실패: " + result["정확도구분"])

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
                    res = get_coords_from_address(addr)
                    results.append({
                        "주소": addr,
                        "위도": res["위도"],
                        "경도": res["경도"],
                        "정확도구분": res["정확도구분"]
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
                    result = get_address_from_coords(lat, lon)
                    if result["주소"]:
                        st.success("📍 주소: " + result["주소"])
                    else:
                        st.warning("📭 결과 없음")
                except:
                    st.error("⚠️ 형식 오류 또는 API 오류")

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
                    res = get_address_from_coords(lat, lon)
                    results.append({
                        "위도": lat,
                        "경도": lon,
                        "주소": res["주소"]
                    })

                result_df = pd.DataFrame(results)
                st.success("✅ 주소 조회 완료")
                st.dataframe(result_df)
                download = to_excel(result_df)
                st.download_button("📥 결과 다운로드", data=download, file_name="result_coord_to_addr.xlsx")


# -----------------------------
# 주소 → 좌표 변환 함수 (카카오 API)
# -----------------------------
def get_coords_from_address(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        documents = r.json().get("documents", [])
        if documents:
            doc = documents[0]
            return {
                "위도": doc["y"],
                "경도": doc["x"],
                "정확도구분": "정좌표"
            }
        else:
            return {"위도": None, "경도": None, "정확도구분": "주소없음"}
    return {"위도": None, "경도": None, "정확도구분": "API오류"}

# -----------------------------
# 좌표 → 주소 변환 함수 (카카오 API)
# -----------------------------
def get_address_from_coords(lat, lon):
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"x": lon, "y": lat}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        docs = r.json().get("documents", [])
        if docs:
            address = docs[0].get("address", {})
            full = f"{address.get('region_1depth_name', '')} {address.get('region_2depth_name', '')} {address.get('region_3depth_name', '')} {address.get('road_name', '')} {address.get('main_address_no', '')}"
            return {"주소": full.strip()}
        else:
            return {"주소": None}
    return {"주소": None}

# -----------------------------
# 템플릿 생성 함수
# -----------------------------
def generate_template(template_type="address"):
    if template_type == "address":
        df = pd.DataFrame({"주소": ["충청북도 충주시 호암수청1로 29"]})
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

