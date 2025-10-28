import streamlit as st
from PyPDF2 import PdfReader
import base64
from io import BytesIO
import time

# --- 초기 설정 ---
st.set_page_config(page_title="모의고사 앱", layout="wide")

# --- 세션 상태 초기화 ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "subject" not in st.session_state:
    st.session_state.subject = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "time_left" not in st.session_state:
    st.session_state.time_left = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# --- PDF → 이미지 변환 함수 (PyMuPDF 이용) ---
def pdf_to_images(pdf_bytes):
    import fitz  # PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for i in range(len(doc)):
        pix = doc[i].get_pixmap()
        img = BytesIO(pix.tobytes("png"))
        images.append(img)
    return images

# --- 홈 페이지 ---
if st.session_state.page == "home":
    st.title("📘 모의고사 시작하기")

    subject = st.radio("과목을 선택하세요", ["국어", "수학"])
    uploaded_file = st.file_uploader("모의고사 PDF 업로드", type=["pdf"])

    if uploaded_file and st.button("시험 시작"):
        st.session_state.subject = subject
        st.session_state.pdf_bytes = uploaded_file.read()
        st.session_state.images = pdf_to_images(st.session_state.pdf_bytes)

        # 과목별 설정
        st.session_state.num_questions = 45 if subject == "국어" else 30
        st.session_state.time_left = 80 * 60 if subject == "국어" else 100 * 60
        st.session_state.start_time = time.time()
        st.session_state.page = "exam"
        st.rerun()

# --- 시험 페이지 ---
elif st.session_state.page == "exam":
    import math
    from datetime import timedelta

    # 1초마다 새로고침 (타이머 실시간 반영)
    st_autorefresh = st.experimental_rerun
    count = st.experimental_get_query_params()
    st_autorefresh = st.experimental_rerun
    st_autorefresh_interval = st.experimental_data_editor

    st_autorefresh = st.experimental_rerun

    # 타이머 업데이트
    elapsed = time.time() - st.session_state.start_time
    st.session_state.time_left = max(0, (80*60 if st.session_state.subject == "국어" else 100*60) - int(elapsed))

    if st.session_state.time_left <= 0:
        st.session_state.page = "result"
        st.rerun()

    # 1초마다 리프레시
    st_autorefresh = st.experimental_rerun
    st_autorefresh = st_autorefresh  # dummy to avoid lint

    st_autorefresh(interval=1000, key="timer_refresh")

    st.title(f"📝 {st.session_state.subject} 모의고사")

    col1, col2 = st.columns([4, 1])

    with col1:
        start = st.session_state.current_page
        end = start + 2
        for img in st.session_state.images[start:end]:
            st.image(img, use_container_width=True)

        col_a, col_b = st.columns(2)
        if col_a.button("⬅ 이전"):
            if st.session_state.current_page > 0:
                st.session_state.current_page -= 2
                st.rerun()
        if col_b.button("다음 ➡"):
            if st.session_state.current_page + 2 < len(st.session_state.images):
                st.session_state.current_page += 2
                st.rerun()

    with col2:
        st.subheader("OMR 서랍")
        st.write(f"({st.session_state.num_questions}문항)")

        for i in range(1, st.session_state.num_questions + 1):
            st.session_state.answers[i] = st.number_input(
                f"{i}번", min_value=1, max_value=5, step=1,
                value=st.session_state.answers.get(i, 1),
                key=f"ans_{i}"
            )

        # 타이머 표시
        minutes = st.session_state.time_left // 60
        seconds = st.session_state.time_left % 60
        st.metric("남은 시간", f"{minutes:02d}:{seconds:02d}")

        if st.button("시험 종료"):
            st.session_state.page = "result"
            st.rerun()

# --- 결과 페이지 ---
elif st.session_state.page == "result":
    st.title("📊 결과 확인")

    st.write("OMR 입력 결과:")
    st.write(st.session_state.answers)

    st.success("시험이 종료되었습니다. 수고하셨습니다! 👏")

    if st.button("처음으로 돌아가기"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
