import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import re
from PIL import Image
import PyPDF2
import pandas as pd
from datetime import datetime

# --- IMPORT FILE PROMPTS ---
try:
    from prompts import get_expert_prompt
except ImportError:
    st.error("⚠️ Lỗi: Không tìm thấy file 'prompts.py'. Hãy tạo file này cùng thư mục.")
    st.stop()

# =============================================================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ
# =============================================================================

st.set_page_config(page_title="Rin.Ai - Siêu Trợ Lý AI", page_icon="💎", layout="wide")

def process_uploaded_file(uploaded_file):
    if uploaded_file is None: return None
    try:
        if uploaded_file.type.startswith('image'):
            return Image.open(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages: text += page.extract_text()
            return text
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type or "csv" in uploaded_file.type:
            if "csv" in uploaded_file.type: df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            return df.to_string()
        elif "word" in uploaded_file.type or "docx" in uploaded_file.type:
             return "File Word đã nhận (Hệ thống hiện tại hỗ trợ đọc nội dung text cơ bản)."
        else: return uploaded_file.getvalue().decode("utf-8")
    except Exception as e: return f"Lỗi đọc file: {e}"

def clean_text_for_tts(text):
    if not text: return ""
    clean = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', text, flags=re.DOTALL)
    clean = re.sub(r'\([^)]*\)', '', clean)
    clean = re.sub(r'\[[^]]*\]', '', clean)
    clean = clean.replace('*', '').replace('#', '').replace('`', '').replace('-', '')
    return clean.strip()

def play_text_to_speech(text_content, speed_slow=False):
    try:
        text_to_read = clean_text_for_tts(text_content)
        if len(text_to_read) < 5: return 
        
        tts = gTTS(text=text_to_read, lang='vi', slow=speed_slow)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes, format='audio/mp3')
        
        status = "🐢 Đang đọc chậm..." if speed_slow else "🐇 Đang đọc tốc độ thường..."
        st.caption(f"🔊 {status}")
    except: pass

def generate_image_url(prompt):
    clean_prompt = prompt.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?nologo=true&model=turbo"

@st.cache_resource
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    try:
        # Ưu tiên model mới nhất hỗ trợ Search
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        for p in priority:
            for m in models:
                if p in m: return m
        return "gemini-1.5-flash"
    except: return None

# =============================================================================
# 2. SIDEBAR (THANH CÔNG CỤ TRÁI)
# =============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # --- NHẬP KEY (ĐÃ THÊM HƯỚNG DẪN) ---
    st.subheader("🔑 Tài khoản")
    key_option = st.radio("Chế độ:", ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn"], label_visibility="collapsed")
    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server")
        except: st.error("❌ Chưa cấu hình Key chung")
    else: 
        st.info("Nhập Google API Key:")
        # --- LINK HƯỚNG DẪN LẤY KEY ---
        st.markdown("[👉 Bấm vào đây để lấy Key miễn phí](https://aistudio.google.com/app/apikey)")
        final_key = st.text_input("Dán Key vào đây:", type="password")
        if final_key: st.success("✅ Đã nhận Key")
    
    st.divider()

    # --- MENU CÔNG CỤ (ĐÃ BỔ SUNG FULL HỆ SINH THÁI) ---
    st.subheader("🔥 Công Cụ Mở Rộng")
    st.link_button("🤖 Mở App ChatGPT", "https://chatgpt.com/") 
    
    with st.expander("🌐 Google AI Tools (Full)"):
        st.link_button("💎 Gemini Chat", "https://gemini.google.com/")
        st.link_button("📚 NotebookLM (Học tập)", "https://notebooklm.google.com/")
        st.link_button("🛠️ AI Studio (Cho Dev)", "https://aistudio.google.com/")
        st.link_button("🎨 ImageFX (Tạo ảnh)", "https://aitestkitchen.withgoogle.com/tools/image-fx")
        st.link_button("🎥 VideoFX (Tạo Video)", "https://aitestkitchen.withgoogle.com/tools/video-fx")
        st.link_button("🎵 MusicFX (Tạo Nhạc)", "https://aitestkitchen.withgoogle.com/tools/music-fx")
    
    with st.expander("📝 Văn phòng (Workspace)"):
        st.link_button("Google Docs AI", "https://docs.google.com/")
        st.link_button("Google Sheets AI", "https://sheets.google.com/")
    
    st.divider()
    
    # --- UPLOAD FILE ---
    st.subheader("📎 Đính Kèm Tài Liệu")
    uploaded_file = st.file_uploader("Chọn file:", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx', 'docx'], label_visibility="collapsed")
    
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        st.success(f"✅ Đã nhận: {uploaded_file.name}")
    
    st.divider()

    # --- MENU CHỨC NĂNG CHÍNH ---
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
            "🏠 Bất Động Sản & Xe Sang"
        ]
    )

# =============================================================================
# 3. LOGIC CHÍNH (MAIN APP) - ĐÃ ĐƯỢC TỐI ƯU
# =============================================================================

if not final_key and menu != "🏠 Trang Chủ & Giới Thiệu":
    st.warning("👋 Vui lòng nhập Key bên tay trái để bắt đầu.")
    st.stop()

if final_key:
    genai.configure(api_key=final_key)
    best_model = get_best_model(final_key)

# --- TRANG CHỦ ---
if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 👋 Chào mừng đến với Rin.Ai PRO
        **Sản phẩm tâm huyết được phát triển bởi: Mr. Học**
        
        Rin.Ai là "Super App" tích hợp sức mạnh Google AI phục vụ công việc thực tế.
        """)
        st.link_button("👉 Chat Zalo Ngay Với Mr. Học", "https://zalo.me/0901108788")
    with col2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg")

# --- MODULE 1: TIN TỨC & SÁCH (ĐÃ SỬA LỖI SEARCH) ---
elif menu == "📰 Đọc Báo & Tóm Tắt Sách":
    st.header("📰 Chuyên Gia Tri Thức & Tin Tức")
    today_str = datetime.now().strftime("%d/%m/%Y")
    st.caption(f"📅 Hôm nay: {today_str}")

    task = st.radio("Chế độ:", ["🔎 Tin Tức Thời Sự", "📚 Tóm tắt Sách/Tài liệu"], horizontal=True)
    
    if task == "🔎 Tin Tức Thời Sự":
        topic = st.text_input("Nhập chủ đề (VD: Tình hình bão lũ, Giá vàng hôm nay...):")
        if st.button("🔎 Tìm kiếm"):
            if topic:
                with st.spinner(f"Đang quét tin tức mới nhất về {topic}..."):
                    try:
                        # --- [SỬA LỖI QUAN TRỌNG] Cập nhật cú pháp Tools mới nhất ---
                        # Thư viện mới dùng 'google_search_retrieval' thay vì 'google_search'
                        tool_config = {'google_search_retrieval': {}}
                        
                        search_model = genai.GenerativeModel(best_model, tools=[tool_config])
                        
                        search_prompt = f"""
                        Hãy tìm kiếm và báo cáo chi tiết về: "{topic}".
                        Thời gian: Cập nhật mới nhất ngày hôm nay ({today_str}).
                        Yêu cầu:
                        1. Tóm tắt các sự kiện chính.
                        2. Cung cấp số liệu cụ thể (nếu có).
                        3. Đính kèm Link nguồn báo uy tín.
                        """
                        
                        res = search_model.generate_content(search_prompt).text
                        
                        st.success("✅ Kết quả tìm kiếm:")
                        st.markdown(res)
                        st.divider()
                        play_text_to_speech(res)
                        
                    except Exception as e: 
                        st.error(f"Lỗi kết nối Google Search: {e}")
                        st.info("💡 Mẹo: Hãy thử đổi sang model 'gemini-1.5-pro' hoặc kiểm tra lại API Key.")
            else:
                st.warning("Vui lòng nhập chủ đề cần tìm!")

    else:
        # Phần Tóm tắt sách giữ nguyên vì đã ổn
        txt_input = st.text_area("Dán văn bản (hoặc upload file bên trái):")
        user_content = file_content if file_content else txt_input
        if st.button("📚 Tóm tắt") and user_content:
             with st.spinner("Đang đọc và tóm tắt..."):
                model = genai.GenerativeModel(best_model)
                req = [f"Tóm tắt nội dung sau:", user_content] if isinstance(user_content, Image.Image) else [f"Tóm tắt nội dung sau: {user_content}"]
                res = model.generate_content(req).text
                st.markdown(res)
                play_text_to_speech(res)

# --- MODULE 2: MEDIA ---
elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
    st.header("🎨 Studio Đa Phương Tiện")
    mode = st.radio("Công cụ:", ["🖼️ Tạo Ảnh", "🎬 Tạo Prompt Video", "🎙️ Voice AI"], horizontal=True)
    
    if mode == "🖼️ Tạo Ảnh":
        desc = st.text_area("Mô tả ảnh:")
        if st.button("🎨 Vẽ") and desc:
            with st.spinner("Đang vẽ..."):
                model = genai.GenerativeModel(best_model)
                p_en = model.generate_content(f"Translate prompt to English: {desc}").text
                st.image(generate_image_url(p_en))
    
    elif mode == "🎬 Tạo Prompt Video":
        idea = st.text_area("Ý tưởng video:")
        if st.button("🎥 Tạo Prompt") and idea:
            model = genai.GenerativeModel(best_model)
            st.code(model.generate_content(f"Create English Video Prompt for Sora/Runway: {idea}").text)

    elif mode == "🎙️ Voice AI":
        c1, c2 = st.columns(2)
        is_slow = c1.checkbox("🐢 Đọc chậm")
        tone = c2.selectbox("Cảm xúc:", ["Truyền cảm", "Vui vẻ", "Nghiêm túc"])
        txt = st.text_area("Nội dung:")
        if st.button("🎙️ Đọc") and txt:
            play_text_to_speech(txt, is_slow)

# --- MODULE 3: CHUYÊN GIA ---
else:
    st.header(menu)
    expert_instruction = get_expert_prompt(menu)
    
    system_append = ""
    if menu == "🎓 Giáo Dục & Đào Tạo":
        c1, c2 = st.columns(2)
        sach = c1.selectbox("Bộ sách:", ["Cánh Diều", "Kết Nối Tri Thức", "Chân Trời Sáng Tạo"])
        role = c2.radio("Vai trò:", ["Học sinh", "Giáo viên"], horizontal=True)
        system_append = f"\n(Bộ sách: {sach}, Đối tượng: {role})."

    if "history" not in st.session_state: st.session_state.history = {}
    if menu not in st.session_state.history:
        st.session_state.history[menu] = [{"role": "assistant", "content": f"Xin chào! Tôi là chuyên gia {menu}. Tôi có thể giúp gì cho bạn?"}]

    for msg in st.session_state.history[menu]:
        if msg["role"] == "user":
            with st.chat_message("user"): st.markdown(msg["content"])
        else:
            clean_show = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', msg["content"], flags=re.DOTALL)
            if clean_show.strip():
                with st.chat_message("assistant"): st.markdown(clean_show)

    if prompt := st.chat_input("Nhập yêu cầu..."):
        with st.chat_message("user"): 
            st.markdown(prompt)
            if file_content: st.caption(f"📎 Đính kèm: {uploaded_file.name}")
        st.session_state.history[menu].append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Đang phân tích..."):
                try:
                    msg_content = [prompt + system_append]
                    if file_content:
                        if isinstance(file_content, Image.Image):
                            msg_content.append(file_content)
                        else:
                            msg_content.append(f"\nFILE DATA:\n{file_content}")
                    
                    model = genai.GenerativeModel(best_model, system_instruction=expert_instruction)
                    full_txt = model.generate_content(msg_content).text
                    
                    p2d = re.search(r'###PROMPT_2D###(.*?)###END_PROMPT###', full_txt, re.DOTALL)
                    p3d = re.search(r'###PROMPT_3D###(.*?)###END_PROMPT###', full_txt, re.DOTALL)
                    txt_show = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', full_txt, flags=re.DOTALL)
                    
                    st.markdown(txt_show.strip())
                    
                    if p2d or p3d:
                        st.divider()
                        ca, cb = st.columns(2)
                        if p2d: 
                            with ca: st.image(generate_image_url("Blueprint plan. " + p2d.group(1)), caption="Bản vẽ 2D")
                        if p3d: 
                            with cb: st.image(generate_image_url("Architecture render 8k. " + p3d.group(1)), caption="Phối cảnh 3D")
                    
                    st.session_state.history[menu].append({"role": "assistant", "content": full_txt})
                except Exception as e: st.error(f"Lỗi: {e}")
