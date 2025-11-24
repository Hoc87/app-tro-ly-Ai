import io
import re
from datetime import datetime

import docx
import google.generativeai as genai
import pandas as pd
import PyPDF2
import streamlit as st
from gtts import gTTS
from PIL import Image

from prompts import get_expert_prompt

# -------------------------------------------------------------------
# CẤU HÌNH CHUNG
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Rin.Ai - Siêu Trợ Lý AI",
    page_icon="💎",
    layout="wide",
)

current_model_name = "gemini-1.5-flash"


# -------------------------------------------------------------------
# HÀM HỖ TRỢ
# -------------------------------------------------------------------

def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        file_type = uploaded_file.type or ""
        file_name = uploaded_file.name.lower()

        # Ảnh
        if file_type.startswith("image"):
            return Image.open(uploaded_file)

        # PDF
        if file_type == "application/pdf" or file_name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text

        # CSV / Excel
        if (
            "excel" in file_type
            or "spreadsheet" in file_type
            or file_name.endswith(".csv")
            or file_name.endswith(".xlsx")
        ):
            if file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            return df.to_string(index=False)

        # Word
        if file_name.endswith(".docx"):
            d = docx.Document(uploaded_file)
            text = "\n".join(p.text for p in d.paragraphs)
            return text

        # Text thuần
        raw = uploaded_file.getvalue()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")

    except Exception as e:
        return f"Lỗi đọc file: {e}"


def clean_text_for_tts(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(
        r"###PROMPT_[23]D###.*?###END_PROMPT###",
        "",
        text,
        flags=re.DOTALL,
    )
    clean = clean.replace("**", "")
    clean = re.sub(r"`+", "", clean)
    clean = re.sub(r"\n{2,}", "\n", clean)
    return clean.strip()


def play_text_to_speech(text_content: str, speed_slow: bool = False):
    try:
        text_to_read = clean_text_for_tts(text_content)
        if len(text_to_read) < 5:
            return
        tts = gTTS(text=text_to_read, lang="vi", slow=speed_slow)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3")
        status = "🐢 Đang đọc chậm..." if speed_slow else "🐇 Đang đọc tốc độ thường..."
        st.caption(f"🔊 {status}")
    except Exception:
        pass


def generate_image_url(prompt: str) -> str:
    clean_prompt = prompt.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?nologo=true&model=turbo"


@st.cache_resource(show_spinner=False)
def get_available_models(api_key: str):
    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())
        names = [
            m.name
            for m in models
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        candidates = [
            n
            for n in names
            if "gemini" in n
            and (
                "1.5" in n
                or "2.0" in n
                or "2.5" in n
                or "pro" in n
                or "flash" in n
            )
        ]
        if not candidates:
            candidates = names or ["gemini-1.5-flash"]

        def sort_key(x: str):
            return (
                "flash" not in x.lower(),
                "pro" not in x.lower(),
                "2.5" not in x,
                "2.0" not in x,
                "1.5" not in x,
            )

        candidates.sort(key=sort_key)
        return candidates
    except Exception:
        return ["gemini-1.5-flash"]


def get_model(model_name: str):
    return genai.GenerativeModel(model_name)


# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/12222/12222588.png",
        width=80,
    )
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()

    # KEY
    st.subheader("🔑 Tài khoản & Cấu hình")
    key_option = st.radio(
        "Chế độ:",
        ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn"],
        label_visibility="collapsed",
    )

    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server chung")
        except Exception:
            st.error("❌ Chưa cấu hình Key chung trên server.")
    else:
        st.info("Nhập Google API Key:")
        st.markdown(
            "[👉 Bấm vào đây để lấy Key miễn phí](https://aistudio.google.com/app/apikey)"
        )
        final_key = st.text_input("Dán Key vào đây:", type="password")
        if final_key:
            st.success("✅ Đã nhận Key cá nhân")

    if final_key:
        available_models = get_available_models(final_key)
        selected_model_display = st.selectbox(
            "🧠 Chọn bộ não AI:",
            available_models,
            index=0,
        )
        current_model_name = selected_model_display
        st.caption(f"Đang dùng model: `{current_model_name}`")

    st.divider()

    # CÔNG CỤ MỞ RỘNG
    st.subheader("🔥 Công Cụ Mở Rộng")
    st.link_button(
        "🤖 Trợ Lý AI ChatGPT",
        "https://chatgpt.com/g/g-69004bb8428481918ecf4ade89a9216c-rin-ai-center-trung-tam-tro-ly-ai",
    )
    with st.expander("🌐 Google AI Tools (Full)"):
        st.link_button("💎 Gemini Chat", "https://gemini.google.com/")
        st.link_button("📚 NotebookLM", "https://notebooklm.google.com/")
        st.link_button("🛠️ AI Studio", "https://aistudio.google.com/")
        st.link_button(
            "🎨 ImageFX",
            "https://aitestkitchen.withgoogle.com/tools/image-fx",
        )
        st.link_button(
            "🎥 VideoFX",
            "https://aitestkitchen.withgoogle.com/tools/video-fx",
        )
        st.link_button(
            "🎵 MusicFX",
            "https://aitestkitchen.withgoogle.com/tools/music-fx",
        )

    with st.expander("📝 Văn phòng (Workspace)"):
        st.link_button("Google Docs", "https://docs.google.com/")
        st.link_button("Google Sheets", "https://sheets.google.com/")

    st.divider()

    # FILE UPLOAD TOÀN PHIÊN
    st.subheader("📎 Đính Kèm Tài Liệu (Toàn phiên)")
    uploaded_file = st.file_uploader(
        "Chọn file:",
        type=["png", "jpg", "jpeg", "pdf", "txt", "csv", "xlsx", "docx"],
        label_visibility="collapsed",
        key="sidebar_uploader",
    )
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        st.success(f"✅ Đã nhận: {uploaded_file.name}")

    st.divider()

    # MENU CHUYÊN GIA
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.selectbox(
        "Lĩnh vực hỗ trợ:",
        [
            "🏠 Trang Chủ & Giới Thiệu",
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "📰 Đọc Báo & Tóm Tắt Sách",
            "🎨 Thiết Kế & Media (Ảnh/Video/Voice)",
            "🖥️ Chuyên Gia Tin Học Văn Phòng (Office)",
            "🏗️ Kiến Trúc - Nội Thất - Xây Dựng",
            "🏛️ Trợ Lý Cán bộ Ủy ban (Xã/Phường/TP)",
            "🏛️ Dịch Vụ Hành Chính Công",
            "🎓 Giáo Dục & Đào Tạo",
            "🎥 Chuyên Gia Video Google Veo",
            "👔 Nhân Sự - Tuyển Dụng - CV",
            "⚖️ Luật - Hợp Đồng - Hành Chính",
            "💰 Kinh Doanh & Marketing",
            "🏢 Giám Đốc & Quản Trị (CEO)",
            "🛒 TMĐT (Shopee/TikTok Shop)",
            "💻 Lập Trình - Freelancer - Digital",
            "❤️ Y Tế - Sức Khỏe - Gym",
            "✈️ Du Lịch - Lịch Trình - Vi Vu",
            "🧠 Tâm Lý - Cảm Xúc - Tinh Thần",
            "🍽️ Nhà Hàng - F&B - Ẩm Thực",
            "📦 Logistic - Vận Hành - Kho Bãi",
