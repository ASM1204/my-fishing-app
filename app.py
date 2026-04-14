import streamlit as st
from streamlit_echarts import st_echarts, dict_to_json
import pandas as pd

st.set_page_config(page_title="대물 낚시 수첩", layout="centered")

st.title("🗺️ 낚시 포인트 스마트 백지도")

# --- 데이터 로드 기능 ---
def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return pd.DataFrame()

df = load_data("fishing_data.csv")
points_df = load_data("points.csv")

# 세션 상태 관리
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "전국"

# --- 1. 전국 지도 화면 ---
if st.session_state.selected_region == "전국":
    st.subheader("탐색할 지역을 직접 터치하세요.")

    # 지도 데이터 (SouthKorea라는 이름으로 등록될 데이터)
    options = {
        "tooltip": {"trigger": "item", "formatter": "{b}"},
        "series": [{
            "type": "map",
            "map": "SouthKorea", # register_map으로 등록할 이름과 일치해야 함
            "label": {"show": True, "fontSize": 10},
            "itemStyle": {"areaColor": "#fdfdfd", "borderColor": "#333"},
            "emphasis": {
                "itemStyle": {"areaColor": "#318ce7"},
                "label": {"show": True, "color": "#fff"}
            },
            "data": [
                {"name": "경기도"}, {"name": "강원도"}, {"name": "충청북도"},
                {"name": "충청남도"}, {"name": "전라북도"}, {"name": "전라남도"},
                {"name": "경상북도"}, {"name": "경상남도"}, {"name": "제주특별자치도"},
                {"name": "서울특별시"}, {"name": "부산광역시"}, {"name": "대구광역시"},
                {"name": "인천광역시"}, {"name": "광주광역시"}, {"name": "대전광역시"},
                {"name": "울산광역시"}, {"name": "세종특별자치시"}
            ]
        }]
    }

    # 지도를 표시하는 가장 안전한 방법 (JsCode 사용 대신 기본 기능 활용)
    # 에러가 났던 map_js_url을 제거하고 기본 맵 컴포넌트 호출
    try:
        # map_js_url 대신 라이브러리에서 권장하는 방식으로 지도 데이터 호출
        clicked = st_echarts(
            options=options,
            map_js_url="https://raw.githubusercontent.com/apache/echarts/master/test/data/map/json/south_korea.json",
            height="550px",
            key="korea_map_main"
        )

        if clicked:
            # 클릭 데이터 처리
            res = clicked if isinstance(clicked, str) else clicked.get('name')
            if res:
                st.session_state.selected_region = res
                st.rerun()
    except Exception as e:
        # 지도가 안 뜰 경우를 대비한 비상용 버튼 메뉴
        st.warning("지도 로딩 중입니다... 아래 버튼으로도 지역 선택이 가능합니다.")
        cols = st.columns(3)
        regions = ["경기", "강원", "충남", "전남", "경남", "제주"]
        for i, r in enumerate(regions):
            if cols[i % 3].button(r, use_container_width=True):
                st.session_state.selected_region = r
                st.rerun()

# --- 2. 상세 화면 ---
else:
    st.header(f"📍 {st.session_state.selected_region} 탐색")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ 전국 지도로 돌아가기"):
            st.session_state.selected_region = "전국"
            st.rerun()
    with col2:
        if st.button("📜 이 지역 기록 보기"):
            st.switch_page("pages/2_view.py")

    st.markdown("---")
    
    if not points_df.empty:
        short_name = st.session_state.selected_region[:2]
        local_points = points_df[points_df['지역'].str.contains(short_name)]
        if not local_points.empty:
            st.subheader(f"🏠 등록된 {st.session_state.selected_region} 포인트")
            for _, p_row in local_points.iterrows():
                st.info(f"📍 {p_row['포인트명']}")
        else:
            st.write("등록된 포인트가 없습니다.")
    else:
        st.info("'설정' 페이지에서 포인트를 먼저 등록해주세요.")

st.sidebar.write(f"**현재 위치:** {st.session_state.selected_region}")
