import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
from PIL import Image
import PyPDF2
import pandas as pd

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Siêu Trợ Lý AI", page_icon="💎", layout="wide")

# --- HÀM XỬ LÝ FILE UPLOAD ---
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

# --- HÀM TỰ ĐỘNG CHỌN MODEL ---
@st.cache_resource
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
        for p in priority:
            for m in models:
                if p in m: return m
        return "gemini-pro"
    except: return None

# --- SIDEBAR: CẤU HÌNH ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # 1. CẤU HÌNH TÀI KHOẢN
    st.subheader("🔑 Tài khoản sử dụng")
    key_option = st.radio("Chế độ:", ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn"], label_visibility="collapsed")
    
    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server")
        except: st.error("❌ Chưa cấu hình Key chung")
    else: 
        st.info("""
        **👇 Hướng dẫn lấy Key (30s):**
        1. Vào **[Google AI Studio](https://aistudio.google.com/)**
        2. Bấm **Get API key** -> **Create API key**.
        3. Copy và dán vào ô dưới.
        """)
        final_key = st.text_input("Dán API Key VIP:", type="password")
        if final_key: st.success("✅ Đã nhận Key")

    st.divider()

    # 2. MENU CHỨC NĂNG
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio(
        "Lĩnh vực:",
        [
            "🏠 Trang Chủ & Giới Thiệu", 
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "📰 Đọc Báo & Tóm Tắt Sách",
            "🎨 Thiết Kế & Media (Ảnh/Video/Voice)", # <-- TẬP TRUNG VÀO ĐÂY
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
            "🏗️ Kiến Trúc - Nội Thất - Xây Dựng",
            "🎤 Sự Kiện - MC - Hội Nghị",
            "🏠 Bất Động Sản & Xe Sang"
        ]
    )

# --- NỘI DUNG CHÍNH ---

# 1. TRANG GIỚI THIỆU
if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 🚀 Rin.Ai - Super App Đa Phương Tiện
        Chào mừng bạn đến với phiên bản Rin.Ai PRO. Chúng tôi tích hợp sức mạnh của Google để xử lý mọi định dạng dữ liệu: Hình ảnh, Video, Giọng nói.
        
        ---
        ### 👨‍🏫 Đào tạo & Liên hệ:
        ## **Chuyên gia: Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        > **📢 ĐẶC BIỆT:** Nếu bạn có nhu cầu học AI bài bản để áp dụng vào công việc thực tế hoặc đời sống, hãy liên hệ ngay **Mr. Học** để được hướng dẫn trực tiếp.
        """)
    with col2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg")

# 2. KIỂM TRA KEY
elif not final_key:
    st.warning("👋 Vui lòng nhập Key bên tay trái để sử dụng.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # =================================================================================
    # 🔥 MODULE ĐẶC BIỆT: THIẾT KẾ & MEDIA (ĐÚNG YÊU CẦU MỚI)
    # =================================================================================
    if menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
        st.header("🎨 Studio Sáng Tạo Đa Phương Tiện")
        
        # THANH UPLOAD FILE (LUÔN HIỆN Ở ĐÂY)
        with st.expander("📎 Đính kèm tài liệu tham khảo (Ảnh mẫu/Kịch bản...)", expanded=False):
            uploaded_file = st.file_uploader("Chọn file:", type=['png', 'jpg', 'pdf', 'txt', 'docx'])
            file_content = process_uploaded_file(uploaded_file)
            if file_content: st.success(f"Đã nhận: {uploaded_file.name}")

        # MENU CON: CHỌN CÔNG CỤ CỤ THỂ
        media_tool = st.radio(
            "👉 Bạn muốn làm gì?",
            ["🖼️ Tạo Ảnh (Trực tiếp/Prompt)", "🎬 Tạo Video (Prompt Veo/Sora)", "🎙️ Tạo Voice/Hội Thoại"],
            horizontal=True
        )
        st.divider()

        # --- 1. CÔNG CỤ ẢNH ---
        if media_tool == "🖼️ Tạo Ảnh (Trực tiếp/Prompt)":
            img_mode = st.selectbox("Chế độ:", ["Vẽ Ngay Lập Tức (Tại App)", "Sinh Prompt (Cho Midjourney/Canva)"])
            
            if img_mode == "Vẽ Ngay Lập Tức (Tại App)":
                desc = st.text_area("Mô tả bức tranh bạn muốn vẽ:", height=100, placeholder="VD: Một con mèo máy Doraemon ngầu...")
                if st.button("🎨 Vẽ Ngay"):
                    if desc:
                        with st.spinner("Đang vẽ..."):
                            model = genai.GenerativeModel(best_model)
                            trans = model.generate_content(f"Translate to detailed English prompt: {desc}").text
                            final = trans.replace(" ", "%20")
                            st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Rin.Ai Generated")
            else:
                desc = st.text_area("Ý tưởng ảnh:", placeholder="VD: Poster quảng cáo giày thể thao...")
                if st.button("📝 Viết Prompt"):
                    model = genai.GenerativeModel(best_model)
                    st.write(model.generate_content(f"Đóng vai chuyên gia Art Director. Viết 3 prompt tiếng Anh chi tiết cho Midjourney v6 về: {desc}. Thêm thông số --ar 16:9 --v 6.0 --style raw. Giải thích tiếng Việt.").text)

        # --- 2. CÔNG CỤ VIDEO (VEO3/SORA) ---
        elif media_tool == "🎬 Tạo Video (Prompt Veo/Sora)":
            st.info("Chuyên gia viết Prompt cho: Google Veo, Sora, Kling, InVideo.")
            platform = st.selectbox("Nền tảng mục tiêu:", ["Google Veo (Veo3)", "OpenAI Sora", "Kling AI", "InVideo", "Runway Gen-3"])
            video_idea = st.text_area("Mô tả video bạn muốn làm:", height=100)
            
            if st.button("🎬 Viết Prompt Video Chuẩn"):
                if video_idea:
                    model = genai.GenerativeModel(best_model)
                    prompt = f"""
                    Đóng vai Đạo diễn phim chuyên nghiệp và Chuyên gia Prompt cho {platform}.
                    Nhiệm vụ: Viết Prompt chi tiết để tạo video về: "{video_idea}".
                    YÊU CẦU KỸ THUẬT CHO {platform}:
                    - Mô tả Góc máy (Camera Angles): Wide, Close-up, Drone shot...
                    - Chuyển động (Movement): Pan, Tilt, Zoom, Dolly...
                    - Ánh sáng & Màu sắc (Lighting & Color).
                    - Âm thanh (nếu công cụ hỗ trợ).
                    - Prompt phải viết bằng Tiếng Anh chuẩn.
                    """
                    with st.spinner("Đang xử lý kỹ thuật..."):
                        st.markdown(model.generate_content(prompt).text)
                        st.success(f"Copy Prompt trên và dán vào {platform} để tạo video!")

        # --- 3. CÔNG CỤ VOICE (NÂNG CẤP VÙNG MIỀN/HỘI THOẠI) ---
        elif media_tool == "🎙️ Tạo Voice/Hội Thoại":
            voice_type = st.radio("Loại kịch bản:", ["Độc thoại (1 người)", "Hội thoại (2 người)"], horizontal=True)
            
            if voice_type == "Độc thoại (1 người)":
                c1, c2, c3 = st.columns(3)
                gender = c1.selectbox("Giới tính:", ["Nam", "Nữ"])
                region = c2.selectbox("Vùng miền:", ["Giọng Bắc", "Giọng Trung", "Giọng Nam"])
                tone = c3.selectbox("Cảm xúc:", ["Trầm ấm", "Vui tươi", "Nghiêm túc", "Buồn"])
                topic = st.text_area("Nội dung cần đọc:")
                
                if st.button("📝 Viết Kịch Bản Voice"):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Viết kịch bản lời bình cho 1 người ({gender}, {region}, {tone}). Chủ đề: {topic}. Yêu cầu: Dùng từ ngữ địa phương chuẩn {region}. Đánh dấu [Ngắt nghỉ], [Nhấn mạnh].").text
                    st.markdown(res)
                    # Nút nghe thử
                    try:
                        tts = gTTS(text=res[:300], lang='vi')
                        audio_bytes = io.BytesIO()
                        tts.write_to_fp(audio_bytes)
                        st.audio(audio_bytes, format='audio/mp3')
                    except: pass

            else: # HỘI THOẠI 2 NGƯỜI
                st.markdown("#### Thiết lập nhân vật")
                c1, c2 = st.columns(2)
                with c1:
                    st.info("Nhân vật A")
                    ga = st.selectbox("Giới tính A", ["Nam", "Nữ"], key="ga")
                    ra = st.selectbox("Vùng miền A", ["Bắc", "Trung", "Nam"], key="ra")
                with c2:
                    st.info("Nhân vật B")
                    gb = st.selectbox("Giới tính B", ["Nam", "Nữ"], key="gb")
                    rb = st.selectbox("Vùng miền B", ["Bắc", "Trung", "Nam"], key="rb")
                
                topic = st.text_area("Chủ đề cuộc trò chuyện:")
                if st.button("🗣️ Tạo Hội Thoại"):
                    model = genai.GenerativeModel(best_model)
                    prompt = f"""
                    Viết kịch bản hội thoại tự nhiên giữa:
                    - NV A ({ga}, giọng {ra})
                    - NV B ({gb}, giọng {rb})
                    - Chủ đề: {topic}
                    YÊU CẦU:
                    - Phải thể hiện rõ từ ngữ địa phương (VD: Nam dùng 'chén/muỗng', Bắc dùng 'bát/thìa').
                    - Có chỉ dẫn cảm xúc (Cười lớn), (Thở dài).
                    """
                    st.markdown(model.generate_content(prompt).text)

    # =================================================================================
    # CÁC MODULE CHATBOT KHÁC (CÓ UPLOAD FILE TRÊN KHUNG CHAT)
    # =================================================================================
    else:
        st.header(menu)
        
        # KHUNG UPLOAD FILE (NẰM NGAY TRÊN KHUNG CHAT - TIỆN LỢI)
        with st.expander("📎 Đính kèm tài liệu cho Trợ lý (Ảnh/PDF/Excel)", expanded=True):
            uploaded_file = st.file_uploader("Kéo thả file vào đây:", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx'], label_visibility="collapsed")
            file_content = None
            if uploaded_file:
                file_content = process_uploaded_file(uploaded_file)
                st.success(f"✅ Đã tải: {uploaded_file.name}")

        # LOGIC GIÁO DỤC
        edu_wrapper = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            col1, col2 = st.columns(2)
            sach = col1.selectbox("📚 Bộ Sách:", ["Cánh Diều", "Chân Trời Sáng Tạo", "Kết Nối Tri Thức", "Sách Cũ"])
            vai_tro = col2.radio("Bạn là:", ["Học sinh/Phụ huynh", "Giáo viên"], horizontal=True)
            if vai_tro == "Học sinh/Phụ huynh":
                edu_wrapper = f" .LƯU Ý: Tôi là HS học sách '{sach}'. Hãy giảng giải chi tiết, KHÔNG đưa đáp án ngay. Hướng dẫn phương pháp giải."
            else:
                edu_wrapper = f" .Tôi là GV dạy sách '{sach}'. Hỗ trợ soạn giáo án."

        # SYSTEM INSTRUCTION
        consultant_logic = """
        QUY TẮC: 
        1. ƯU TIÊN SỐ 1: Nếu có File đính kèm -> Phân tích File trước.
        2. Nếu hỏi ngắn -> HỎI LẠI bối cảnh.
        3. Đưa giải pháp thực chiến.
        """
        
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu gì?",
            "📰 Đọc Báo & Tóm Tắt Sách": "Hãy gửi file sách hoặc nhập chủ đề báo chí bạn muốn tôi tổng hợp.",
            # ... (Giữ nguyên)
        }
        
        # Chat History
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            st.session_state.history[menu].append({"role": "assistant", "content": initial_greetings.get(menu, f"Xin chào chuyên gia {menu} đây.")})

        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        sys_prompt = f"Bạn là chuyên gia {menu}. {consultant_logic}"
        model = genai.GenerativeModel(best_model, system_instruction=sys_prompt)
        
        if prompt := st.chat_input("Nhập câu hỏi..."):
            with st.chat_message("user"):
                st.markdown(prompt)
                if file_content: st.caption(f"📎 [File đính kèm]")
            
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Đang phân tích..."):
                    try:
                        final_input = [prompt + edu_wrapper]
                        if file_content:
                            if isinstance(file_content, str): final_input.append(f"\nFILE:\n{file_content}")
                            else: final_input.append(file_content)

                        response = model.generate_content(final_input)
                        st.markdown(response.text)
                        
                        # CHỈ HIỆN VOICE Ở CÁC MỤC CẦN THIẾT (MEDIA, ĐỌC BÁO, GIÁO DỤC...)
                        allowed_voice = ["📰 Đọc Báo & Tóm Tắt Sách", "🎓 Giáo Dục & Đào Tạo", "✈️ Du Lịch - Lịch Trình - Vi Vu", "🎤 Sự Kiện - MC - Hội Nghị"]
                        if menu in allowed_voice:
                            try:
                                tts = gTTS(text=response.text[:500], lang='vi')
                                audio_bytes = io.BytesIO()
                                tts.write_to_fp(audio_bytes)
                                st.audio(audio_bytes, format='audio/mp3')
                            except: pass

                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
