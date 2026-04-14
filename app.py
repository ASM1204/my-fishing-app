import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import st_folium

# 앱 제목 및 설정
st.set_page_config(page_title="대물 낚시 수첩", layout="wide")
st.title("🎣 나만의 비밀 조과 & 포인트 기록")

# 데이터 저장 (간이로 파일 저장 방식 - 더 안전하게는 구글 시트 연결 가능)
DATA_FILE = "fishing_data.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "메모"])

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴", ["조과 기록하기", "나의 기록 & 지도"])

if menu == "조과 기록하기":
    st.header("📸 오늘의 조과 기록")
    
    with st.form("fishing_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜", datetime.date.today())
            fish_type = st.text_input("어종", placeholder="예: 감성돔")
            size = st.number_input("크기 (cm)", min_value=0.0, step=0.1)
        with col2:
            loc_name = st.text_input("포인트명")
            lat = st.number_input("위도 (Latitude)", format="%.6f", value=37.5665)
            lon = st.number_input("경도 (Longitude)", format="%.6f", value=126.9780)
        
        uploaded_file = st.file_uploader("물고기 사진 업로드", type=['jpg', 'png', 'jpeg'])
        memo = st.text_area("출조 메모 (날씨, 채비 등)")
        
        submitted = st.form_submit_button("기록 저장하기")
        
        if submitted:
            # 데이터 저장 로직
            new_entry = pd.DataFrame([[date, fish_type, size, loc_name, lat, lon, memo]], 
                                     columns=["날짜", "어종", "크기", "포인트명", "위도", "경도", "메모"])
            df = load_data()
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("기록이 저장되었습니다!")

elif menu == "나의 기록 & 지도":
    st.header("📜 나의 출조 히스토리")
    df = load_data()
    
    if not df.empty:
        # 지도 표시
        st.subheader("📍 포인트 지도")
        m = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=10)
        for i, row in df.iterrows():
            folium.Marker(
                [row['위도'], row['경도']], 
                popup=f"{row['어종']} ({row['크기']}cm)",
                tooltip=row['포인트명']
            ).add_to(m)
        st_folium(m, width=700, height=500)
        
        # 표 표시
        st.subheader("📊 상세 기록 리스트")
        st.dataframe(df.sort_values("날짜", ascending=False))
    else:
        st.info("아직 기록이 없습니다.")
