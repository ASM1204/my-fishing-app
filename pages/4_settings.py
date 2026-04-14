import streamlit as st
import pandas as pd

st.set_page_config(page_title="설정 및 관리", layout="wide")

st.title("⚙️ 포인트 및 장비 설정")
st.info("여기에서 등록한 정보는 조과 기록 시 선택 목록으로 나타납니다.")

# --- 데이터 로드/저장 함수 ---
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
        new_p = c1.text_input("새 포인트 이름", placeholder="예: 시화방조제 T-light")
        new_r = c2.selectbox("지역", ["서울", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
        if st.form_submit_button("포인트 등록"):
            if new_p:
                new_row = pd.DataFrame([{"포인트명": new_p, "지역": new_r}])
                pd.concat([p_df, new_row], ignore_index=True).to_csv("points.csv", index=False)
                st.rerun()

    st.table(p_df)
    if not p_df.empty and st.button("포인트 목록 초기화"):
        pd.DataFrame(columns=["포인트명", "지역"]).to_csv("points.csv", index=False)
        st.rerun()

# --- Tab 2: 장비 관리 ---
with tab2:
    st.subheader("보유 장비 기록")
    g_df = manage_data("gears.csv", ["구분", "장비명"])
    
    with st.form("add_gear"):
        c1, c2 = st.columns(2)
        g_type = c1.selectbox("구분", ["로드", "릴", "라인", "루어/미끼", "기타"])
        g_name = c2.text_input("모델명/제품명", placeholder="예: 스텔라 C3000HG")
        if st.form_submit_button("장비 등록"):
            if g_name:
                new_row = pd.DataFrame([{"구분": g_type, "장비명": g_name}])
                pd.concat([g_df, new_row], ignore_index=True).to_csv("gears.csv", index=False)
                st.rerun()

    st.table(g_df)
