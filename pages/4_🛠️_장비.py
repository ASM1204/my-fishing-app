import streamlit as st
import pandas as pd

# 페이지 설정 및 사이드바 제거
st.set_page_config(page_title="낚's - 장비", layout="centered")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapseButton"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 상단 홈 버튼
if st.button("🏠 HOME으로 가기"):
    st.switch_page("app.py")

st.markdown("---")
st.title("🛠️ 장비 및 포인트 관리")

def manage_data(file_name, columns):
    try:
        return pd.read_csv(file_name)
    except:
        return pd.DataFrame(columns=columns)

tab1, tab2 = st.tabs(["📍 자주 가는 포인트", "🎣 나의 장비고"])

# --- Tab 1: 포인트 관리 ---
with tab1:
    st.subheader("나만의 포인트 목록")
    p_df = manage_data("points.csv", ["포인트명", "지역"])
    
    with st.form("add_point"):
        c1, c2 = st.columns(2)
        new_p = c1.text_input("새 포인트 이름", placeholder="예: 시화방조제")
        new_r = c2.selectbox("지역", ["서울", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
        if st.form_submit_button("포인트 등록"):
            if new_p:
                new_row = pd.DataFrame([{"포인트명": new_p, "지역": new_r}])
                p_df = pd.concat([p_df, new_row], ignore_index=True)
                p_df.to_csv("points.csv", index=False)
                st.success(f"'{new_p}' 등록 완료!")
                st.rerun()

    st.dataframe(p_df, use_container_width=True)
    if not p_df.empty:
        if st.button("📍 포인트 목록 전체 삭제"):
            pd.DataFrame(columns=["포인트명", "지역"]).to_csv("points.csv", index=False)
            st.rerun()

# --- Tab 2: 장비 관리 ---
with tab2:
    st.subheader("보유 장비 기록")
    g_df = manage_data("gears.csv", ["구분", "장비명"])
    
    with st.form("add_gear"):
        c1, c2 = st.columns(2)
        g_type = c1.selectbox("구분", ["로드", "릴", "라인", "루어/미끼", "기타"])
        g_name = c2.text_input("모델명/제품명", placeholder="예: 스텔라 C3000")
        if st.form_submit_button("장비 등록"):
            if g_name:
                new_row = pd.DataFrame([{"구분": g_type, "장비명": g_name}])
                g_df = pd.concat([g_df, new_row], ignore_index=True)
                g_df.to_csv("gears.csv", index=False)
                st.success(f"'{g_name}' 등록 완료!")
                st.rerun()

    st.dataframe(g_df, use_container_width=True)
    if not g_df.empty:
        if st.button("🎣 장비 목록 전체 삭제"):
            pd.DataFrame(columns=["구분", "장비명"]).to_csv("gears.csv", index=False)
            st.rerun()
