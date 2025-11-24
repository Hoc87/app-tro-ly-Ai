import io
import re
from datetime import datetime

import google.generativeai as genai
import pandas as pd
import PyPDF2
import streamlit as st
from gtts import gTTS
from PIL import Image
import docx  # từ python-docx

# --- IMPORT FILE PROMPTS ---
try:
    from prompts import get_expert_prompt
except ImportError:
    st.error("⚠️ Lỗi: Không tìm thấy file 'prompts.py'. Hãy tạo file này cùng thư mục.")
    st.stop()

# =============================================================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ
# =============================================================================

st.set_page_config(
    page_title="Rin.Ai - Siêu Trợ Lý AI",
    page_icon="💎",
    layout="wide",
)


def process_uploaded_file(uploaded_file):
    """Đọc nội dung file upload (ảnh, PDF, Excel, CSV, DOCX, TXT...)."""
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

        # Word (DOCX)
        if file_name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            text = "\n".join(p.text for p in doc.paragraphs)
            return text

        # Text thường
        raw = uploaded_file.getvalue()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")

    except Exception as e:
        return f"Lỗi đọc file: {e}"


def clean_text_for_tts(text: str) -> str:
    """Làm sạch text để đọc TTS (loại bớt Markdown, prompt kỹ thuật)."""
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
    """Đọc text bằng gTTS, phát trực tiếp trên Streamlit."""
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
        # Không chặn app nếu TTS lỗi
        pass


def generate_image_url(prompt: str) -> str:
    """Tạo URL ảnh từ Pollinations dựa trên prompt tiếng Anh."""
    clean_prompt = prompt.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?nologo=true&model=turbo"


@st.cache_resource(show_spinner=False)
def get_available_models(api_key: str):
    """Lấy danh sách model khả dụng, ưu tiên Flash/Pro."""
    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())

        names = [
            m.name
            for m in models
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]

        # Ưu tiên: 1.5 / 2.0 Flash & Pro
        candidates = [
            n
            for n in names
            if "gemini" in n
            and ("1.5" in n or "2.0" in n or "2.5" in n or "pro" in n or "flash" in n)
        ]

        if not candidates:
            candidates = names or ["gemini-1.5-flash"]

        # Sắp xếp: Flash trước, Pro sau, 2.5 > 2.0 > 1.5
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
    """Tạo GenerativeModel đã cấu hình sẵn API key (genai.configure gọi trước)."""
    return genai.GenerativeModel(model_name)


# =============================================================================
# 2. SIDEBAR (THANH BÊN TRÁI)
# =============================================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/12222/12222588.png",
        width=80,
    )
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()

    # --- NHẬP KEY ---
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

    # --- CHỌN MODEL ---
    global current_model_name  # dùng biến toàn cục
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

    # --- MENU CÔNG CỤ THAM KHẢO ---
    st.subheader("🔥 Công Cụ Mở Rộng")
    st.link_button("🤖 Mở App ChatGPT", "https://chatgpt.com/")
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

    # --- UPLOAD FILE ---
    st.subheader("📎 Đính Kèm Tài Liệu")
    uploaded_file = st.file_uploader(
        "Chọn file:",
        type=["png", "jpg", "jpeg", "pdf", "txt", "csv", "xlsx", "docx"],
        label_visibility="collapsed",
    )
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        st.success(f"✅ Đã nhận: {uploaded_file.name}")

    st.divider()

    # --- MENU CHÍNH ---
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
            "📊 Kế Toán - Báo Cáo - Số Liệu",
            "🎤 Sự Kiện - MC - Hội Nghị",
            "🏠 Bất Động Sản & Xe Sang",
        ],
    )

# =============================================================================
# 3. LOGIC CHÍNH (MAIN APP)
# =============================================================================

# Nếu chưa có key và không phải trang giới thiệu => yêu cầu nhập
if not final_key and menu != "🏠 Trang Chủ & Giới Thiệu":
    st.warning("👋 Vui lòng nhập Google API Key bên tay trái để bắt đầu.")
    st.stop()

# Cấu hình Gemini (1 lần)
if final_key:
    genai.configure(api_key=final_key)

# --- TRANG CHỦ ---
if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            """
        ### 👋 Chào mừng đến với Rin.Ai PRO
        **Sản phẩm tâm huyết được phát triển bởi: _Mr. Học_**

        Rin.Ai là "Super App" tích hợp sức mạnh Google AI để:
        - Hỗ trợ công việc văn phòng, kinh doanh, marketing
        - Giúp học tập, nghiên cứu, luyện thi
        - Tự động hoá trên nền tảng Google (Docs, Sheets, Slides...)
        """
        )
        st.link_button(
            "👉 Chat Zalo với Mr. Học",
            "https://zalo.me/0901108788",
        )
    with col2:
        st.image(
            "https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg"
        )

# --- MODULE: ĐỌC TIN & TÓM TẮT SÁCH ---
elif menu == "📰 Đọc Báo & Tóm Tắt Sách":
    st.header("📰 Chuyên Gia Tri Thức & Tin Tức")
    today_str = datetime.now().strftime("%d/%m/%Y")

    task = st.radio(
        "Chế độ:",
        ["🔎 Tin Tức Thời Sự", "📚 Tóm tắt Sách/Tài liệu"],
        horizontal=True,
    )

    if task == "🔎 Tin Tức Thời Sự":
        topic = st.text_input(f"Nhập chủ đề tin tức ({today_str}):")
        if st.button("🔎 Phân tích tin tức"):
            if topic:
                with st.spinner(f"Đang phân tích bằng model {current_model_name}..."):
                    try:
                        model = get_model(current_model_name)
                        prompt = (
                            f"Hãy tóm tắt các tin tức mới nhất (nếu có thể) về chủ đề: {topic} "
                            f"tính đến ngày {today_str}. "
                            "Trình bày ngắn gọn, có bullet, và nếu có thể hãy gợi ý các từ khoá để người dùng tự tra cứu thêm."
                        )
                        res = model.generate_content(prompt)
                        text = res.text
                        st.success("✅ Kết quả tổng hợp:")
                        st.markdown(text)
                        play_text_to_speech(text)
                    except Exception as e:
                        st.error(f"Lỗi Model {current_model_name}: {e}")
                        st.info(
                            "💡 Mẹo: Hãy thử đổi sang model 'gemini-1.5-flash' ở thanh bên trái."
                        )
    else:
        st.subheader("📚 Tóm tắt tài liệu / sách")
        txt_input = st.text_area("Dán nội dung, hoặc chỉ cần upload file ở thanh bên trái:")
        content = file_content if file_content is not None else txt_input

        if st.button("📚 Tóm tắt") and content:
            with st.spinner(f"Đang tóm tắt bằng model {current_model_name}..."):
                try:
                    model = get_model(current_model_name)
                    if isinstance(content, Image.Image):
                        req = [
                            "Tóm tắt nội dung chính trong hình sau (nếu là trang sách/tài liệu):",
                            content,
                        ]
                    else:
                        req = [
                            f"Hãy tóm tắt nội dung sau thành 5–7 ý chính, dễ hiểu cho người Việt:\n\n{content}"
                        ]
                    res = model.generate_content(req)
                    text = res.text
                    st.markdown(text)
                    play_text_to_speech(text)
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# --- MODULE: MEDIA (ẢNH / VIDEO PROMPT / VOICE) ---
elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
    st.header("🎨 Studio Đa Phương Tiện – Rin.Ai")
    mode = st.radio(
        "Công cụ:",
        ["🖼️ Tạo Ảnh", "🎬 Tạo Prompt Video", "🎙️ Voice AI"],
        horizontal=True,
    )

    # ẢNH
    if mode == "🖼️ Tạo Ảnh":
        desc = st.text_area("Nhập mô tả HÌNH ẢNH (tiếng Việt):")
        if st.button("🎨 Vẽ Ngay") and desc:
            with st.spinner("Đang chuyển prompt sang tiếng Anh & tạo ảnh..."):
                try:
                    model = get_model(current_model_name)
                    p_en = model.generate_content(
                        f"Translate this image prompt to natural English, concise but detailed: {desc}"
                    ).text
                    img_url = generate_image_url(p_en)
                    st.image(img_url, caption="Ảnh AI tạo bởi Rin.Ai (Pollinations)")
                except Exception as e:
                    st.error(f"Lỗi tạo ảnh: {e}")

    # VIDEO PROMPT
    elif mode == "🎬 Tạo Prompt Video":
        idea = st.text_area("Ý tưởng video (tiếng Việt):")
        if st.button("🎥 Viết Prompt") and idea:
            with st.spinner("Đang viết Video Prompt tiếng Anh..."):
                try:
                    model = get_model(current_model_name)
                    prompt_en = model.generate_content(
                        f"Create a professional English video prompt for Veo/Sora/Runway based on this idea (in Vietnamese): {idea}"
                        "\n\nOutput only the final English prompt, no explanation."
                    ).text
                    st.code(prompt_en, language="markdown")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    # VOICE
    elif mode == "🎙️ Voice AI":
        c1, c2 = st.columns(2)
        is_slow = c1.checkbox("🐢 Đọc chậm", value=False)
        tone = c2.selectbox("Giọng đọc:", ["Truyền cảm", "Vui vẻ", "Nghiêm túc"])
        txt = st.text_area("Nhập nội dung muốn đọc:")

        if st.button("🎙️ Đọc") and txt:
            st.info(f"Giọng: {tone}")
            play_text_to_speech(txt, is_slow)

# --- MODULE: CÁC CHUYÊN GIA THEO NGÀNH ---
else:
    st.header(menu)
    expert_instruction = get_expert_prompt(menu)

    # Bổ sung cấu hình riêng cho Giáo dục
    system_append = ""
    if menu == "🎓 Giáo Dục & Đào Tạo":
        c1, c2 = st.columns(2)
        sach = c1.selectbox(
            "Bộ sách:",
            ["Cánh Diều", "Kết Nối Tri Thức", "Chân Trời Sáng Tạo"],
        )
        role = c2.radio("Vai trò:", ["Học sinh", "Giáo viên", "Phụ huynh"], horizontal=True)
        system_append = f"\n(Bộ sách: {sach}, Đối tượng: {role})."

    # Khởi tạo lịch sử chat
    if "history" not in st.session_state:
        st.session_state.history = {}

    if menu not in st.session_state.history:
        st.session_state.history[menu] = [
            {
                "role": "assistant",
                "content": f"Xin chào! Tôi là chuyên gia trong lĩnh vực **{menu}**. Bạn cần hỗ trợ điều gì?",
            }
        ]

    # Hiển thị lịch sử
    for msg in st.session_state.history[menu]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            clean_show = re.sub(
                r"###PROMPT_[23]D###.*?###END_PROMPT###",
                "",
                msg["content"],
                flags=re.DOTALL,
            )
            if clean_show.strip():
                with st.chat_message("assistant"):
                    st.markdown(clean_show)

    # Ô nhập chat
    user_prompt = st.chat_input("Gửi yêu cầu...")

    if user_prompt:
        # Hiển thị user chat
        with st.chat_message("user"):
            st.markdown(user_prompt)
            if file_content is not None and uploaded_file is not None:
                st.caption(f"📎 Đính kèm: {uploaded_file.name}")

        st.session_state.history[menu].append(
            {"role": "user", "content": user_prompt}
        )

        # Gọi Gemini
        with st.chat_message("assistant"):
            with st.spinner(f"Chuyên gia ({current_model_name}) đang phân tích..."):
                try:
                    final_prompt = user_prompt + system_append
                    message_payload = []

                    if file_content is not None:
                        # Nếu là ảnh -> gửi multimodal
                        if isinstance(file_content, Image.Image):
                            message_payload = [final_prompt, file_content]
                        else:
                            final_prompt += (
                                "\n\n=== FILE DATA ===\n"
                                f"{file_content}\n"
                                "================="
                            )
                            message_payload = [final_prompt]
                    else:
                        message_payload = [final_prompt]

                    model = get_model(current_model_name)
                    chat = model.start_chat(
                        system_instruction=expert_instruction,
                        history=[],
                    )
                    response = chat.send_message(message_payload)
                    full_txt = response.text

                    # Lấy prompt 2D/3D nếu có
                    p2d = re.search(
                        r"###PROMPT_2D###(.*?)###END_PROMPT###",
                        full_txt,
                        re.DOTALL,
                    )
                    p3d = re.search(
                        r"###PROMPT_3D###(.*?)###END_PROMPT###",
                        full_txt,
                        re.DOTALL,
                    )
                    txt_show = re.sub(
                        r"###PROMPT_[23]D###.*?###END_PROMPT###",
                        "",
                        full_txt,
                        flags=re.DOTALL,
                    )

                    st.markdown(txt_show.strip())

                    # Nếu có prompt vẽ, hiển thị thêm ảnh
                    if p2d or p3d:
                        st.divider()
                        col_a, col_b = st.columns(2)
                        if p2d:
                            with col_a:
                                st.image(
                                    generate_image_url(
                                        "Blueprint floor plan. " + p2d.group(1)
                                    ),
                                    caption="Bản vẽ 2D (demo AI)",
                                )
                        if p3d:
                            with col_b:
                                st.image(
                                    generate_image_url(
                                        "Architecture render 8k. " + p3d.group(1)
                                    ),
                                    caption="Phối cảnh 3D (demo AI)",
                                )

                    st.session_state.history[menu].append(
                        {"role": "assistant", "content": full_txt}
                    )

                    # Giới hạn lịch sử cho nhẹ RAM
                    if len(st.session_state.history[menu]) > 40:
                        st.session_state.history[menu] = st.session_state.history[
                            menu
                        ][:40]

                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    st.warning(
                        "⚠️ Nếu gặp lỗi, hãy thử đổi sang model 'gemini-1.5-flash' ở thanh bên trái."
                    )
