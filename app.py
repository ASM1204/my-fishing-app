import streamlit as st
import pandas as pd
import datetime

# 페이지 설정
st.set_page_config(page_title="대물 수첩", layout="wide")

# --- 스타일 설정 (백지도 느낌) ---
st.markdown("""
    <style>
    .region-btn {
        display: inline-block;
        width: 100px;
        height: 60px;
        line-height: 60px;
        margin: 5px;
        text-align: center;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #f9f9f9;
        cursor: pointer;
        font-weight: bold;
    }
    .region-btn:hover { background-color: #e2e2e2; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 ---
DATA_FILE = "fishing_data.csv"

def load_data():
    try: return pd.read_csv(DATA_FILE)
    except: return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "시도", "상세지역"])

# --- 메인 로직 ---
st.title("🗺️ 낚시 포인트 스마트 탐색")

if 'view_level' not in st.session_state:
    st.session_state.view_level = 'national' # national -> city -> town
if 'selected_sido' not in st.session_state:
    st.session_state.selected_sido = None

menu = st.sidebar.radio("메뉴", ["지도 탐색", "조과 기록", "전체 기록"])

if menu == "지도 탐색":
    # 1단계: 전국 백지도 (시/도 선택)
    if st.session_state.view_level == 'national':
        st.subheader("대한민국 전도 (시/도를 선택하세요)")
        # 실제 지도를 그리는 대신, 클릭 가능한 구역을 배치합니다. (로딩 0초)
        sidos = ["서울", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        cols = st.columns(5)
        for i, sido in enumerate(sidos):
            if cols[i % 5].button(sido, use_container_width=True):
                st.session_state.selected_sido = sido
                st.session_state.view_level = 'city'
                st.rerun()

    # 2단계: 시/군/구 선택 (예: 경기도 클릭 시)
    elif st.session_state.view_level == 'city':
        st.subheader(f"📍 {st.session_state.selected_sido} 상세 지역")
        if st.button("⬅️ 뒤로가기"):
            st.session_state.view_level = 'national'
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
