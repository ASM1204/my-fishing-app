import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
import json

st.set_page_config(page_title="낚's", layout="centered")

# 이모지를 활용한 세련된 제목
st.title("🎣 낚's : 스마트 조과 지도")

def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return pd.DataFrame()

df = load_data("fishing_data.csv")
points_df = load_data("points.csv")

if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "전국"

if st.session_state.selected_region == "전국":
    st.subheader("📍 탐색할 지역을 선택하세요")

    options = {
        "tooltip": {"trigger": "item", "formatter": "{b}"},
        "series": [{
            "type": "map",
            "map": "SouthKorea",
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

    try:
        clicked = st_echarts(
            options=options,
            map_js_url="https://raw.githubusercontent.com/apache/echarts/master/test/data/map/json/south_korea.json",
            height="550px",
            key="korea_map_main"
        )
        if clicked:
            res = clicked if isinstance(clicked, str) else clicked.get('name')
            if res:
                st.session_state.selected_region = res
                st.rerun()
    except:
        # 지도 로딩 실패 시 버튼 UI
        cols = st.columns(3)
        regions = ["경기", "강원", "충남", "전남", "경남", "제주", "서울", "충북", "전북"]
        for i, r in enumerate(regions):
            if cols[i % 3].button(r, use_container_width=True):
                st.session_state.selected_region = r
                st.rerun()

else:
    st.header(f"📍 {st.session_state.selected_region} 탐색 중")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ 전국 지도로 이동"):
            st.session_state.selected_region = "전국"
            st.rerun()
    with c2:
        if st.button("📜 이 지역 기록 보기"):
            st.switch_page("pages/2_view.py")

    st.markdown("---")
    
    if not points_df.empty:
        short_name = st.session_state.selected_region[:2]
        local_points = points_df[points_df['지역'].str.contains(short_name, na=False)]
        if not local_points.empty:
            st.subheader(f"🏠 등록된 {st.session_state.selected_region} 포인트")
            for _, p_row in local_points.iterrows():
                st.info(f"📍 {p_row['포인트명']}")
        else:
            st.write("등록된 포인트가 없습니다.")
    else:
        st.info("'설정'에서 포인트를 등록해주세요.")
