import streamlit as st
from streamlit_echarts import st_echarts
import json

st.set_page_config(page_title="대물 낚시 수첩", layout="centered")

st.title("🗺️ 낚시 포인트 스마트 백지도")

# 세션 상태: 어느 지역을 보고 있는지 저장
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "전국"

# --- 1. 전국 지도 화면 ---
if st.session_state.selected_region == "전국":
    st.subheader("탐색할 지역을 직접 터치하세요.")

    # 한국 지도 데이터 설정 (더 안정적인 설정)
    options = {
        "tooltip": {"trigger": "item", "formatter": "{b}"},
        "series": [
            {
                "name": "대한민국",
                "type": "map",
                "map": "SouthKorea", # 지도 이름 설정
                "label": {"show": True, "fontSize": 10},
                "itemStyle": {"areaColor": "#f4f4f4", "borderColor": "#333"},
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
            }
        ]
    }

    # 지도 데이터 URL (공식 소스 활용)
    map_url = "https://raw.githubusercontent.com/apache/echarts/master/test/data/map/json/south_korea.json"

    # 지도 출력 및 클릭 감지 (에러 방지를 위해 설정 최적화)
    try:
        clicked = st_echarts(
            options, 
            map_js_url=map_url,
            height="550px",
        )

        # 클릭 시 지역 변경 (반환값이 딕셔너리 형태일 수 있어 안전하게 처리)
        if clicked:
            # 클릭된 객체에서 지역 이름 추출
            if isinstance(clicked, str):
                st.session_state.selected_region = clicked
            elif isinstance(clicked, dict) and 'name' in clicked:
                st.session_state.selected_region = clicked['name']
            st.rerun()
    except Exception as e:
        st.error(f"지도를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")

# --- 2. 상세 지역 화면 ---
else:
    st.header(f"📍 {st.session_state.selected_region} 상세")
    if st.button("⬅️ 전국 지도로 돌아가기"):
        st.session_state.selected_region = "전국"
        st.rerun()
    
    st.info(f"현재 {st.session_state.selected_region} 지역의 포인트 기록을 준비 중입니다.")
    # (이후 여기에 조과 기록 리스트를 넣으면 됩니다!)
