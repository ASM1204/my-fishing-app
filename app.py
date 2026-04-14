import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import datetime

# 기본 설정
st.set_page_config(page_title="대물 낚시 수첩", layout="wide")

# --- 데이터 로드 및 저장 함수 ---
DATA_FILE = "fishing_data.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "시도"])

# --- 한국 시도 경계 데이터 (무료 공개 JSON) ---
KOREA_SIDO_URL = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo.json"

# --- 메인 로직 ---
st.title("🎣 낚시 조과 & 스마트 포인트 앱")

menu = st.sidebar.selectbox("메뉴 선택", ["전체지도 탐색", "조과 기록하기", "나의 기록 히스토리"])

# 1. 전체지도 탐색 (드릴 다운 기초)
if menu == "전체지도 탐색":
    st.header("🗺️ 대한민국 지역별 포인트")
    st.info("지도의 시도 지역을 클릭하면 해당 지역으로 집중합니다.")

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles="cartodbpositron")

    # 시도 경계 레이어 추가
    try:
        response = requests.get(KOREA_SIDO_URL)
        sido_geo = response.json()
        
        folium.GeoJson(
            sido_geo,
            name="korea_sido",
            style_function=lambda x: {
                'fillColor': '#f9f9f9',
                'color': '#333333',
                'weight': 1,
                'fillOpacity': 0.4,
            },
            highlight_function=lambda x: {'weight': 3, 'fillColor': '#318ce7', 'fillOpacity': 0.6},
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['지역명:'])
        ).add_to(m)
    except:
        st.error("지도 데이터를 불러오지 못했습니다.")

    # 기존 저장된 포인트들 지도에 표시
    df = load_data()
    for _, row in df.iterrows():
        folium.Marker(
            [row['위도'], row['경도']],
            popup=f"{row['어종']} ({row['크기']}cm)",
            icon=folium.Icon(color="blue", icon="fish", prefix="fa")
        ).add_to(m)

    # 지도 화면 출력 및 클릭 감지
    map_data = st_folium(m, width="100%", height=600)

    # 클릭 시 동작
    if map_data['last_active_drawing']:
        selected_name = map_data['last_active_drawing']['properties']['name']
        st.subheader(f"📍 {selected_name} 지역 상세 보기")
        st.write(f"현재 {selected_name} 지역의 포인트들을 필터링 중입니다...")
        # 여기서 하위 행정구역(시군구) GeoJSON을 연결하면 다음 단계로 넘어갑니다.

# 2. 조과 기록하기
elif menu == "조과 기록하기":
    st.header("📝 오늘의 조과 남기기")
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜", datetime.date.today())
            fish = st.text_input("어종")
            size = st.number_input("크기(cm)", min_value=0.0)
        with col2:
            point_name = st.text_input("포인트 별명")
            lat = st.number_input("위도", format="%.6f", value=36.5)
            lon = st.number_input("경도", format="%.6f", value=127.5)
        
        memo = st.text_area("메모")
        submitted = st.form_submit_button("저장하기")
        
        if submitted:
            new_data = pd.DataFrame([[date, fish, size, point_name, lat, lon, "미분류"]], 
                                     columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "시도"])
            df = load_data()
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("저장 완료!")

# 3. 기록 히스토리
elif menu == "나의 기록 히스토리":
    st.header("📜 저장된 모든 기록")
    df = load_data()
    st.dataframe(df, use_container_width=True)
