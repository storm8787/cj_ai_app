#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import io
import datetime

# ✅ 네이버 API 키
NAVER_CLIENT_ID = st.secrets["NAVER_API"]["client_id"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_API"]["client_secret"]

# ✅ API 사용량 상태 저장
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0
LIMIT = 2900000

# ✅ 메인 함수
def run_geocoding_tool():
    st.header("📍 (업무지원) 주소-좌표 변환기")
    st.write("🔐 사용 API: 네이버 API (월 290만 건 이내 무료)")

    # ✅ 월 사용량 제한 안내
    if st.session_state.api_calls >= LIMIT:
        st.error("❌ 월 API 호출량이 290만 건을 초과하여 더 이상 요청할 수 없습니다.")
        return
    else:
        st.info(f"📈 현재 API 호출량: {st.session_state.api_calls:,} / {LIMIT:,}건")

    direction = st.radio("변환 방향을 선택하세요", ["주소 → 좌표", "좌표 → 주소"], horizontal=True)
    mode = st.radio("처리 방식을 선택하세요", ["건별 입력", "파일 업로드"], horizontal=True)

    if direction == "주소 → 좌표":
        if mode == "건별 입력":
            address = st.text_input("📌 주소를 입력하세요", placeholder="예: 충청북도 충주시 호암수청1로 29")
            if st.button("좌표 변환"):
                result = get_coords_from_address(address)
                if result["위도"] and result["경도"]:
                    st.success(f"📌 위도: {result['위도']} / 경도: {result['경도']}")
                else:
                    st.error("⚠️ 변환 실패: " + result["오류"])
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
                    results.append({"주소": addr, "위도": res["위도"], "경도": res["경도"], "오류": res["오류"]})
                result_df = pd.DataFrame(results)
                st.dataframe(result_df)
                download = to_excel(result_df)
                st.download_button("📥 결과 다운로드", data=download, file_name="result_addr_to_coord.xlsx")

    else:  # 좌표 → 주소
        if mode == "건별 입력":
            col1, col2 = st.columns(2)
            with col1:
                lat = st.text_input("위도")
            with col2:
                lon = st.text_input("경도")
            if st.button("주소 조회"):
                result = get_address_from_coords(lat, lon)
                if result["주소"]:
                    st.success("📍 주소: " + result["주소"])
                else:
                    st.warning("📭 결과 없음")
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
                    results.append({"위도": lat, "경도": lon, "주소": res["주소"], "오류": res["오류"]})
                result_df = pd.DataFrame(results)
                st.dataframe(result_df)
                download = to_excel(result_df)
                st.download_button("📥 결과 다운로드", data=download, file_name="result_coord_to_addr.xlsx")

# ✅ 주소 → 좌표 변환 (네이버 API)
def get_coords_from_address(address):
    st.session_state.api_calls += 1
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {"X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID, "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET}
    params = {"query": address}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        items = r.json().get("addresses", [])
        if items:
            item = items[0]
            return {"위도": item.get("y"), "경도": item.get("x"), "오류": ""}
        return {"위도": None, "경도": None, "오류": "주소 없음"}
    return {"위도": None, "경도": None, "오류": f"API 오류({r.status_code})"}

# ✅ 좌표 → 주소 변환 (네이버 API)
def get_address_from_coords(lat, lon):
    st.session_state.api_calls += 1
    url = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    headers = {"X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID, "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET}
    params = {"coords": f"{lon},{lat}", "output": "json", "orders": "roadaddr"}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        results = r.json().get("results", [])
        if results:
            addr = results[0].get("region", {})
            land = results[0].get("land", {})
            full = f"{addr.get('area1', {}).get('name', '')} {addr.get('area2', {}).get('name', '')} {addr.get('area3', {}).get('name', '')} {land.get('name', '')} {land.get('number1', '')}".strip()
            return {"주소": full, "오류": ""}
        return {"주소": None, "오류": "주소 없음"}
    return {"주소": None, "오류": f"API 오류({r.status_code})"}

# ✅ 템플릿 생성
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

# ✅ 엑셀 변환
def to_excel(df):
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output

