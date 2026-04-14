import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd

st.set_page_config(page_title="대물 낚시 수첩", layout="centered")

st.title("🗺️ 낚시 포인트 스마트 백지도")

# --- 데이터 로드 (지도에 표시할 통계용) ---
try:
    df = pd.read_csv("fishing_data.csv")
except:
    df = pd.DataFrame()

# 세션 상태: 현재 선택된 지역 관리
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "전국"

# --- 1. 전국 지도 모드 ---
if st.session_state.selected_region == "전국":
    st.subheader("탐색할 지역을 직접 터치하세요.")
    
    # 지역별 데이터 개수 계산 (지도에 시각화하기 위함)
    region_counts = []
    if not df.empty and '포인트' in df.columns:
        # 설정(points.csv)과 연동하여 지역 정보 매칭 (고급 기능용)
        try:
            points_info = pd.read_csv("points.csv")
            df_with_region = df.merge(points_info, left_on='포인트', right_on='포인트명', how='left')
            counts = df_with_region['지역'].value_counts()
            for reg, val in counts.items():
                region_counts.append({"name": f"{reg}도" if "제주" not in reg and "시" not in reg else reg, "value": int(val)})
        except:
            pass

    options = {
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}개의 기록"},
        "visualMap": {
            "min": 0,
            "max": 10,
            "left": "left",
            "top": "bottom",
            "text": ["많음", "적음"],
            "calculable": True,
            "inRange": {"color": ["#fdfdfd", "#318ce7"]}
        },
        "series": [{
            "type": "map",
            "map": "SouthKorea",
            "label": {"show": True, "fontSize": 10},
            "itemStyle": {"borderColor": "#333"},
            "emphasis": {
                "itemStyle": {"areaColor": "#ffcc00"},
                "label": {"show": True, "color": "#000"}
            },
            "data": region_counts # 실제 조과가 있는 지역은 색상이 진하게 표시됨
        }]
    }

    clicked = st_echarts(
        options, 
        map_js_url="https://raw.githubusercontent.com/apache/echarts/master/test/data/map/json/south_korea.json",
        height="550px",
    )

    if clicked:
        # 클릭된 지역명 추출 및 세션 저장
        region = clicked if isinstance(clicked, str) else clicked.get('name')
        if region:
            st.session_state.selected_region = region
            st.rerun()

# --- 2. 지역 선택 후 화면 ---
else:
    st.header(f"📍 {st.session_state.selected_region} 지역 탐색")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ 전국 지도로 돌아가기"):
            st.session_state.selected_region = "전국"
            st.rerun()
    with col2:
        # 이 버튼을 누르면 해당 지역으로 필터링된 조회 페이지로 이동한다는 느낌을 줌
        if st.button("📜 이 지역 기록만 보기"):
            st.switch_page("pages/2_view.py")

    st.markdown("---")
    
    # 해당 지역의 포인트 목록 보여주기
    try:
        p_df = pd.read_csv("points.csv")
        # '경기' 클릭 시 '경기도' 혹은 '경기' 포함 데이터 필터링
        target = st.session_state.selected_region.replace("도", "").replace("특별자치시", "").replace("광역시", "").strip()
        local_points = p_df[p_df['지역'].str.contains(target)]
        
        if not local_points.empty:
            st.subheader(f"🏠 등록된 {st.session_state.selected_region} 포인트")
            for _, p_row in local_points.iterrows():
                st.info(f"📍 {p_row['포인트명']}")
        else:
            st.write(f"아직 {st.session_state.selected_region}에 등록된 포인트가 없습니다.")
            if st.button("➕ 포인트 등록하러 가기"):
                st.switch_page("pages/4_settings.py")
    except:
        st.write("포인트 정보를 불러올 수 없습니다. '설정'에서 포인트를 먼저 등록해주세요.")

st.sidebar.markdown("---")
st.sidebar.write(f"**현재 접속 지역:** {st.session_state.selected_region}")
