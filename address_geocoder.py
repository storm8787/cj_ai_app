#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import io
import folium
from streamlit_folium import st_folium

from urllib.parse import quote_plus

KAKAO_API_KEY = st.secrets["KAKAO_API"]["KEY"]
JS_KEY = st.secrets["KAKAO_API"]["JS_KEY"]

# ✅ 행정동 중심좌표 DB (직접 수집한 것 기반)
dong_coords = {
    "주덕읍": ("36.9756382529379", "127.795607766653"),
    "살미면": ("36.9053897150325", "127.964612737336"),
    "수안보면": ("36.8472710272136", "127.994785817453"),
    "대소원면": ("36.977810921957", "127.81798438609"),
    "신니면": ("36.995573390012", "127.736394413436"),
    "노은면": ("37.0481450135857", "127.754137176945"),
    "앙성면": ("37.1091674050492", "127.750768224757"),
    "중앙탑면": ("37.028931544342", "127.857035068528"),
    "금가면": ("37.0430221614579", "127.924478732073"),
    "동량면": ("37.0263327303528", "127.963254082287"),
    "산척면": ("37.0816686531557", "127.9559645917"),
    "엄정면": ("37.0866781306916", "127.914877536217"),
    "소태면": ("37.1097895873743", "127.847739119082"),
    "성내.충인동": ("36.9734381778844", "127.933869282965"),
    "교현.안림동": ("36.9747966497151", "127.935282939261"),
    "교현2동": ("36.9814769299978", "127.929102109455"),
    "용산동": ("36.9642270579558", "127.938737856086"),
    "지현동": ("36.9682108608662", "127.932188386436"),
    "문화동": ("36.9716759115419", "127.925560081272"),
    "호암.직동": ("36.9529358203833", "127.933609911294"),
    "달천동": ("36.9601080580716", "127.903345363646"),
    "봉방동": ("36.9736601560487", "127.919281720775"),
    "칠금.금릉동": ("36.9821246699753", "127.919046610961"),
    "연수동": ("36.9867248377519", "127.934130527889"),
    "목행.용탄동": ("37.0115867558614", "127.917010287047"),
}

default_coords = ("36.991", "127.925")  # 충주시청 기준

# ─────────────────────────────────────────────
# ✅ 카카오 API 함수
# ─────────────────────────────────────────────
def get_coords_from_kakao(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        docs = r.json()["documents"]
        if docs:
            x = docs[0]["x"]
            y = docs[0]["y"]
            return {"위도": y, "경도": x, "정확도": "정좌표", "오류": ""}
        return {"위도": None, "경도": None, "정확도": "", "오류": "주소 없음"}
    return {"위도": None, "경도": None, "정확도": "", "오류": f"API 오류({r.status_code})"}

def get_coords_with_fallback(address):
    # 1차: 전체 주소로 시도
    result = get_coords_from_kakao(address)
    if result["위도"]:
        result["정확도"] = "정좌표"
        return result

    # 2차: 진짜 인근번지 보정 시도 (예: 31-3 → 31-2 → 31)
    import re
    match = re.search(r"(\d+)-(\d+)", address)
    if match:
        base = int(match.group(1))
        sub = int(match.group(2))
        for i in range(1, 4):  # 최대 3번만 시도
            new_sub = sub - i
            if new_sub < 0:
                break
            new_addr = re.sub(r"\d+-\d+", f"{base}-{new_sub}", address)
            result = get_coords_from_kakao(new_addr)
            if result["위도"]:
                result["정확도"] = f"인근번지 보정({base}-{new_sub})"
                return result
        # 단일번지로 재시도
        result = get_coords_from_kakao(address.replace(f"{base}-{sub}", str(base)))
        if result["위도"]:
            result["정확도"] = f"인근번지 보정({base})"
            return result

    # 3차: 행정동 기반 좌표 보정
    for dong, (lat, lon) in dong_coords.items():
        if dong in address:
            return {"위도": lat, "경도": lon, "정확도": "행정동 대표좌표", "오류": ""}

    # 4차: 시군구 중심 좌표
    lat, lon = default_coords
    return {"위도": lat, "경도": lon, "정확도": "시군구 대표좌표", "오류": ""}

def get_address_from_kakao(lat, lon):
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"x": lon, "y": lat}
    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        data = r.json()
        docs = data.get("documents", [])
        if docs:
            doc = docs[0]
            jibun = doc.get("address", {}).get("address_name")
            road_info = doc.get("road_address")
            road = road_info.get("address_name") if road_info else None

            if not jibun and not road:
                return {
                    "지번주소": None,
                    "도로명주소": None,
                    "오류": "주소정제 실패"
                }

            return {
                "지번주소": jibun,
                "도로명주소": road,
                "오류": ""
            }

        return {"지번주소": None, "도로명주소": None, "오류": "주소정제 실패"}

    return {"지번주소": None, "도로명주소": None, "오류": f"API 오류({r.status_code})"}

# ─────────────────────────────────────────────
# ✅ 지도 표시 함수(건별별)
# ─────────────────────────────────────────────
def draw_folium_map(lat, lon):
    try:
        # 문자열로 넘어왔을 경우를 대비해 float 변환
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        st.error("❌ 위도/경도 값이 유효하지 않습니다.")
        return

    # 지도 생성
    #m = folium.Map(location=[lat, lon], zoom_start=17)
    m = folium.Map(location=[lat, lon], zoom_start=17, tiles='CartoDB positron')

    folium.Marker([lat, lon], tooltip="📍 위치").add_to(m)

    # 지도를 스트림릿에 표시
    st_folium(m, width=1500, height=500, returned_objects=[])

# ─────────────────────────────────────────────
# ✅ 지도 표시 함수(파일별)
# ─────────────────────────────────────────────
def draw_folium_map_multiple(df):
    # ✅ 좌표값을 숫자로 강제 변환하고, 실패한 행은 제거
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")
    df = df.dropna(subset=["위도", "경도"])

    if df.empty:
        st.warning("⚠️ 유효한 좌표 데이터가 없어 지도를 생성할 수 없습니다.")
        return

    # ✅ 지도 생성 (초기 중심값은 의미 없음, fit_bounds로 덮어씀)
    m = folium.Map(location=[df["위도"].mean(), df["경도"].mean()], zoom_start=12, tiles="CartoDB positron")

    bounds = []  # 마커 경계 저장용
    for _, row in df.iterrows():
        try:
            lat = float(row["위도"])
            lon = float(row["경도"])

            # ✅ 주소가 없을 때도 가능한 범위 내에서 fallback
            addr = row.get("주소") or row.get("지번주소") or row.get("도로명주소") or ""

            folium.Marker([lat, lon], tooltip=addr).add_to(m)
            bounds.append([lat, lon])
        except Exception as e:
            print(f"🚨 마커 생성 중 오류: {e}")
            continue

    # ✅ 모든 마커를 포함하는 범위로 지도 줌 자동 조정
    if bounds:
        m.fit_bounds(bounds)

    st_folium(m, width=1500, height=500, key="map_multiple")

# ─────────────────────────────────────────────
# ✅ 주소 → 좌표 (건별)
# ─────────────────────────────────────────────
def handle_single_address_to_coords():
    address = st.text_input("📌 주소 입력", placeholder="예: 충청북도 충주시 으뜸로 21")

    if st.button("변환 실행", key="btn_convert_addr"):
        res = get_coords_with_fallback(address)
        if res["위도"]:
            msg = f"📌 위도: {res['위도']} / 경도: {res['경도']} ({res['정확도']})"
            st.success(msg)
            st.session_state.update(
                last_lat=res["위도"],
                last_lon=res["경도"],
                coord_msg=msg
            )
        else:
            st.error("❌ 변환 실패: " + res["오류"])

    if st.button("🗺️ 지도 보기", key="btn_show_map_addr") and st.session_state.get("last_lat"):
        lat = st.session_state["last_lat"]
        lon = st.session_state["last_lon"]
        draw_folium_map(lat, lon)
        st.info(st.session_state.get("coord_msg", ""))

# ─────────────────────────────────────────────
# ✅ 좌표 → 주소 (건별)
# ─────────────────────────────────────────────
def handle_single_coords_to_address():
    lat = st.text_input("위도", placeholder="예: 36.991")
    lon = st.text_input("경도", placeholder="예: 127.925")

    if st.button("주소 조회", key="btn_convert_coord"):
        res = get_address_from_kakao(lat, lon)

        jibun = res.get("지번주소", "")
        road = res.get("도로명주소", "")

        if jibun or road:
            st.success("📍 변환 결과")
            if road:
                st.write(f"🛣️ 도로명주소: {road}")
            if jibun:
                st.write(f"🏡 지번주소: {jibun}")

            st.session_state.update(
                last_lat=lat,
                last_lon=lon,
                coord_msg=f"도로명: {road}, 지번: {jibun}"
            )
        else:
            st.warning("📭 결과 없음")

    if st.button("🗺️ 지도 보기", key="btn_show_map_coord") and st.session_state.get("last_lat"):
        draw_folium_map(st.session_state["last_lat"], st.session_state["last_lon"])
        st.info(st.session_state.get("coord_msg", ""))

# ─────────────────────────────────────────────
# ✅ 파일 업로드용 주소 → 좌표 (핵심부만)
# ─────────────────────────────────────────────
def handle_file_address_to_coords():
    st.markdown("📥 템플릿 형식: 주소 컬럼 이름은 반드시 `주소`")
    generate_template(["주소"], "template_주소→좌표.xlsx")
    up = st.file_uploader("📂 파일 업로드", type="xlsx")
    if not up:
        return

    df = pd.read_excel(up)
    if "주소" not in df.columns:
        st.error("❌ '주소' 컬럼이 누락되었습니다.")
        return

    results = []
    for addr in df["주소"]:
        r = get_coords_with_fallback(addr)
        results.append({
            "주소": addr,
            "위도": r["위도"],
            "경도": r["경도"],
            "정확도": r["정확도"],
            "오류": r["오류"]
        })
    out_df = pd.DataFrame(results)
    st.dataframe(out_df)
    to_excel_download(out_df, "결과_주소→좌표.xlsx")

    if "show_multi_map" not in st.session_state:
        st.session_state["show_multi_map"] = False

    # 버튼 누르면 True 설정
    if st.button("🗺️ 지도 보기", key="btn_show_map_multi_addr"):
        valid_df = out_df.dropna(subset=["위도", "경도"])
        st.session_state["multi_map_df"] = valid_df
        st.session_state["show_multi_map"] = True

    # 버튼 누른 이후에만 지도 실행
    if st.session_state["show_multi_map"]:
        draw_folium_map_multiple(st.session_state["multi_map_df"])

# ─────────────────────────────────────────────
# ✅ 파일 업로드용 좌표 → 주소 (핵심부만)
# ─────────────────────────────────────────────
def handle_file_coords_to_address():
    st.markdown("📥 템플릿 형식: 위도/경도 컬럼 이름은 반드시 `위도`, `경도`")
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
            results.append({
                "위도": row["위도"],
                "경도": row["경도"],
                "지번주소": r.get("지번주소",""),
                "도로명주소": r.get("도로명주소",""),
                "오류": r["오류"]
            })
        result_df = pd.DataFrame(results)
        st.success("✅ 변환 완료")
        st.dataframe(result_df)
        to_excel_download(result_df, "결과_좌표→주소.xlsx")

        if "show_multi_map" not in st.session_state:
            st.session_state["show_multi_map"] = False

        # 버튼 누르면 True 설정
        if st.button("🗺️ 지도 보기", key="btn_show_map_multi_addr"):
            valid_df = result_df.dropna(subset=["위도", "경도"])

            # ✅ 디버깅 코드 (웹에 출력)
            st.markdown(f"📌 지도에 찍힐 좌표 수: **{len(valid_df)}**")
            st.dataframe(valid_df[["위도", "경도", "지번주소", "도로명주소"]])

            st.session_state["multi_map_df"] = valid_df
            st.session_state["show_multi_map"] = True

        # 버튼 누른 이후에만 지도 실행
        if st.session_state["show_multi_map"]:
            draw_folium_map_multiple(st.session_state["multi_map_df"])

def generate_template(columns, filename):
    df = pd.DataFrame(columns=columns)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("📥 템플릿 다운로드", data=buffer.getvalue(), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def to_excel_download(df, filename):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("📤 결과 다운로드", data=buffer.getvalue(), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def run_geocoding_tool():
    st.title("📍 주소-좌표 변환기")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔄 변환 방향")
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

# ✅ 실행
if __name__ == "__main__":
    run_geocoding_tool()

