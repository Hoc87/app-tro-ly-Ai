import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import re  # Thư viện xử lý văn bản (cắt bỏ ngoặc đơn)
from PIL import Image
import PyPDF2
import pandas as pd

# =============================================================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ
# =============================================================================

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

# --- HÀM LÀM SẠCH VĂN BẢN (TTS) ---
def clean_text_for_tts(text):
    """Loại bỏ nội dung trong ngoặc đơn (...) để AI không đọc hướng dẫn diễn xuất."""
    if not text: return ""
    clean = re.sub(r'\([^)]*\)', '', text) # Xóa (...)
    clean = re.sub(r'\[[^]]*\]', '', clean) # Xóa [...]
    clean = clean.replace('*', '').replace('#', '') # Xóa ký tự markdown
    return clean.strip()

# --- HÀM ĐỌC VĂN BẢN (TTS) ---
def play_text_to_speech(text_content):
    try:
        text_to_read = clean_text_for_tts(text_content)
        if len(text_to_read) < 2:
            st.warning("⚠️ Chỉ có hướng dẫn diễn xuất, không có lời thoại thực tế.")
            return

        tts = gTTS(text=text_to_read, lang='vi')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes, format='audio/mp3')
        st.caption("🔊 Đang đọc (Đã lọc bỏ ghi chú trong ngoặc)...")
    except Exception as e:
        st.warning(f"Lỗi tạo giọng nói: {e}")

# --- HÀM CHỌN MODEL ---
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

# =============================================================================
# 2. "BỘ NÃO" CHUYÊN GIA (EXPERT PERSONAS)
# =============================================================================
def get_expert_system_instruction(menu_name):
    # Định nghĩa chi tiết từng vai trò
    personas = {
        "👔 Nhân Sự - Tuyển Dụng - CV": """
            Bạn là Giám đốc Nhân sự (CHRO) với 20 năm kinh nghiệm.
            Nhiệm vụ: Tư vấn chiến lược nhân sự, sửa CV chuẩn ATS, phỏng vấn mô phỏng.
            Phong cách: Chuyên nghiệp, thấu hiểu tâm lý, ngôn từ chuẩn mực doanh nghiệp.
        """,
        "⚖️ Luật - Hợp Đồng - Hành Chính": """
            Bạn là Luật sư Cấp cao và Chuyên gia Pháp lý. 
            Nhiệm vụ: Soạn thảo hợp đồng chặt chẽ, tư vấn luật chính xác theo luật pháp Việt Nam.
            Phong cách: Cẩn trọng, chính xác từng từ, luôn cảnh báo rủi ro.
        """,
        "💰 Kinh Doanh & Marketing": """
            Bạn là CMO và Chuyên gia Chiến lược Kinh doanh thực chiến.
            Nhiệm vụ: Lập kế hoạch Marketing, phân tích thị trường, tối ưu doanh thu (ROI, KPI).
            Phong cách: Sáng tạo, tư duy đột phá (Growth Hacking).
        """,
        "🏢 Giám Đốc & Quản Trị (CEO)": """
            Bạn là Cố vấn Chiến lược cho CEO. Tư duy: Quản trị rủi ro, tầm nhìn dài hạn và tối ưu vận hành.
        """,
        "🛒 TMĐT (Shopee/TikTok Shop)": """
            Bạn là Mega Seller trên Shopee, TikTok Shop.
            Nhiệm vụ: Tối ưu SEO từ khóa, viết mô tả sản phẩm thôi miên, chiến lược Livestream nghìn đơn.
            Phong cách: Năng động, bắt trend nhanh, ngôn từ thu hút (FOMO).
        """,
        "💻 Lập Trình - Freelancer - Digital": """
            Bạn là Senior Solutions Architect và Full-stack Developer.
            Nhiệm vụ: Code sạch (Clean Code), tối ưu thuật toán, debug triệt để.
        """,
        "❤️ Y Tế - Sức Khỏe - Gym": """
            Bạn là Bác sĩ Chuyên khoa và Chuyên gia Dinh dưỡng.
            Nhiệm vụ: Tư vấn sức khỏe dựa trên y học chứng cứ. Luôn nhắc đi khám nếu bệnh nặng.
        """,
        "✈️ Du Lịch - Lịch Trình - Vi Vu": """
            Bạn là Hướng dẫn viên du lịch 5 sao.
            Nhiệm vụ: Lên lịch trình chi tiết, tìm hidden gems. Phong cách: Hào hứng, trải nghiệm.
        """,
        "🧠 Tâm Lý - Cảm Xúc - Tinh Thần": """
            Bạn là Chuyên gia Tâm lý học lâm sàng. Nhiệm vụ: Lắng nghe, chữa lành, không phán xét.
        """,
        "🏗️ Kiến Trúc - Nội Thất - Xây Dựng": """
            Bạn là Kiến trúc sư trưởng. Tư vấn thiết kế, vật liệu, phong thủy và chi phí.
        """,
        "🏠 Bất Động Sản & Xe Sang": """
            Bạn là Trùm môi giới Bất động sản và Xe sang. Phân tích đầu tư, định giá, kỹ năng đàm phán.
        """
    }
    selected_persona = personas.get(menu_name, "Bạn là trợ lý AI đa năng, thông minh và hữu ích.")
    return f"""
    {selected_persona}
    NGUYÊN TẮC:
    1. Thực chiến: Đưa giải pháp áp dụng ngay.
    2. Sâu sắc: Phân tích gốc rễ.
    3. Tương tác: Hỏi lại nếu thiếu thông tin.
    """

# =============================================================================
# 3. GIAO DIỆN & LOGIC CHÍNH
# =============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # --- 1. CẤU HÌNH TÀI KHOẢN (ĐÃ KHÔI PHỤC HƯỚNG DẪN) ---
    st.subheader("🔑 Tài khoản sử dụng")
    key_option = st.radio("Chế độ:", ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn"], label_visibility="collapsed")
    
    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server")
        except:
            st.error("❌ Chưa cấu hình Key chung")
    else: 
        # ĐÃ KHÔI PHỤC LẠI PHẦN HƯỚNG DẪN CHI TIẾT NÀY
        st.info("""
        **👇 Hướng dẫn lấy Key (30s):**
        1. Vào **[Google AI Studio](https://aistudio.google.com/)**
        2. Bấm **Get API key** -> **Create API key**.
        3. Copy và dán vào ô dưới.
        """)
        final_key = st.text_input("Dán API Key VIP:", type="password")
        if final_key: st.success("✅ Đã nhận Key")
    
    st.divider()
    
    # --- 2. UPLOAD FILE ---
    st.subheader("📎 Tài liệu đính kèm")
    uploaded_file = st.file_uploader("Ảnh/PDF/Excel...", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx'], label_visibility="collapsed")
    file_content = process_uploaded_file(uploaded_file)
    if file_content: st.info(f"✅ Đã đọc: {uploaded_file.name}")
    
    st.divider()

    # --- 3. MENU CHỨC NĂNG ---
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio("Lĩnh vực:", [
        "🏠 Trang Chủ & Giới Thiệu", 
        "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
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
        "🏗️ Kiến Trúc - Nội Thất - Xây Dựng",
        "🎤 Sự Kiện - MC - Hội Nghị",
        "🏠 Bất Động Sản & Xe Sang"
    ])

# --- NỘI DUNG CHÍNH ---

if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("""
        ### 🚀 Rin.Ai - Super App Đa Phương Tiện
        Chào mừng bạn đến với phiên bản Rin.Ai PRO.
        
        **Điểm đặc biệt:**
        * **Chuyên gia thực chiến:** Mỗi lĩnh vực đều có một AI đóng vai chuyên gia với 20 năm kinh nghiệm.
        * **Media Pro:** Tạo Prompt video chuẩn Hollywood (Tiếng Anh) & Kịch bản giọng nói tự động lọc bỏ ghi chú.
        * **Đa phương tiện:** Hiểu hình ảnh, đọc PDF, phân tích Excel.
        
        ---
        ### 👨‍🏫 Liên hệ đào tạo & Hợp tác:
        ## **Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        """)
    with c2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg")

elif not final_key:
    st.warning("👋 Vui lòng nhập Key bên tay trái để bắt đầu.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # -------------------------------------------------------------------------
    # MODULE 1: TIN TỨC & SÁCH (CÓ VOICE)
    # -------------------------------------------------------------------------
    if menu == "📰 Đọc Báo & Tóm Tắt Sách":
        st.header("📰 Chuyên Gia Tri Thức & Tổng Hợp")
        task = st.radio("Chế độ:", ["🔎 Tổng hợp Tin Tức", "📚 Tóm tắt Sách/Tài liệu"], horizontal=True)
        
        if task == "🔎 Tổng hợp Tin Tức":
            topic = st.text_input("Nhập chủ đề (VD: Xu hướng AI 2025):")
            if st.button("🔎 Phân tích ngay"):
                if topic:
                    with st.spinner("Đang quét thông tin..."):
                        model = genai.GenerativeModel(best_model)
                        res = model.generate_content(f"Đóng vai biên tập viên tin tức. Tổng hợp tin tức mới nhất và xu hướng quan trọng về: {topic}. Trình bày ngắn gọn, dễ hiểu.").text
                        st.markdown(res)
                        st.divider()
                        play_text_to_speech(res)
        else:
            st.info("Tải file PDF lên hoặc dán văn bản vào dưới.")
            text_input = st.text_area("Văn bản cần tóm tắt:")
            final_in = file_content if file_content else text_input
            
            if st.button("📚 Tóm tắt") and final_in:
                with st.spinner("Đang đọc hiểu..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Tóm tắt nội dung sau, rút ra 5 bài học cốt lõi: {final_in}").text
                    st.markdown(res)
                    st.divider()
                    play_text_to_speech(res)

    # -------------------------------------------------------------------------
    # MODULE 2: MEDIA STUDIO (LOGIC PHỨC TẠP)
    # -------------------------------------------------------------------------
    elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
        st.header("🎨 Studio Đa Phương Tiện Chuyên Nghiệp")
        mode = st.radio("Công cụ:", ["🖼️ Tạo Ảnh", "🎬 Tạo Video (Sora/Veo)", "🎙️ Kịch Bản & Voice"], horizontal=True)
        st.divider()

        # 2.1 TẠO ẢNH
        if mode == "🖼️ Tạo Ảnh":
            desc = st.text_area("Mô tả ảnh muốn vẽ:", height=100)
            if st.button("🎨 Vẽ Ngay"):
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    prompt_en = model.generate_content(f"Translate to detailed English prompt for image generation: {desc}").text
                    final_url = f"https://image.pollinations.ai/prompt/{prompt_en.replace(' ', '%20')}?nologo=true"
                    st.image(final_url)
        
        # 2.2 TẠO VIDEO (ÉP BUỘC TIẾNG ANH CHUẨN KỸ THUẬT)
        elif mode == "🎬 Tạo Video (Sora/Veo)":
            st.info("🔥 Chế độ này sẽ tạo Prompt Tiếng Anh chuẩn Hollywood cho Sora, Runway, Kling.")
            idea = st.text_area("Mô tả ý tưởng video (Tiếng Việt):", height=100)
            if st.button("🎥 Viết Prompt Chuẩn"):
                if idea:
                    with st.spinner("Đang thiết kế góc máy & ánh sáng..."):
                        model = genai.GenerativeModel(best_model)
                        # System Instruction cục bộ cực mạnh cho Video
                        sys_video = """
                        ACT AS: Expert AI Video Prompt Engineer.
                        TASK: Convert user idea into a HIGH-END VIDEO PROMPT.
                        RULES: 
                        1. OUTPUT ONLY ENGLISH.
                        2. Structure: [Subject] + [Action] + [Camera Movement] + [Lighting] + [Tech Specs].
                        3. Keywords required: 8k, cinematic, photorealistic, depth of field, slow motion, Unreal Engine 5.
                        """
                        res = model.generate_content(f"{sys_video}\nInput: {idea}").text
                        st.success("✅ Prompt (Copy dòng dưới để tạo video):")
                        st.code(res, language="text")
                else: st.warning("Nhập ý tưởng trước!")

        # 2.3 TẠO VOICE (TÁCH LỜI THOẠI VÀ DIỄN XUẤT)
        elif mode == "🎙️ Kịch Bản & Voice":
            v_type = st.radio("Loại:", ["Độc thoại", "Hội thoại (2 người)"], horizontal=True)
            
            # System Instruction cho biên kịch
            sys_writer = "Bạn là biên kịch tài ba. Quy tắc: Hướng dẫn diễn xuất/âm thanh phải để trong ngoặc đơn (...). Lời thoại phải tự nhiên."
            model = genai.GenerativeModel(best_model, system_instruction=sys_writer)

            if v_type == "Độc thoại":
                c1, c2, c3 = st.columns(3)
                gender = c1.selectbox("Giới tính:", ["Nam", "Nữ"])
                region = c2.selectbox("Giọng:", ["Bắc (Chuẩn)", "Trung", "Nam"])
                tone = c3.selectbox("Cảm xúc:", ["Trầm ấm", "Vui tươi", "Nghiêm túc"])
                topic = st.text_area("Nội dung:")
                if st.button("🎙️ Tạo & Đọc"):
                    if topic:
                        with st.spinner("Đang viết..."):
                            res = model.generate_content(f"Viết kịch bản lời bình cho giọng {gender}, vùng {region}, cảm xúc {tone}. Chủ đề: {topic}.").text
                            st.subheader("Kịch bản chi tiết:")
                            st.markdown(res)
                            st.divider()
                            play_text_to_speech(res) # Code tự lọc ngoặc đơn
            else:
                st.info("Hội thoại 2 người")
                topic = st.text_area("Chủ đề hội thoại:")
                if st.button("🗣️ Tạo & Đọc"):
                    if topic:
                        with st.spinner("Đang viết..."):
                            res = model.generate_content(f"Viết đoạn hội thoại ngắn, hài hước giữa 2 người về: {topic}. Nhớ ghi chú hành động trong ngoặc đơn.").text
                            st.subheader("Kịch bản:")
                            st.markdown(res)
                            st.divider()
                            play_text_to_speech(res)

    # -------------------------------------------------------------------------
    # MODULE 3: CÁC CHUYÊN GIA TƯ VẤN (CHATBOTS)
    # -------------------------------------------------------------------------
    else:
        st.header(menu)
        
        # Lấy System Instruction "xịn" từ hàm cấu hình ở trên
        expert_instruction = get_expert_system_instruction(menu)
        
        # Xử lý riêng cho Giáo Dục
        edu_append = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            c1, c2 = st.columns(2)
            sach = c1.selectbox("Bộ sách:", ["Cánh Diều", "Kết Nối Tri Thức", "Chân Trời Sáng Tạo"])
            role = c2.radio("Vai trò:", ["Học sinh", "Giáo viên"], horizontal=True)
            edu_append = f". Lưu ý: Đang dùng sách '{sach}'. Vai trò người hỏi: {role}."

        # Khởi tạo Chat History
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            welcome_msg = "Xin chào! Tôi là chuyên gia trong lĩnh vực này. Tôi có thể giúp gì cho bạn?"
            st.session_state.history[menu].append({"role": "assistant", "content": welcome_msg})

        # Hiển thị lịch sử chat
        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Ô nhập liệu
        if prompt := st.chat_input("Nhập câu hỏi cho chuyên gia..."):
            with st.chat_message("user"):
                st.markdown(prompt)
                if file_content: st.caption("📎 [Đã đính kèm file]")
            st.session_state.history[menu].append({"role": "user", "content": prompt})

            # Xử lý trả lời
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang phân tích..."):
                    try:
                        # Ghép Prompt + File + Edu Logic
                        full_prompt = [prompt + edu_append]
                        if file_content:
                            if isinstance(file_content, str): full_prompt.append(f"\n\nCONTEXT FILE:\n{file_content}")
                            else: full_prompt.append(file_content) # Nếu là ảnh

                        # Gọi Model với System Instruction chuyên sâu
                        model = genai.GenerativeModel(best_model, system_instruction=expert_instruction)
                        response = model.generate_content(full_prompt)
                        
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi kết nối: {e}")
