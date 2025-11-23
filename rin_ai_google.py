import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import re
import requests 
from PIL import Image
import PyPDF2
import pandas as pd

# IMPORT FILE PROMPTS
from prompts import get_expert_prompt

# =============================================================================
# CẤU HÌNH & HÀM HỖ TRỢ
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
        else: return uploaded_file.getvalue().decode("utf-8")
    except Exception as e: return f"Lỗi đọc file: {e}"

def clean_text_for_tts(text):
    if not text: return ""
    clean = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', text, flags=re.DOTALL)
    clean = re.sub(r'\([^)]*\)', '', clean)
    clean = re.sub(r'\[[^]]*\]', '', clean)
    clean = clean.replace('*', '').replace('#', '').replace('`', '')
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
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        for p in priority:
            for m in models:
                if p in m: return m
        return "gemini-pro"
    except: return None

# =============================================================================
# GIAO DIỆN SIDEBAR (THANH BÊN TRÁI)
# =============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # 1. KEY
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
        final_key = st.text_input("Dán Key vào đây:", type="password")
        if final_key: st.success("✅ Đã nhận Key")
    
    st.divider()

    # 2. LIÊN KẾT MẠNH MẼ (ĐÃ CẬP NHẬT THEO ẢNH BẠN GỬI)
    st.subheader("🔥 Bộ Công Cụ Google AI")
    
    # Sử dụng Expander để nhóm lại cho gọn, hoặc để lộ thiên tùy bạn.
    # Ở đây tôi để lộ thiên các tool quan trọng nhất để dễ bấm.
    
    st.link_button("💎 Gemini (Chat & Code)", "https://gemini.google.com/")
    st.link_button("📚 NotebookLM (Học tập)", "https://notebooklm.google.com/")
    st.link_button("🛠️ AI Studio (Dev)", "https://aistudio.google.com/")
    
    with st.expander("🎨 Sáng tạo (Ảnh/Video/Nhạc)"):
        st.link_button("🖼️ ImageFX (Imagen 3)", "https://aitestkitchen.withgoogle.com/tools/image-fx")
        st.link_button("🎥 VideoFX (Veo)", "https://aitestkitchen.withgoogle.com/tools/video-fx")
        st.link_button("🎵 MusicFX (Lyria)", "https://aitestkitchen.withgoogle.com/tools/music-fx")
    
    with st.expander("📝 Văn phòng (Workspace AI)"):
        st.link_button("Google Docs AI", "https://docs.google.com/")
        st.link_button("Google Sheets AI", "https://sheets.google.com/")
        st.link_button("Google Slides AI", "https://slides.google.com/")

    st.divider()
    st.link_button("👉 Mở App ChatGPT", "https://chatgpt.com/") 
    st.divider()
    
    # 3. UPLOAD FILE
    st.subheader("📎 Đính Kèm Tài Liệu")
    st.caption("👇 Tải File Word, Excel, PDF, Ảnh tại đây:")
    uploaded_file = st.file_uploader("Chọn file...", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx', 'docx'], label_visibility="collapsed")
    
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        st.success(f"✅ Đã đọc: {uploaded_file.name}")
    
    st.divider()

    # 4. MENU CHỨC NĂNG (ĐÃ ĐỔI SANG SELECTBOX - SỔ XUỐNG)
    st.subheader("📂 Chọn Chuyên Gia")
    
    # --- THAY ĐỔI Ở ĐÂY: st.radio -> st.selectbox ---
    menu = st.selectbox(
        "Hãy chọn lĩnh vực bạn cần hỗ trợ:",
        [
            "🏠 Trang Chủ & Giới Thiệu", 
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "🖥️ Chuyên Gia Tin Học Văn Phòng (Office)",
            "🏛️ Trợ Lý Cán bộ Ủy ban (Xã/Phường/TP)",
            "🏛️ Dịch Vụ Hành Chính Công",
            "🏗️ Kiến Trúc - Nội Thất - Xây Dựng",
            "📰 Đọc Báo & Tóm Tắt Sách", 
            "🎨 Thiết Kế & Media (Ảnh/Video/Voice)", 
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
# LOGIC CHÍNH
# =============================================================================

if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("""
    ### 🚀 Chào mừng đến với Rin.Ai PRO
    
    Đây là "Super App" tích hợp mọi sức mạnh AI của Google:
    
    1.  **Thanh bên trái:** Bộ công cụ Google AI chính hãng (Gemini, NotebookLM, ImageFX...).
    2.  **Menu chuyên gia:** Hơn 20 trợ lý ảo đóng vai chuyên gia thực chiến (Có quy trình làm việc cụ thể).
    3.  **Tính năng đặc biệt:** * Vẽ bản vẽ nhà 2D/3D.
        * Soạn thảo văn bản chuẩn Nghị định 30.
        * Xử lý Excel/Word tự động.
    
    👉 **HƯỚNG DẪN:** Chọn chuyên gia ở menu xổ xuống bên trái, tải file lên (nếu có) và bắt đầu chat!
    """)

elif not final_key:
    st.warning("👋 Vui lòng nhập Key bên tay trái để bắt đầu.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

   # -------------------------------------------------------------------------
    # MODULE 1: TIN TỨC & SÁCH (ĐÃ NÂNG CẤP TÌM KIẾM THỰC TẾ - REALTIME)
    # -------------------------------------------------------------------------
    if menu == "📰 Đọc Báo & Tóm Tắt Sách":
        st.header("📰 Chuyên Gia Tri Thức & Tin Tức")
        
        # Hiển thị ngày giờ hiện tại
        from datetime import datetime
        today_str = datetime.now().strftime("%d/%m/%Y")
        st.caption(f"📅 Hôm nay là: {today_str}")

        task = st.radio("Chế độ:", ["🔎 Tin Tức Thời Sự (Real-time)", "📚 Tóm tắt Sách/Tài liệu"], horizontal=True)
        
        if task == "🔎 Tin Tức Thời Sự (Real-time)":
            st.info("💡 Tính năng này sẽ kích hoạt Google Search để tìm tin tức mới nhất, đã được kiểm chứng.")
            topic = st.text_input("Nhập chủ đề muốn xem (VD: Bão lũ miền Trung hôm nay, Giá vàng hôm nay...):")
            
            if st.button("🔎 Tìm kiếm & Tổng hợp ngay"):
                if topic:
                    with st.spinner("Đang truy cập Google Search để lọc tin chính thống..."):
                        try:
                            # KÍCH HOẠT CÔNG CỤ GOOGLE SEARCH
                            tools_config = {'google_search_retrieval': {}}
                            
                            # Khởi tạo model với công cụ tìm kiếm
                            search_model = genai.GenerativeModel(best_model, tools=[tools_config])
                            
                            # Prompt ép buộc lấy tin xác thực
                            search_prompt = f"""
                            Hãy tìm kiếm và tổng hợp thông tin THỜI SỰ, MỚI NHẤT tính đến thời điểm hiện tại ({today_str}) về chủ đề: "{topic}".
                            
                            YÊU CẦU BẮT BUỘC:
                            1. TÍNH THỜI ĐIỂM: Chỉ lấy những tin tức mới nhất (trong 24-48h qua).
                            2. NGUỒN TIN: Chỉ tổng hợp từ các báo chính thống, uy tín.
                            3. TRÌNH BÀY: Ngắn gọn, gạch đầu dòng các ý chính.
                            """
                            
                            response = search_model.generate_content(search_prompt)
                            res_text = response.text
                            
                            st.success("✅ Đã cập nhật tin mới nhất:")
                            st.markdown(res_text)
                            st.divider()
                            play_text_to_speech(res_text)
                            
                        except Exception as e:
                            st.error(f"Lỗi kết nối Google Search: {e}")
                            st.caption("Lưu ý: Hãy đảm bảo Model bạn chọn là 'gemini-1.5-flash' hoặc 'gemini-1.5-pro' để hỗ trợ tính năng này.")
                else:
                    st.warning("Vui lòng nhập chủ đề tin tức!")

        else:
            # Phần tóm tắt sách giữ nguyên
            st.info("Tải file PDF lên hoặc dán văn bản vào dưới.")
            txt = st.text_area("Văn bản (Nếu không có file):")
            inp = file_content if file_content else txt
            if st.button("📚 Tóm tắt") and inp:
                with st.spinner("Đang đọc hiểu..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Tóm tắt nội dung sau, rút ra 5 bài học cốt lõi: {inp}").text
                    st.markdown(res)
                    play_text_to_speech(res)

    # -------------------------------------------------------------------------
    # MODULE 2: MEDIA
    # -------------------------------------------------------------------------
    elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
        st.header("🎨 Studio Đa Phương Tiện")
        mode = st.radio("Công cụ:", ["🖼️ Tạo Ảnh", "🎬 Tạo Video", "🎙️ Voice AI (Kịch bản & Đọc)"], horizontal=True)
        
        if mode == "🖼️ Tạo Ảnh":
            desc = st.text_area("Mô tả ảnh:")
            if st.button("🎨 Vẽ"):
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    p_en = model.generate_content(f"Translate to English prompt: {desc}").text
                    st.image(generate_image_url(p_en))
        
        elif mode == "🎬 Tạo Video":
            idea = st.text_area("Ý tưởng video:")
            if st.button("🎥 Tạo Prompt"):
                model = genai.GenerativeModel(best_model)
                p = model.generate_content(f"Create English Video Prompt (Sora/Runway) for: {idea}. Structure: [Subject] [Movement] [Style]").text
                st.code(p)

        elif mode == "🎙️ Voice AI (Kịch bản & Đọc)":
            st.subheader("🎙️ Tạo giọng đọc AI")
            c_conf1, c_conf2 = st.columns(2)
            is_slow = c_conf1.checkbox("🐢 Đọc chậm rãi", value=False)
            tone = c_conf2.selectbox("Cảm xúc:", ["Truyền cảm", "Vui tươi", "Nghiêm túc", "Hào hứng", "Buồn"])
            
            v_type = st.radio("Loại kịch bản:", ["🗣️ Độc thoại (Lời bình)", "👥 Hội thoại (2 người)"], horizontal=True)

            if v_type == "🗣️ Độc thoại (Lời bình)":
                topic = st.text_area("Nội dung/Chủ đề:")
                if st.button("📝 Viết & Đọc"):
                    with st.spinner("Đang xử lý..."):
                        model = genai.GenerativeModel(best_model)
                        res = model.generate_content(f"Viết kịch bản độc thoại. Cảm xúc: {tone}. Chủ đề: {topic}. Ghi chú diễn xuất trong ngoặc đơn.").text
                        st.markdown(res)
                        play_text_to_speech(res, is_slow)
            else:
                topic = st.text_area("Chủ đề cuộc trò chuyện:")
                if st.button("📝 Viết & Đọc Hội Thoại"):
                     with st.spinner("Đang xử lý..."):
                        model = genai.GenerativeModel(best_model)
                        res = model.generate_content(f"Viết hội thoại 2 người. Cảm xúc: {tone}. Chủ đề: {topic}. Ghi chú diễn xuất trong ngoặc đơn.").text
                        st.markdown(res)
                        play_text_to_speech(res, is_slow)


    # -------------------------------------------------------------------------
    # MODULE 3: CHUYÊN GIA (CORE)
    # -------------------------------------------------------------------------
    else:
        st.header(menu)
        expert_instruction = get_expert_prompt(menu)
        
        edu_append = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            c1, c2 = st.columns(2)
            sach = c1.selectbox("Bộ sách giáo khoa:", ["Cánh Diều", "Kết Nối Tri Thức Với Cuộc Sống", "Chân Trời Sáng Tạo"])
            role = c2.radio("Bạn là:", ["Học sinh", "Phụ huynh", "Giáo viên"], horizontal=True)
            edu_append = f".\nLƯU Ý: Tôi đang sử dụng bộ sách '{sach}'. Vai trò của tôi là: {role}. Hãy trả lời phù hợp với lứa tuổi và vai trò này."

        # CHAT HISTORY
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            greeting = "Xin chào! Tôi là chuyên gia lĩnh vực này (Quy trình chuẩn). "
            if file_content: greeting += "Tôi đã nhận được file bạn gửi. "
            st.session_state.history[menu].append({"role": "assistant", "content": greeting})

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
                with st.spinner("Đang xử lý theo quy trình..."):
                    try:
                        full_p = [prompt + edu_append]
                        if file_content: full_p.append(f"DỮ LIỆU TỪ FILE:\n{file_content}")
                        
                        model = genai.GenerativeModel(best_model, system_instruction=expert_instruction)
                        response = model.generate_content(full_p)
                        full_txt = response.text

                        p2d = re.search(r'###PROMPT_2D###(.*?)###END_PROMPT###', full_txt, re.DOTALL)
                        p3d = re.search(r'###PROMPT_3D###(.*?)###END_PROMPT###', full_txt, re.DOTALL)
                        txt_show = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', full_txt, flags=re.DOTALL)
                        
                        st.markdown(txt_show.strip())
                        
                        if p2d or p3d:
                            st.divider()
                            c_a, c_b = st.columns(2)
                            if p2d:
                                with c_a: st.image(generate_image_url("Blueprint. " + p2d.group(1)), caption="Bản vẽ 2D")
                            if p3d:
                                with c_b: st.image(generate_image_url("Architecture render. " + p3d.group(1)), caption="Phối cảnh 3D")
                        
                        st.session_state.history[menu].append({"role": "assistant", "content": full_txt})
                    except Exception as e: st.error(f"Lỗi: {e}")
