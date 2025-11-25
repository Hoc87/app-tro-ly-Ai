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

# -------------------------------------------------------------
# CẤU HÌNH CHUNG
# -------------------------------------------------------------

st.set_page_config(
    page_title="Rin.Ai - Siêu Trợ Lý AI",
    page_icon="💎",
    layout="wide",
)
# --- ẨN THANH MENU VÀ ICON GITHUB (BẢO MẬT) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
current_model_name = "gemini-1.5-flash"

# -------------------------------------------------------------
# HÀM HỖ TRỢ
# -------------------------------------------------------------

def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        file_type = uploaded_file.type or ""
        file_name = uploaded_file.name.lower()

        if file_type.startswith("image"):
            return Image.open(uploaded_file)

        if file_type == "application/pdf" or file_name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text

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

        if file_name.endswith(".docx"):
            d = docx.Document(uploaded_file)
            text = "\n".join(p.text for p in d.paragraphs)
            return text

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
        # Lọc model an toàn: loại tts / speech / embed
        candidates = [
            n
            for n in names
            if "gemini" in n.lower()
            and (
                "1.5" in n
                or "2.0" in n
                or "2.5" in n
                or "pro" in n.lower()
                or "flash" in n.lower()
            )
            and "tts" not in n.lower()
            and "speech" not in n.lower()
            and "embed" not in n.lower()
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


# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/12222/12222588.png",
        width=80,
    )
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()

    # ---- TÀI KHOẢN & CẤU HÌNH ----
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

    # ---- CHỌN MODEL (TỰ ĐỘNG + NÂNG CAO) ----
    if final_key:
        available_models = get_available_models(final_key)
        recommended_model = available_models[0]

        advanced_model_choice = st.checkbox(
            "⚙️ Bật chế độ chọn model nâng cao",
            value=False,
        )

        if advanced_model_choice:
            selected_model_display = st.selectbox(
                "🧠 Chọn bộ não AI:",
                available_models,
                index=0,
            )
            current_model_name = selected_model_display
            st.caption(f"Đang dùng model: `{current_model_name}` (tùy chỉnh)")
        else:
            current_model_name = recommended_model
            st.caption(f"Đang dùng model khuyến nghị: `{current_model_name}`")

    st.divider()

    # ---- CÔNG CỤ MỞ RỘNG ----
    st.subheader("🔥 Công Cụ Mở Rộng")
    st.link_button(
        "🤖 Danh sách Trợ Lý AI ChatGPT",
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

    # ---- UPLOAD FILE TOÀN PHIÊN ----
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

    # ---- MENU CHUYÊN GIA ----
    st.subheader("📂 Chọn Chuyên Gia (Hệ sinh thái Ai của Google")
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

# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------

if not final_key and menu != "🏠 Trang Chủ & Giới Thiệu":
    st.warning("👋 Vui lòng nhập Google API Key bên tay trái để bắt đầu.")
    st.stop()

if final_key:
    genai.configure(api_key=final_key)

# TRANG CHỦ
if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
💎 **Rin.Ai – Hệ Sinh Thái AI Thực Chiến Cho Người Việt**

👋 Chào mừng bạn đến với **Rin.Ai PRO**  
Được nghiên cứu, xây dựng và liên tục nâng cấp bởi **Mr. Học** – người sáng lập hệ sinh thái **Rin.Ai**.

Rin.Ai là một **"Super App" AI** tích hợp song song hai nền tảng:

- 🤖 **Google AI Suite**: Gemini, AI Studio, NotebookLM, Imagen, Veo…
- 🧠 **ChatGPT & hệ sinh thái OpenAI**

🎯 Mục tiêu: mang sức mạnh của các mô hình AI hàng đầu thế giới vào **công việc, học tập và tự động hoá** hàng ngày của người Việt.

---

### 🚀 1. Cho công việc & kinh doanh

- 🖥️ Hỗ trợ **văn phòng, báo cáo, Excel/Sheets, biểu mẫu, hợp đồng, slide thuyết trình**.
- 📈 Đồng hành cùng **kinh doanh & marketing**: chân dung khách hàng, ý tưởng nội dung, kịch bản video, kịch bản bán hàng & chăm sóc khách hàng.
- 📋 Đề xuất **checklist, quy trình, mẫu template** có thể áp dụng ngay vào thực tế.

### 🎓 2. Cho học tập & phát triển bản thân

- 📚 Giải thích kiến thức **từ phổ thông đến kỹ năng nghề** theo cách dễ hiểu, nhiều ví dụ.
- 📄 Tóm tắt nhanh **sách, tài liệu, PDF, slide, ghi chú** thành các ý chính.
- 📝 Hỗ trợ **luyện thi, ôn tập, làm bài tập**, gợi ý cách tự học thông minh hơn.

### ⚙️ 3. Tự động hoá trên nền tảng Google

- 🔧 Gợi ý **Apps Script, công thức, macro** cho Google Docs, Sheets, Slides, Gmail…
- 🔁 Biến các thao tác lặp lại thành **quy trình tự động**, giảm lỗi thủ công.
- 📊 Gợi ý cách **chuẩn hoá dữ liệu, dựng báo cáo, dashboard** phục vụ quyết định nhanh.

---

### 🤝 Hợp tác xây dựng Trợ lý AI riêng

Nếu bạn là **cá nhân, doanh nghiệp, trung tâm đào tạo hoặc tổ chức** muốn xây dựng:

- 🤖 **Trợ lý AI mang thương hiệu riêng**
- 📂 Tích hợp **quy trình, dữ liệu, tài liệu nội bộ** của chính bạn
- 🌐 Hoạt động trên nhiều kênh (web, mobile, chatbot, nội bộ doanh nghiệp)

➡️ Hãy liên hệ trực tiếp để được tư vấn & thiết kế giải pháp:

- 👤 **Mr. Học – Founder Rin.Ai**
- 📱 **Điện thoại/Zalo:** **0901108788**
- 📧 **Email:** nguyenhoc1010@gmail.com

✨ Rin.Ai mong muốn đồng hành cùng bạn trong hành trình **ứng dụng AI thực chiến**, làm việc **nhanh hơn – thông minh hơn – hiệu quả hơn** mỗi ngày.
🎁 Bạn thấy Rin.Ai hữu ích? **Đừng giữ cho riêng mình!** 👉 Hãy chia sẻ đường link * https://rin-ai.streamlit.app/ * App này đến **Bạn bè & Đồng nghiệp** để cùng nhau áp dụng AI, giúp công việc và học tập trở nên nhẹ nhàng, hiệu quả hơn.
     *"Thành công là khi chúng ta cùng nhau tiến bộ!"* 🚀

👉 **Tiếp theo:** hãy dùng **menu bên trái** để chọn **Chuyên gia AI** phù hợp với nhu cầu của bạn và bắt đầu trò chuyện ngay bây giờ.
        """)
        st.link_button(
            "👉 Chat Zalo với Mr. Học",
            "https://zalo.me/0901108788",
        )

    with col2:
        st.image(
            "https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg",
            use_column_width=True,
        )


# ĐỌC BÁO & TÓM TẮT SÁCH
elif menu == "📰 Đọc Báo & Tóm Tắt Sách":
    st.header("📰 Chuyên Gia Tri Thức & Tin Tức")
    today_str = datetime.now().strftime("%d/%m/%Y")

    # Lấy system_instruction từ prompts.py
    expert_instruction = get_expert_prompt(menu)

    task = st.radio(
        "Chế độ:",
        ["🔎 Tin Tức Thời Sự", "📚 Tóm tắt Sách/Tài liệu"],
        horizontal=True,
        key="news_mode_radio",
    )

    # ==============================
    # 1) CHẾ ĐỘ: TIN TỨC THỜI SỰ
    # ==============================
    if task == "🔎 Tin Tức Thời Sự":
        topic = st.text_input(
            f"Nhập chủ đề tin tức ({today_str}):",
            key="news_topic_input",
        )

        if st.button("🔎 Phân tích tin tức", key="news_analyze_btn"):
            if not topic:
                st.warning("❗ Vui lòng nhập chủ đề trước khi phân tích.")
            else:
                with st.spinner(
                    f"Đang dùng {current_model_name} để phân tích chủ đề “{topic}”..."
                ):
                    try:
                        # KHÔNG dùng tools google_search để tránh lỗi SDK cũ
                        model = genai.GenerativeModel(
                            current_model_name,
                            system_instruction=expert_instruction,
                        )

                        prompt_text = (
                         "Bạn đang ở vai trò: CHUYÊN GIA TRI THỨC & TIN TỨC trong hệ sinh thái Rin.Ai.\n"
                         "Chế độ hiện tại: TIN TỨC THỜI SỰ.\n"
                         f"Chủ đề người dùng nhập: {topic}\n"
                         f"Ngày tham chiếu hiện tại (HÔM NAY theo hệ thống): {today_str}.\n"
                         "QUAN TRỌNG: Không được nói rằng ngày tham chiếu này là 'trong tương lai' hay 'ngoài phạm vi dữ liệu của bạn'. "
                         "Nếu thiếu dữ liệu mới, chỉ cần nói chung là dữ liệu của bạn cập nhật tới khoảng năm 2024, "
                         "nhưng KHÔNG được phủ nhận ngày tham chiếu.\n"
                         "\n"
                         "LẦN TRẢ LỜI NÀY chỉ có 1 nhiệm vụ: đặt các câu hỏi làm rõ theo đúng workflow đã được cấu hình trong system_instruction, "
                         "không tóm tắt tin tức và không phân tích chi tiết.\n"
                       "Hãy:\n"
                       "- Hỏi người dùng 5 câu khởi động (chủ đề, thời điểm Daily Brief, sách, chế độ đọc, gợi ý sách tương tự).\n"
                       "- Nếu chủ đề liên quan tới tài chính / kinh doanh / chứng khoán, hỏi thêm về QUỐC GIA và KHUNG THỜI GIAN (Hôm nay / 24h / 7 ngày).\n"
                      "Chỉ trả lời bằng danh sách câu hỏi cần người dùng bổ sung, không phân tích tin tức trong lượt này."
                    )


                        response = model.generate_content(prompt_text)
                        res_text = response.text

                        st.success("✅ Kết quả tổng hợp & phân tích:")
                        st.markdown(res_text)
                        play_text_to_speech(res_text)

                    except Exception as e:
                        st.error(f"❌ Lỗi khi phân tích tin tức: {e}")
                        st.info(
                            "💡 Nếu lỗi tiếp diễn, hãy thử chọn model `gemini-1.5-flash` ở thanh bên trái."
                        )

    # ==============================
    # 2) CHẾ ĐỘ: TÓM TẮT SÁCH / TÀI LIỆU
    # ==============================
    else:
        st.subheader("📚 Tóm tắt Sách / Tài liệu")
        txt_input = st.text_area(
            "Dán nội dung, hoặc chỉ cần upload file ở thanh bên trái:",
            key="news_text_area",
        )
        content = file_content if file_content is not None else txt_input

        if st.button("📚 Tóm tắt", key="news_summary_btn") and content:
            with st.spinner("Đang tóm tắt nội dung..."):
                try:
                    model = genai.GenerativeModel(
                        current_model_name,
                        system_instruction=expert_instruction,
                    )

                    if isinstance(content, Image.Image):
                        request = [
                            "Chế độ: TÓM TẮT SÁCH/TÀI LIỆU.\n"
                            "Hãy tóm tắt nội dung chính của hình ảnh/tài liệu sau, trình bày dạng gạch đầu dòng dễ hiểu cho người Việt:",
                            content,
                        ]
                    else:
                        request = [
                            "Chế độ: TÓM TẮT SÁCH/TÀI LIỆU.\n"
                            "Hãy tóm tắt nội dung sau theo đúng quy trình bạn đã được cấu hình "
                            "(ý chính, phân tích ngắn, tổng kết 3–5 ý quan trọng):\n\n"
                            f"{content}"
                        ]

                    res_text = model.generate_content(request).text
                    st.markdown(res_text)
                    play_text_to_speech(res_text)

                except Exception as e:
                    st.error(f"❌ Lỗi khi tóm tắt tài liệu: {e}")
# -------------------------------------------------------------
# CÁC CHUYÊN GIA THEO NGÀNH (CHUNG CHO TẤT CẢ MENU CÒN LẠI)
# Bao gồm: ✨ Trợ Lý Đa Lĩnh Vực, 🎨 Media, Office, Kiến trúc, Luật, Kinh doanh...
# -------------------------------------------------------------
else:
    st.header(menu)

    # Lấy cấu hình chuyên gia từ prompts.py
    expert_instruction = get_expert_prompt(menu)

    # Tuỳ chỉnh thêm cho Giáo dục (chọn bộ sách / vai trò)
    system_append = ""
    if menu == "🎓 Giáo Dục & Đào Tạo":
        c1, c2 = st.columns(2)
        sach = c1.selectbox(
            "Bộ sách:",
            ["Cánh Diều", "Kết Nối Tri Thức", "Chân Trời Sáng Tạo"],
        )
        role = c2.radio(
            "Vai trò:",
            ["Học sinh", "Giáo viên", "Phụ huynh"],
            horizontal=True,
        )
        system_append = f"\n(Bộ sách: {sach}, Đối tượng: {role})."

    # Upload file riêng cho từng câu hỏi (nằm trong khu chat, dễ nhìn)
    st.markdown("**📎 Đính kèm tài liệu cho câu hỏi này (tùy chọn):**")
    chat_uploaded_file = st.file_uploader(
        "Chọn file cho câu hỏi (ảnh/PDF/Word/Excel...):",
        type=["png", "jpg", "jpeg", "pdf", "txt", "csv", "xlsx", "docx"],
        label_visibility="collapsed",
        key=f"chat_uploader_{menu}",
    )
    chat_file_content = None
    if chat_uploaded_file is not None:
        chat_file_content = process_uploaded_file(chat_uploaded_file)

    # Lưu lịch sử chat theo từng menu chuyên gia
    if "history" not in st.session_state:
        st.session_state.history = {}

    if menu not in st.session_state.history:
        st.session_state.history[menu] = [
            {
                "role": "assistant",
                "content": (
                    f"Xin chào! Tôi là **chuyên gia {menu}** trong hệ sinh thái Rin.Ai. "
                    "Bạn hãy mô tả thật rõ yêu cầu, bối cảnh và mục tiêu, tôi sẽ hỗ trợ theo đúng vai trò & quy trình đã được cấu hình."
                ),
            }
        ]

    # Hiển thị lại lịch sử hội thoại
    for msg in st.session_state.history[menu]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            # Ẩn phần PROMPT_2D / 3D khi hiển thị, chỉ dùng nội bộ
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
    user_prompt = st.chat_input("Gửi yêu cầu cho chuyên gia...")

    if user_prompt:
        # Xác định file sẽ dùng cho câu hỏi này
        used_file_content = (
            chat_file_content if chat_file_content is not None else file_content
        )
        used_file_name = None
        if chat_uploaded_file is not None:
            used_file_name = chat_uploaded_file.name
        elif uploaded_file is not None and file_content is not None:
            used_file_name = uploaded_file.name

        # Hiển thị tin nhắn người dùng
        with st.chat_message("user"):
            st.markdown(user_prompt)
            if used_file_name:
                st.caption(f"📎 Đính kèm: {used_file_name}")

        st.session_state.history[menu].append(
            {"role": "user", "content": user_prompt}
        )

        # Gọi model theo đúng chuyên gia
        with st.chat_message("assistant"):
            with st.spinner(f"Chuyên gia ({current_model_name}) đang phân tích..."):
                try:
                    final_prompt = user_prompt + system_append

                    # Chuẩn bị payload cho Gemini: nếu có file thì gắn thêm
                    if used_file_content is not None:
                        if isinstance(used_file_content, Image.Image):
                            message_payload = [final_prompt, used_file_content]
                        else:
                            final_prompt += (
                                "\n\n=== FILE DATA (tóm tắt nội dung người dùng gửi) ===\n"
                                f"{used_file_content}\n"
                                "===================================================="
                            )
                            message_payload = [final_prompt]
                    else:
                        message_payload = [final_prompt]

                    # Tạo model & start_chat để có memory trong từng lần hỏi
                    model = get_model(current_model_name)
                    chat = model.start_chat(
                        system_instruction=expert_instruction,
                        history=[],
                    )
                    response = chat.send_message(message_payload)
                    full_txt = response.text or ""

                    # Tách PROMPT_2D / 3D (nếu là chuyên gia Kiến trúc)
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

                    # Hiển thị nội dung trả lời chính
                    st.markdown(txt_show.strip())

                    # Nếu có prompt vẽ 2D/3D → demo thêm ảnh minh hoạ (tuỳ chọn)
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

                    # Lưu vào lịch sử
                    st.session_state.history[menu].append(
                        {"role": "assistant", "content": full_txt}
                    )
                    # Giới hạn lịch sử để tránh quá dài
                    if len(st.session_state.history[menu]) > 40:
                        st.session_state.history[menu] = st.session_state.history[
                            menu
                        ][-40:]

                except Exception as e:
                    st.error(f"❌ Lỗi khi chuyên gia trả lời: {e}")
                    st.warning(
                        "⚠️ Nếu gặp lỗi, hãy thử đổi sang model 'gemini-1.5-flash' ở thanh bên trái."
                    )


