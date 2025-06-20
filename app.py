
import streamlit as st
from pydub import AudioSegment
import numpy as np
import os
import tempfile

st.set_page_config(page_title="문장 단위 오디오 분리", layout="wide")
st.title("🎧 Welcome to Betia - 문장 단위 오디오 분리 도구")

uploaded_audio = st.file_uploader("전체 오디오 파일(MP3)", type=["mp3"])
uploaded_script = st.file_uploader("문장 리스트(.txt)", type=["txt"])

if uploaded_audio and uploaded_script:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tf_audio:
        tf_audio.write(uploaded_audio.read())
        audio_path = tf_audio.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tf_txt:
        tf_txt.write(uploaded_script.read())
        script_path = tf_txt.name

    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) / 1000  # in seconds

    with open(script_path, "r", encoding="utf-8") as f:
        script_lines = [line.strip() for line in f.readlines() if line.strip()]

    st.markdown(f"**총 문장 수:** {len(script_lines)} / **오디오 길이:** {duration:.2f}초")

    default_starts = np.linspace(0, duration, len(script_lines) + 1)[:-1]
    starts = []

    st.markdown("### ⏱️ 문장 시작 시간 수동 조정")
    for i, (line, default_start) in enumerate(zip(script_lines, default_starts)):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input(f"{i+1:02d}. {line}", value=line, key=f"text_{i}")
        with col2:
            start_time = st.number_input("시작 (초)", min_value=0.0, max_value=float(duration), step=0.1, value=float(round(default_start, 2)), key=f"start_{i}")
            starts.append(start_time)

    if st.button("🎬 문장별 오디오 파일로 분할 및 다운로드"):
        out_dir = tempfile.mkdtemp()
        for i in range(len(script_lines)):
            start = int(starts[i] * 1000)
            end = int(starts[i+1] * 1000) if i < len(script_lines) - 1 else len(audio)
            chunk = audio[start:end]
            out_path = os.path.join(out_dir, f"sentence_{i+1:02d}.mp3")
            chunk.export(out_path, format="mp3")

        import shutil
        zip_path = shutil.make_archive(out_dir, 'zip', out_dir)
        with open(zip_path, "rb") as f:
            st.download_button("📦 다운로드: 분할된 문장 ZIP", f, file_name="split_sentences.zip")
