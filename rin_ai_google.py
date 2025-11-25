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
                            "Chế độ: TIN TỨC THỜI SỰ.\n"
                            f"Chủ đề: {topic}\n"
                            f"Ngày tham chiếu: {today_str}.\n"
                            "Hãy áp dụng đúng vai trò, nhiệm vụ, quy trình và nguyên tắc mà bạn đã được cấu hình "
                            "trong system_instruction: tổng hợp bức tranh chính, phân tích tác động và đưa phần nguồn tham khảo (nếu có). "
                            "Nếu không truy cập được tin mới hoặc không chắc chắn, hãy nói rõ giới hạn và KHÔNG bịa link."
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


