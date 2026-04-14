# ... 앞부분 생략 (import 등)

# 저장된 포인트/장비 불러오기
try:
    point_list = pd.read_csv("points.csv")["포인트명"].tolist()
except:
    point_list = []

try:
    gear_list = pd.read_csv("gears.csv")["장비명"].tolist()
except:
    gear_list = []

# ... (중략) ...

with st.form("fishing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.date.today())
        # 텍스트 입력 대신 선택 상자로 변경 (목록이 없으면 직접 입력 가능하게 유지)
        if point_list:
            point = st.selectbox("포인트 선택", point_list)
        else:
            point = st.text_input("포인트 직접 입력")
            
        fish_type = st.text_input("어종")
# ... (이하 동일)
