#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import io

VWORLD_API_KEY = st.secrets["VWORLD"]["KEY"]
NAVER_CLIENT_ID = st.secrets["NAVER_API"]["client_id"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_API"]["client_secret"]

def run_geocoding_tool():
    st.title("📍 주소-좌표 변환기")

    direction = st.radio("변환 방향", ["주소 → 좌표", "좌표 → 주소"], horizontal=True)

    if direction == "주소 → 좌표":
        address = st.text_input("📌 주소 입력", placeholder="예: 충청북도 충주시 으뜸로 21")
        if st.button("변환 실행"):
            result = get_coords_from_vworld(address)
            if result["위도"] and result["경도"]:
                st.success(f"📌 위도: {result['위도']} / 경도: {result['경도']}")
                
                if st.toggle("🗺️ 지도 보기"):
                    draw_naver_map(result["위도"], result["경도"])
            else:
                st.error("❌ 변환 실패: " + result["오류"])

    else:
        lat = st.text_input("위도", placeholder="예: 36.991")
        lon = st.text_input("경도", placeholder="예: 127.925")
        if st.button("주소 조회"):
            result = get_address_from_vworld(lat, lon)
            if result["주소"]:
                st.success("📍 주소: " + result["주소"])
                
                if st.toggle("🗺️ 지도 보기"):
                    draw_naver_map(lat, lon)
            else:
                st.warning("📭 결과 없음")

def get_coords_from_vworld(address):
    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getcoord",
        "key": VWORLD_API_KEY,
        "format": "json",
        "type": "ROAD",
        "address": address,
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        res = r.json()
        if res["response"]["status"] == "OK" and res["response"]["result"]:
            data = res["response"]["result"][0]["point"]
            return {"위도": data["y"], "경도": data["x"], "오류": ""}
        return {"위도": None, "경도": None, "오류": "주소 없음"}
    return {"위도": None, "경도": None, "오류": f"API 오류({r.status_code})"}

def get_address_from_vworld(lat, lon):
    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getaddress",
        "key": VWORLD_API_KEY,
        "format": "json",
        "type": "ROAD",
        "point": f"{lon},{lat}",
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        res = r.json()
        if res["response"]["status"] == "OK" and res["response"]["result"]:
            addr = res["response"]["result"][0]["text"]
            return {"주소": addr, "오류": ""}
        return {"주소": None, "오류": "주소 없음"}
    return {"주소": None, "오류": f"API 오류({r.status_code})"}

def draw_naver_map(lat, lon):
    map_html = f"""
    <iframe src="https://map.naver.com/v5/?c=14138040,{lat},17,0,0,0"
            width="100%" height="400" frameborder="0" allowfullscreen></iframe>
    """
    st.markdown("### 🗺️ 지도 미리보기")
    st.components.v1.html(map_html, height=400)

# 실행
if __name__ == "__main__":
    run_geocoding_tool()

