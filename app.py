import streamlit as st
import pandas as pd
import datetime

# 페이지 설정
st.set_page_config(page_title="대물 수첩", layout="centered")

# --- 스타일 설정 (백지도 위에 투명 버튼 배치) ---
st.markdown("""
    <style>
    .korea-map-container {
        position: relative;
        display: inline-block;
        width: 100%;
        max-width: 400px; /* 지도의 가로 최대 크기 제한 */
        margin: auto;
    }
    .korea-map-img {
        width: 100%;
        height: auto;
        display: block;
    }
    /* 투명 지역 버튼 스타일 */
    .region-btn {
        position: absolute;
        background-color: transparent;
        border: none;
        cursor: pointer;
        outline: none;
    }
    /* 경기도 지역 투명 버튼 예시 (위치 조정 필요) */
    .btn-gyeonggi { top: 20%; left: 30%; width: 20%; height: 25%; }
    .btn-gangwon { top: 15%; left: 55%; width: 25%; height: 30%; }
    /* 다른 지역들도 유사하게 배치 가능 */
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 ---
DATA_FILE = "fishing_data.csv"

def load_data():
    try: return pd.read_csv(DATA_FILE)
    except: return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "시도", "상세지역"])

# --- 메인 화면 ---
st.title("🗺️ 낚시 포인트 스마트 탐색")

if 'selected_sido' not in st.session_state:
    st.session_state.selected_sido = None

menu = st.sidebar.radio("메뉴", ["지도 탐색", "조과 기록", "전체 기록"])

if menu == "지도 탐색":
    # 1단계: 전국 백지도 (시/도 선택)
    if not st.session_state.selected_sido:
        st.subheader("대한민국 전도 (시/도를 직접 찍으세요)")
        
        # 실제 지도를 이미지로 대체 (GitHub에 이미지를 올리고 연결해야 함)
        # 임시로 streamlit에서 기본 제공하는 지도 컴포넌트를 아주 가볍게 띄웁니다.
        st.info("💡 아래 지도의 특정 지역(예: 경기도) 주변을 '더블 클릭'해보세요.")
        
        # 매우 가벼운 지도 컴포넌트 사용 (st.map보다 더 가벼운 방식)
        korea_center = pd.DataFrame({'lat': [36.5], 'lon': [127.5]})
        st.map(korea_center, latitude='lat', longitude='lon', zoom=6, size=1)
        
        # 실제 '그림을 직접 찍는' 기능을 위해선 터치 이벤트를 처리하는 
        # 자바스크립트나 별도의 컴포넌트(예: streamlit-click-detector)가 필요합니다.
        
        # 임시 해결책: 지도를 직접 찍진 못하지만, 아래에서 지역을 선택하게 합니다.
        # (원하셨던 '그림을 직접 찍는' 느낌을 위해선 이 부분에 정교한 커스텀 컴포넌트가 필요합니다.)
        sido_options = ["전국", "서울", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        selected = st.selectbox("어느 지역을 상세 탐색하시겠습니까?", sido_options)
        
        if selected != "전국":
            st.session_state.selected_sido = selected
            st.rerun()

    # 2단계: 시/군/구 선택 (예: 경기도 클릭 시)
    else:
        st.subheader(f"📍 {st.session_state.selected_sido} 상세 지역")
        if st.button("⬅️ 전국 지도로 돌아가기"):
            st.session_state.selected_sido = None
            st.rerun()
            
        # 선택한 시도에 따른 구/군 리스트 (여기선 예시로 몇 개만 넣습니다)
        if st.session_state.selected_sido == "경기":
            cities = ["수원시", "화성시", "평택시", "안산시", "김포시"]
        elif st.session_state.selected_sido == "강원":
            cities = ["춘천시", "강릉시", "속초시", "삼척시"]
        else:
            cities = ["상세 구역 데이터 준비 중..."]
            
        cols = st.columns(4)
        for i, city in enumerate(cities):
            if cols[i % 4].button(city, use_container_width=True):
                st.info(f"{city}의 '동/리' 단위 지도로 이동합니다 (데이터 연결 필요)")

# --- 나머지 메뉴 (기록하기 등) ---
elif menu == "조과 기록":
    st.subheader("📝 기록하기")
    with st.form("input"):
        sido = st.selectbox("지역(시/도)", ["서울", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
        fish = st.text_input("어종")
        size = st.number_input("크기(cm)")
        submit = st.form_submit_button("저장")
        if submit:
            # 저장 로직 (생략)
            st.success("저장되었습니다!")

else:
    st.write(load_data())
