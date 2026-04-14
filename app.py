import streamlit as st
import pandas as pd
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="대물 수첩", layout="centered")

# 2. 데이터 로드 함수 (구역별 필터링 로딩)
DATA_FILE = "fishing_data.csv"

def get_region_data(region_name=None):
    try:
        df = pd.read_csv(DATA_FILE)
        if region_name and region_name != "전국":
            # 전체 데이터를 메모리에 다 올리지 않고 필요한 지역만 필터링
            return df[df['시도'] == region_name]
        return df
    except:
        return pd.DataFrame(columns=["날짜", "어종", "크기", "포인트명", "시도", "위도", "경도"])

# 3. 세션 상태 관리 (현재 어디를 보고 있는지 저장)
if 'current_region' not in st.session_state:
    st.session_state.current_region = "전국"

# 4. 앱 메인 레이아웃
st.title("🗺️ 스마트 조과 지도")

# 메뉴 구성
menu = st.sidebar.radio("메뉴", ["지도 탐색", "조과 기록", "전체 목록"])

if menu == "지도 탐색":
    # 상단 내비게이션
    if st.session_state.current_region != "전국":
        if st.button(f"⬅️ {st.session_state.current_region}에서 전국으로 돌아가기"):
            st.session_state.current_region = "전국"
            st.rerun()

    st.subheader(f"📍 현재 위치: {st.session_state.current_region}")

    # [백지도 대용 인터페이스]
    # 실제 그림 지도를 클릭하는 느낌을 주기 위해 버튼을 지도 모양으로 배치
    if st.session_state.current_region == "전국":
        st.write("상세 정보를 보려는 지역을 터치하세요.")
        
        # 한국 지도 모양의 간이 배치 (Grid 레이아웃)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("강원도"): st.session_state.current_region = "강원"; st.rerun()
            if st.button("충청도"): st.session_state.current_region = "충남"; st.rerun()
            if st.button("전라도"): st.session_state.current_region = "전남"; st.rerun()
        with col2:
            st.write("🇰🇷") # 중심
            if st.button("경기도"): st.session_state.current_region = "경기"; st.rerun()
            if st.button("경상도"): st.session_state.current_region = "경남"; st.rerun()
        with col3:
            if st.button("서울/인천"): st.session_state.current_region = "서울"; st.rerun()
            if st.button("제주도"): st.session_state.current_region = "제주"; st.rerun()

    else:
        # 특정 구역 진입 시 해당 구역 데이터만 로딩 (속도 최적화)
        region_df = get_region_data(st.session_state.current_region)
        
        if not region_df.empty:
            st.map(region_df[['위도', '경도']]) # 해당 구역 점들만 가볍게 표시
            st.table(region_df[['날짜', '어종', '크기', '포인트명']])
        else:
            st.info(f"{st.session_state.current_region}에 등록된 데이터가 없습니다.")

elif menu == "조과 기록":
    with st.form("record_form"):
        st.subheader("📝 새로운 조과 저장")
        sido = st.selectbox("지역 선택", ["서울", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
        fish = st.text_input("어종")
        size = st.number_input("크기(cm)")
        lat = st.number_input("위도", value=36.5, format="%.4f")
        lon = st.number_input("경도", value=127.5, format="%.4f")
        
        if st.form_submit_button("저장"):
            new_data = pd.DataFrame([[datetime.date.today(), fish, size, "포인트", sido, lat, lon]], 
                                     columns=["날짜", "어종", "크기", "포인트명", "시도", "위도", "경도"])
            all_df = get_region_data()
            pd.concat([all_df, new_data]).to_csv(DATA_FILE, index=False)
            st.success("데이터가 안전하게 저장되었습니다.")

else:
    st.dataframe(get_region_data(), use_container_width=True)
