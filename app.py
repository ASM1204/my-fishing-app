import streamlit as st
import pandas as pd

st.set_page_config(page_title="대물 수첩", layout="centered")

# --- CSS: 지도의 호버 효과 및 디자인 ---
st.markdown("""
<style>
    .korea-map { width: 100%; max-width: 500px; height: auto; }
    .region { fill: #f2f2f2; stroke: #333; stroke-width: 1.5; cursor: pointer; transition: fill 0.3s; }
    .region:hover { fill: #318ce7 !important; } /* 호버 시 파란색으로 변함 */
    .label { font-size: 14px; font-weight: bold; pointer-events: none; fill: #555; }
</style>
""", unsafe_allow_html=True)

# --- 데이터 로드 함수 ---
def get_data(region):
    # 실제 사용 시엔 여기서 csv 파일을 읽어 해당 지역 데이터만 반환
    return pd.DataFrame({"어종": ["감성돔"], "크기": [45]}, index=[0])

# --- 메인 로직 ---
st.title("🗺️ 스마트 백지도 터치 탐색")

if 'selected' not in st.session_state:
    st.session_state.selected = "전국"

if st.session_state.selected == "전국":
    st.subheader("지도를 직접 터치해서 지역을 선택하세요.")
    
    # SVG 백지도 (좌표를 직접 그려넣음)
    # 아래는 경기도와 강원도 영역을 예시로 만든 SVG입니다.
    map_svg = f"""
    <svg viewBox="0 0 400 500" class="korea-map">
        <path d="M100,100 L180,100 L180,180 L100,180 Z" class="region" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '경기'}}, '*')"/>
        <text x="120" y="145" class="label">경기</text>
        
        <path d="M185,80 L300,80 L300,180 L185,180 Z" class="region" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '강원'}}, '*')"/>
        <text x="220" y="135" class="label">강원</text>
        
        <text x="150" y="300" style="fill: #ccc;">(다른 지역도 동일하게 배치)</text>
    </svg>
    """
    
    # 클릭 감지를 위한 커스텀 컴포넌트 처리 (여기서는 쉬운 이해를 위해 버튼으로 대체 안내)
    # 실제 정밀 클릭은 'streamlit-echarts'나 'streamlit-folium'의 경량화 버전을 쓰는게 좋습니다.
    
    st.components.v1.html(map_svg, height=500)
    
    # 사용자님이 "직접 찍는" 느낌을 100% 만족시키기 위해 아래 지역 버튼을 지도 모양으로 배치합니다.
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("경기도 (지도 위 클릭 대신)"): st.session_state.selected = "경기"; st.rerun()
    with col3:
        if st.button("강원도 (지도 위 클릭 대신)"): st.session_state.selected = "강원"; st.rerun()

else:
    st.subheader(f"📍 {st.session_state.selected} 상세 포인트")
    if st.button("⬅️ 전국 지도로 돌아가기"):
        st.session_state.selected = "전국"
        st.rerun()
    
    # 선택된 지역의 데이터만 가볍게 출력
    st.write(get_data(st.session_state.selected))
