import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd

st.set_page_config(page_title="대물 낚시 수첩", layout="centered")

# --- 앱 제목 ---
st.title("🗺️ 낚시 포인트 스마트 백지도")

# --- 세션 상태 관리 ---
if 'view' not in st.session_state:
    st.session_state.view = 'national'

# --- 1. 전국 지도 화면 ---
if st.session_state.view == 'national':
    st.subheader("탐색하고 싶은 지역을 직접 터치하세요.")

    # ECharts를 이용한 인터랙티브 백지도 설정
    options = {
        "tooltip": {"trigger": "item", "formatter": "{b}"},
        "series": [
            {
                "name": "대한민국",
                "type": "map",
                "map": "china", # 라이브러리 기본 맵 호출 (한국 데이터 포함된 버전으로 자동 매핑)
                "label": {"show": True},
                "itemStyle": {
                    "areaColor": "#f8f9fa",
                    "borderColor": "#333",
                    "borderWidth": 1
                },
                "emphasis": { # 호버(마우스 올렸을 때) 효과
                    "itemStyle": {"areaColor": "#318ce7"},
                    "label": {"show": True, "color": "#fff"}
                },
                "data": [
                    {"name": "경기도", "value": 1},
                    {"name": "강원도", "value": 2},
                    {"name": "전라남도", "value": 3},
                    # ... 나머지 시도 추가
                ]
            }
        ]
    }

    # 지도 출력 및 클릭 감지
    clicked_region = st_echarts(options, map_js_url="https://raw.githubusercontent.com/apache/echarts/master/test/data/map/json/south_korea.json", height="500px")

    if clicked_region:
        st.session_state.view = clicked_region
        st.rerun()

# --- 2. 상세 구역 화면 ---
else:
    st.header(f"📍 {st.session_state.view} 상세 데이터")
    if st.button("⬅️ 전국 지도로 돌아가기"):
        st.session_state.view = 'national'
        st.rerun()
    
    st.info(f"현재 {st.session_state.view}의 낚시 포인트들을 분석 중입니다.")
    # 여기에 해당 지역 CSV 필터링 코드 추가
