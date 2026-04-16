import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="조과 통계 분석", layout="wide")

st.title("📊 나의 낚시 데이터 분석")

try:
    df = pd.read_csv("fishing_data.csv")
    
    if df.empty:
        st.info("통계를 낼 데이터가 아직 없습니다. 조과를 먼저 기록해 주세요!")
    else:
        # 상단 요약 대시보드
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 출조 횟수", f"{len(df['날짜'].unique())}회")
        with col2:
            st.metric("총 마릿수", f"{int(df['마릿수'].sum())}마리")
        with col3:
            # 최대어 정보 찾기
            if not df[df['길이'] > 0].empty:
                max_row = df.loc[df['길이'].idxmax()]
                st.metric("나의 최대어", f"{max_row['어종']} ({max_row['길이']}cm)")
            else:
                st.metric("나의 최대어", "기록 없음")

        st.markdown("---")

        # 차트 영역
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("🎣 어떤 어종을 많이 잡았나?")
            # 어종별 마릿수 합계 계산
            fish_stats = df.groupby("어종")["마릿수"].sum().reset_index()
            fig_pie = px.pie(fish_stats, values="마릿수", names="어종", hole=0.3,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.subheader("📍 포인트별 조과 현황")
            # 포인트별 마릿수 합계
            point_stats = df.groupby("포인트")["마릿수"].sum().reset_index().sort_values("마릿수", ascending=False)
            fig_bar = px.bar(point_stats, x="포인트", y="마릿수", 
                             color="마릿수", color_continuous_scale="Blues")
            st.plotly_chart(fig_bar, use_container_width=True)

        # 상세 기록 테이블 (선택사항)
        with st.expander("📝 전체 데이터 요약 보기"):
            st.dataframe(df.drop(columns=['사진']), use_container_width=True)

except FileNotFoundError:
    st.warning("데이터 파일이 존재하지 않습니다.")
