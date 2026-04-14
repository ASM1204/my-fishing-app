import streamlit as st

# 메인 설정
st.set_page_config(page_title="대물 낚시 수첩", layout="centered")

st.title("🗺️ 낚시 포인트 스마트 백지도")
st.success("서버가 정상적으로 작동 중입니다! 왼쪽 사이드바에서 메뉴를 선택하세요.")

# 세션 상태 초기화
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "전국"

st.write(f"현재 선택된 지역: {st.session_state.selected_region}")
