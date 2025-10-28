import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="MBTI by Country Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 MBTI 유형별 국가 비교 대시보드")
st.write("업로드한 CSV 파일을 바탕으로 특정 MBTI 유형이 높은 국가 TOP 10을 시각적으로 탐색합니다.")

# =============================
# 파일 업로드
# =============================
uploaded_file = st.file_uploader("📂 MBTI 데이터 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 읽기
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ 파일이 성공적으로 업로드되었습니다!")
    except Exception as e:
        st.error(f"파일을 읽는 중 오류 발생: {e}")
        st.stop()

    # MBTI 타입 목록
    mbti_types = [
        'INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP',
        'ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP'
    ]

    # 국가 컬럼 자동 탐색
    country_col = None
    for col in df.columns:
        if "country" in col.lower():
            country_col = col
            break

    # MBTI 관련 컬럼 탐색 (각 유형이 열 이름으로 존재하는 경우)
    mbti_cols = [c for c in df.columns if c.upper() in mbti_types]

    # 검증
    if not country_col or not mbti_cols:
        st.error("⚠️ 'Country' 또는 MBTI 관련 열(INTJ~ESFP 등)을 찾을 수 없습니다.")
        st.dataframe(df.head())
        st.stop()

    # =============================
    # 사용자 선택
    # =============================
    selected_type = st.selectbox(
        "📊 분석할 MBTI 유형을 선택하세요",
        mbti_cols,
        index=0
    )

    # =============================
    # TOP 10 계산
    # =============================
    top10 = (
        df[[country_col, selected_type]]
        .dropna()
        .sort_values(by=selected_type, ascending=False)
        .head(10)
    )

    # =============================
    # Altair 시각화
    # =============================
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
        .properties(width=700, height=400)
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

    # =============================
    # 추가 기능
    # =============================
    with st.expander("📈 데이터 미리보기"):
        st.dataframe(df.head(20))

    with st.expander("🔍 사용 방법"):
        st.markdown("""
        1. CSV 파일에 **'Country'** 열과 **각 MBTI 유형(INTJ~ESFP)** 열이 있어야 합니다.  
        2. 업로드 후 분석할 유형을 선택하면 상위 10개 국가가 표시됩니다.  
        3. 그래프 막대 위에 마우스를 올리면 값이 표시됩니다.  
        """)

    st.caption("Made with ❤️ using Streamlit & Altair")

else:
    st.info("⬆️ 먼저 CSV 파일을 업로드해주세요. 예시 데이터에는 'Country', 'INTJ', 'INFP' 등의 열이 포함되어야 합니다.")
