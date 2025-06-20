#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import io

KAKAO_API_KEY = st.secrets["KAKAO_API"]["KEY"]

# ─────────────────────────────────────────────
# ✅ 실행 함수
# ─────────────────────────────────────────────
def run_geocoding_tool():
    st.title("📍 주소-자포 변환기")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔹 변환 방향")
        direction = st.radio("", ["주소 → 좌표", "좌표 → 주소"], horizontal=True)
    with col2:
        st.markdown("#### 🛠️ 처리 방식")
        mode = st.radio("", ["건별", "파일별"], horizontal=True)

    if direction == "주소 → 좌표":
        if mode == "건별":
            handle_single_address_to_coords()
        else:
            handle_file_address_to_coords()
    else:
        if mode == "건별":
            handle_single_coords_to_address()
        else:
            handle_file_coords_to_address()

# ─────────────────────────────────────────────
# ✅ 카카오 API 연동 함수
# ─────────────────────────────────────────────
def get_coords_from_kakao(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        if data["documents"]:
            x = data["documents"][0]["x"]
            y = data["documents"][0]["y"]
            return {"위도": y, "경도": x, "오류": ""}
        return {"위도": None, "경도": None, "오류": "주소 없음"}
    return {"위도": None, "경도": None, "오류": f"API 오류({r.status_code})"}

def get_address_from_kakao(lat, lon):
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"x": lon, "y": lat}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        if data["documents"]:
            addr = data["documents"][0]["address"]["address_name"]
            return {"주소": addr, "오류": ""}
        return {"주소": None, "오류": "주소 없음"}
    return {"주소": None, "오류": f"API 오류({r.status_code})"}

# ─────────────────────────────────────────────
# ✅ 건별 변환 함수
# ─────────────────────────────────────────────
def handle_single_address_to_coords():
    address = st.text_input("📌 주소 입력", placeholder="예: 충청북도 충주시 으뜸로 21")
    if st.button("변환 실행"):
        result = get_coords_from_kakao(address)
        if result["위도"] and result["경도"]:
            st.success(f"📌 위도: {result['위도']} / 경도: {result['경도']}")
            if st.checkbox("🗺️ 지도 보기"):
                draw_kakao_map(result["위도"], result["경도"])
        else:
            st.error("❌ 변환 실패: " + result["오류"])

def handle_single_coords_to_address():
    lat = st.text_input("위도", placeholder="예: 36.991")
    lon = st.text_input("경도", placeholder="예: 127.925")
    if st.button("주소 조회"):
        result = get_address_from_kakao(lat, lon)
        if result["주소"]:
            st.success("📍 주소: " + result["주소"])
            if st.checkbox("🗺️ 지도 보기"):
                draw_kakao_map(result["위도"], result["경도"])
        else:
            st.warning("📭 결과 없음")

# ─────────────────────────────────────────────
# ✅ 파일별 처리 함수
# ─────────────────────────────────────────────
def handle_file_address_to_coords():
    st.markdown("📥 템플릿 형식: 주소 컬럼 이름은 반드시 `주소`로 입력")
    generate_template(["주소"], "template_주소→좌표.xlsx")
    uploaded = st.file_uploader("📂 파일 업로드", type="xlsx")
    if uploaded:
        df = pd.read_excel(uploaded)
        if "주소" not in df.columns:
            st.error("❌ '주소' 컬럼이 누락되었습니다.")
            return
        results = []
        for addr in df["주소"]:
            r = get_coords_from_kakao(addr)
            results.append({"주소": addr, "위도": r["위도"], "경도": r["경도"], "오류": r["오류"]})
        result_df = pd.DataFrame(results)
        st.success("✅ 변환 완료")
        st.dataframe(result_df)
        to_excel_download(result_df, "결과_주소→좌표.xlsx")

def handle_file_coords_to_address():
    st.markdown("📥 템플릿 형식: 위도/경도 컬럼 이름은 반드시 `위도`, `경도`로 입력")
    generate_template(["위도", "경도"], "template_좌표→주소.xlsx")
    uploaded = st.file_uploader("📂 파일 업로드", type="xlsx")
    if uploaded:
        df = pd.read_excel(uploaded)
        if not all(col in df.columns for col in ["위도", "경도"]):
            st.error("❌ '위도', '경도' 컬럼이 누락되었습니다.")
            return
        results = []
        for _, row in df.iterrows():
            r = get_address_from_kakao(row["위도"], row["경도"])
            results.append({"위도": row["위도"], "경도": row["경도"], "주소": r["주소"], "오류": r["오류"]})
        result_df = pd.DataFrame(results)
        st.success("✅ 변환 완료")
        st.dataframe(result_df)
        to_excel_download(result_df, "결과_좌표→주소.xlsx")

def draw_kakao_map(lat, lon):
    map_html = f"""
    <iframe width="100%" height="400px"
        src="https://map.kakao.com/link/map/{lat},{lon}" 
        frameborder="0" allowfullscreen></iframe>
    """
    st.markdown("### 🗺️ 지도 미리보기")
    st.components.v1.html(map_html, height=400)


# ─────────────────────────────────────────────
# ✅ 템플릿 및 엑셀 다운로드 함수
# ─────────────────────────────────────────────
def generate_template(columns, filename):
    df = pd.DataFrame(columns=columns)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("📥 템플릿 다운로드", data=buffer.getvalue(), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def to_excel_download(df, filename):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("📤 결과 다운로드", data=buffer.getvalue(), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ─────────────────────────────────────────────
# ✅ 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_geocoding_tool()

