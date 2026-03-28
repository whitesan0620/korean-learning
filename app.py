import streamlit as st
from deep_translator import GoogleTranslator
import asyncio
import edge_tts
import os

st.set_page_config(page_title="韓文歌詞學習工具", layout="centered")

st.title("🎧 韓文歌詞學習工具")

# 👉 輸入歌詞
lyrics = st.text_area("請貼上韓文歌詞（每行一句）")

# 👉 初始化
if "current_text" not in st.session_state:
    st.session_state.current_text = ""

# 👉 語音函式
async def generate_voice(text, filename):
    communicate = edge_tts.Communicate(
        text,
        voice="ko-KR-SunHiNeural"
    )
    await communicate.save(filename)

# 👉 快取翻譯（核心優化）
@st.cache_data
def translate_lines(lines):
    result = []
    for line in lines:
        zh = GoogleTranslator(source='ko', target='zh-TW').translate(line)
        result.append((line, zh))
    return result

if lyrics:
    # 👉 分行
    lines = [line.strip() for line in lyrics.split("\n") if line.strip() != ""]

    # 👉 一次翻譯（只跑一次）
    translated_lines = translate_lines(lines)

    st.subheader("📜 歌詞列表（點擊播放）")

    # 👉 顯示歌詞
    for i, (ko, zh) in enumerate(translated_lines):
        if st.button(f"{i+1}. {ko} / {zh}", key=f"line_{i}"):
            st.session_state.current_text = ko

    st.write("---")

    # 👉 播放區
    if st.session_state.current_text != "":
        ko = st.session_state.current_text

        # 👉 找對應翻譯（不用再翻）
        zh = next((z for k, z in translated_lines if k == ko), "")

        st.subheader("🎧 正在播放")
        st.write(f"韓文：{ko}")
        st.write(f"中文：{zh}")

        filename = f"voice_{hash(ko)}.mp3"

        # 👉 不重複生成語音
        if not os.path.exists(filename):
            asyncio.run(generate_voice(ko, filename))

        st.audio(filename)
