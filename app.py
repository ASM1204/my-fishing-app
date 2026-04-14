import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import datetime

# 앱 설정: 페이지를 넓게 쓰고 제목 설정
st.set_page_config(page_title="대물 낚시 수첩", layout="wide")

# --- 데이터 로드 함수 ---
DATA_FILE = "fishing_data.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        # 데이터 파일이 없으면 빈 표 생성
        return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "시도"])

# --- 캐싱(Caching) 사용: 지도 데이터를 한 번만 불러오도록 설정 (로딩 속도 핵심) ---
@st.cache_data
def get_korea_geo():
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo.json"
    return requests.get(url).json()

# --- 메인 화면 ---
st.title("🎣 낚시 조과 & 스마트 포인트")

menu = st.sidebar.selectbox("메뉴 선택", ["전체지도 탐색", "조과 기록하기", "나의 기록 보기"])

if menu == "전체지도 탐색":
    st.subheader("🗺️ 대한민국 지역별 포인트")
    
    # 1. 지도 초기 설정: 한국 중심(36.5, 127.5), 줌 레벨(7) 고정
    # min_zoom과 max_zoom을 설정해 세계지도로 나가는 것을 방지
    m = folium.Map(
        location=[36.5, 127.5], 
        zoom_start=7, 
        min_zoom=7, 
        max_zoom=14,
        tiles="cartodbpositron" # 가볍고 깨끗한 백지도 스타일
    )

    # 2. 지도 경계선 추가 (캐싱된 데이터 사용)
    try:
        sido_geo = get_korea_geo()
        folium.GeoJson(
            sido_geo,
            name="korea_sido",
            style_function=lambda x: {
                'fillColor': '#f8f9fa',
                'color': '#444444',
                'weight': 1.5,
                'fillOpacity': 0.3,
            },
            highlight_function=lambda x: {'weight': 3, 'fillColor': '#318ce7', 'fillOpacity': 0.5},
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['지역:'])
        ).add_to(m)
    except:
        st.warning("지도 경계 데이터를 불러오는 중입니다...")

    # 3. 저장된 낚시 포인트 표시
    df = load_data()
    for _, row in df.iterrows():
        folium.Marker(
            [row['위도'], row['경도']],
            popup=f"{row['어종']} ({row['크기']}cm)",
            icon=folium.Icon(color="blue", icon="fish", prefix="fa")
        ).add_to(m)

    # 4. 지도 출력 (가로 100% 꽉 차게)
    map_data = st_folium(m, width="100%", height=500)

    # 클릭 이벤트 처리
    if map_data['last_active_drawing']:
        region_name = map_data['last_active_drawing']['properties']['name']
        st.info(f"선택하신 지역: **{region_name}**")
        st.write(f"현재 {region_name} 근처의 낚시 기록들을 불러오고 있습니다.")

elif menu == "조과 기록하기":
    st.subheader("📝 오늘의 조과 남기기")
    # (이전 기록 코드와 동일)
    with st.form("fishing_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜", datetime.date.today())
            fish = st.text_input("어종")
            size = st.number_input("크기(cm)", min_value=0.0)
        with col2:
            point_name = st.text_input("포인트 별명")
            lat = st.number_input("위도", format="%.6f", value=36.5)
            lon = st.number_input("경도", format="%.6f", value=127.5)
        
        submitted = st.form_submit_button("저장하기")
        if submitted:
            new_data = pd.DataFrame([[date, fish, size, point_name, lat, lon, "미분류"]], 
                                     columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "시도"])
            df = load_data()
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("기록 완료!")

else:
    st.subheader("📜 나의 기록 보기")
    st.dataframe(load_data(), use_container_width=True)
