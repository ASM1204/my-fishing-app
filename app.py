import streamlit as st
import pandas as pd
import datetime

# 페이지 설정
st.set_page_config(page_title="대물 수첩", layout="centered")

# --- 데이터 관리 (초간결) ---
DATA_FILE = "fishing_data.csv"

def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        # 위도/경도 데이터가 숫자인지 확인
        df['lat'] = pd.to_numeric(df['위도'], errors='coerce')
        df['lon'] = pd.to_numeric(df['경도'], errors='coerce')
        return df.dropna(subset=['lat', 'lon'])
    except:
        return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "lat", "lon"])

# --- 앱 메인 ---
st.title("🎣 초스피드 낚시수첩")

# 메뉴를 상단 라디오 버튼으로 변경 (사이드바보다 빠름)
menu = st.radio("메뉴", ["📍 지도보기", "📝 기록하기", "📜 목록"], horizontal=True)

df = load_data()

if menu == "📍 지도보기":
    st.subheader("내 포인트 분포")
    if not df.empty:
        # Streamlit 내장 지도는 Folium보다 압도적으로 빠릅니다.
        # 한국 중심 좌표로 자동 포커싱됩니다.
        st.map(df, latitude='lat', longitude='lon', size=20, color='#ff4b4b')
    else:
        st.info("기록된 포인트가 없습니다. 먼저 기록해주세요!")
        # 데이터가 없을 땐 기본 한국 지도
        st.map(pd.DataFrame({'lat': [36.5], 'lon': [127.5]}))

elif menu == "📝 기록하기":
    with st.form("fast_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fish = st.text_input("어종")
            size = st.number_input("크기(cm)", value=0.0)
        with col2:
            lat = st.number_input("위도", value=36.5000, format="%.4f")
            lon = st.number_input("경도", value=127.5000, format="%.4f")
        
        point_name = st.text_input("포인트 별명")
        submitted = st.form_submit_button("번개 저장 ⚡")
        
        if submitted:
            new_data = pd.DataFrame([[datetime.date.today(), fish, size, point_name, lat, lon, lat, lon]], 
                                     columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "lat", "lon"])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("저장되었습니다!")
            st.rerun()

else:
    st.subheader("전체 기록")
    st.dataframe(df[["날짜", "어종", "크기", "포인트명"]], use_container_width=True)
