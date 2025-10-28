import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="MBTI by Country Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 MBTI 유형별 국가 비교 대시보드")
st.write("특정 MBTI 유형의 비율이 높은 국가 TOP 10을 시각적으로 탐색합니다.")

# ---- 데이터 불러오기 ----
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# ---- MBTI 컬럼 자동 감지 ----
mbti_types = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP',
              'ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']

country_col = None
for col in df.columns:
    if "country" in col.lower():
        country_col = col
        break

# MBTI 타입별 컬럼만 필터링
mbti_cols = [c for c in df.columns if c.upper() in mbti_types]

if not country_col or not mbti_cols:
    st.error("⚠️ 데이터에서 Country 컬럼 또는 MBTI 관련 컬럼을 찾을 수 없습니다.")
    st.stop()

# ---- 사용자 선택 ----
selected_type = st.selectbox(
    "📊 분석할 MBTI 유형을 선택하세요",
    mbti_cols,
    index=0
)

# ---- TOP 10 국가 계산 ----
top10 = (
    df[[country_col, selected_type]]
    .dropna()
    .sort_values(by=selected_type, ascending=False)
    .head(10)
)

# ---- 시각화 (Altair) ----
st.subheader(f"🏆 {selected_type} 유형이 높은 국가 TOP 10")

chart = (
    alt.Chart(top10)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X(f"{selected_type}:Q", title=f"{selected_type} 비율"),
        y=alt.Y(f"{country_col}:N", sort='-x', title="국가"),
        color=alt.Color(f"{selected_type}:Q", scale=alt.Scale(scheme='tealblues')),
        tooltip=[country_col, selected_type]
    )
    .properties(
        width=700,
        height=400
    )
)

text = chart.mark_text(
    align='left',
    baseline='middle',
    dx=5,
    color='black'
).encode(
    text=alt.Text(f"{selected_type}:Q", format=".2f")
)

st.altair_chart(chart + text, use_container_width=True)

# ---- 추가 기능 ----
with st.expander("📈 데이터 미리보기"):
    st.dataframe(df.head(20))

with st.expander("🔍 이 대시보드는 어떻게 작동하나요?"):
    st.markdown("""
    1. CSV 파일에서 **국가 이름**과 **각 MBTI 유형의 값**을 자동으로 인식합니다.  
    2. 사용자가 선택한 MBTI 유형의 값을 기준으로 상위 10개 국가를 계산합니다.  
    3. Altair를 이용해 세련된 바 차트를 표시합니다.  
    4. Streamlit Cloud에 바로 배포할 수 있으며, 추가 라이브러리 설치가 필요 없습니다.
    """)

st.caption("Made with ❤️ using Streamlit & Altair")
