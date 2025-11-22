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

# --- HÀM ĐỌC VĂN BẢN (TTS) - ĐÃ SỬA ĐỂ ĐỌC ĐÚNG NỘI DUNG ---
def play_text_to_speech(text_content):
    try:
        # Tạo file âm thanh từ nội dung text_content
        tts = gTTS(text=text_content, lang='vi')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        # Hiển thị trình phát ngay lập tức
        st.audio(audio_bytes, format='audio/mp3')
        st.caption("🔊 Đang đọc nội dung trên...")
    except Exception as e:
        st.warning("Nội dung quá dài hoặc lỗi kết nối server giọng nói. Vui lòng thử đoạn ngắn hơn.")

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
    except:
        return None

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
        except:
            st.error("❌ Chưa cấu hình Key chung")
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
    
    # 2. UPLOAD FILE
    st.subheader("📎 Đính kèm tài liệu")
    st.caption("Tải ảnh, PDF, Excel để AI phân tích ngay.")
    uploaded_file = st.file_uploader("Chọn file:", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx'], label_visibility="collapsed")
    
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        st.info(f"✅ Đã nhận: {uploaded_file.name}")

    st.divider()

    # 3. MENU CHỨC NĂNG
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio(
        "Lĩnh vực:",
        [
            "🏠 Trang Chủ & Giới Thiệu", 
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "📰 Đọc Báo & Tóm Tắt Sách", # <-- CÓ VOICE
            "🎨 Thiết Kế & Media (Ảnh/Video/Voice)", # <-- CÓ VOICE
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

if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 🚀 Rin.Ai - Super App Đa Phương Tiện
        Chào mừng bạn đến với phiên bản Rin.Ai PRO. Chúng tôi tích hợp sức mạnh của Google để xử lý mọi định dạng dữ liệu: Hình ảnh, Tài liệu, Giọng nói.
        
        ---
        ### 👨‍🏫 Đào tạo & Liên hệ:
        ## **Chuyên gia: Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        
        > **📢 ĐẶC BIỆT:** Nếu bạn có nhu cầu học AI bài bản để áp dụng vào công việc thực tế hoặc đời sống, hãy liên hệ ngay **Mr. Học** để được hướng dẫn trực tiếp.
        """)
    with col2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg")

elif not final_key:
    st.warning("👋 Vui lòng nhập Key bên tay trái để sử dụng.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # =================================================================================
    # 🔥 MODULE: ĐỌC BÁO & TÓM TẮT SÁCH (CÓ VOICE)
    # =================================================================================
    if menu == "📰 Đọc Báo & Tóm Tắt Sách":
        st.header("📰 Chuyên Gia Tri Thức (Có đọc giọng nói)")
        
        task_type = st.radio("Bạn muốn:", ["🔎 Tìm & Tổng hợp Tin Tức", "📚 Tóm tắt Sách/Tài liệu"], horizontal=True)
        
        if task_type == "🔎 Tìm & Tổng hợp Tin Tức":
            topic = st.text_input("Nhập chủ đề (VD: Xu hướng AI 2025):")
            if st.button("🔎 Tổng hợp ngay"):
                if topic:
                    with st.spinner("Đang quét thông tin..."):
                        model = genai.GenerativeModel(best_model)
                        res = model.generate_content(f"Tổng hợp tin tức mới nhất và xu hướng quan trọng về: {topic}. Trình bày ngắn gọn, dễ hiểu.").text
                        st.markdown(res)
                        st.divider()
                        play_text_to_speech(res) # <-- ĐỌC NỘI DUNG VỪA TẠO
        else:
            st.info("Dán nội dung sách hoặc tải file PDF bên trái để tóm tắt.")
            text_input = st.text_area("Hoặc dán văn bản vào đây:")
            
            # Ưu tiên đọc file nếu có
            final_input = None
            if file_content: final_input = file_content
            elif text_input: final_input = text_input
            
            if st.button("📚 Tóm tắt") and final_input:
                with st.spinner("Đang đọc và tóm tắt..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Tóm tắt nội dung sau, rút ra 5 bài học chính: {final_input}").text
                    st.markdown(res)
                    st.divider()
                    play_text_to_speech(res) # <-- ĐỌC NỘI DUNG VỪA TẠO

    # =================================================================================
    # 🔥 MODULE: THIẾT KẾ & MEDIA (CÓ VOICE CHUYÊN SÂU)
    # =================================================================================
    elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
        st.header("🎨 Studio Đa Phương Tiện")
        media_mode = st.radio("Công cụ:", ["🖼️ Tạo Ảnh (Vẽ/Prompt)", "🎬 Tạo Video (Prompt Veo/Sora)", "🎙️ Tạo Voice/Hội Thoại"], horizontal=True)
        st.divider()

        # --- 1. TẠO ẢNH ---
        if media_mode == "🖼️ Tạo Ảnh (Vẽ/Prompt)":
            img_sub = st.selectbox("Chế độ:", ["Vẽ Ngay Lập Tức (Tại App)", "Sinh Prompt (Midjourney/Canva)"])
            if img_sub == "Vẽ Ngay Lập Tức (Tại App)":
                desc = st.text_area("Mô tả ảnh:", height=100)
                if st.button("🎨 Vẽ Ngay"):
                    with st.spinner("Đang vẽ..."):
                        model = genai.GenerativeModel(best_model)
                        trans = model.generate_content(f"Translate to detailed English prompt: {desc}").text
                        final = trans.replace(" ", "%20")
                        st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true")
            else:
                idea = st.text_area("Ý tưởng:")
                if st.button("Tạo Prompt"):
                    model = genai.GenerativeModel(best_model)
                    st.write(model.generate_content(f"Viết 3 prompt Midjourney v6 cho: {idea}").text)

        # --- 2. TẠO VIDEO ---
        elif media_mode == "🎬 Tạo Video (Prompt Veo/Sora)":
            st.info("Viết Prompt chuyên sâu cho Google Veo, Sora, Kling.")
            veo_idea = st.text_area("Mô tả video:", height=100)
            if st.button("Viết Prompt Video"):
                 model = genai.GenerativeModel(best_model)
                 st.write(model.generate_content(f"Viết prompt video AI chi tiết (Góc máy, ánh sáng, chuyển động) cho: {veo_idea}").text)

        # --- 3. TẠO VOICE (FIX LỖI ĐỌC SAI) ---
        elif media_mode == "🎙️ Tạo Voice/Hội Thoại":
            voice_type = st.radio("Loại kịch bản:", ["Độc thoại (1 người)", "Hội thoại (2 người)"], horizontal=True)
            
            if voice_type == "Độc thoại (1 người)":
                c1, c2, c3 = st.columns(3)
                gender = c1.selectbox("Giới tính:", ["Nam", "Nữ"])
                region = c2.selectbox("Vùng miền:", ["Giọng Bắc (Chuẩn)", "Giọng Trung", "Giọng Nam"])
                tone = c3.selectbox("Cảm xúc:", ["Trầm ấm", "Vui tươi", "Nghiêm túc"])
                topic = st.text_area("Nội dung cần đọc:")
                
                if st.button("📝 Viết Kịch Bản & Đọc"):
                    if topic:
                        with st.spinner("Đang viết..."):
                            model = genai.GenerativeModel(best_model)
                            res = model.generate_content(f"Viết kịch bản lời bình ngắn gọn cho 1 người ({gender}, {region}, {tone}). Chủ đề: {topic}. Dùng từ ngữ địa phương {region}.").text
                            st.markdown(res)
                            st.divider()
                            play_text_to_speech(res) # <-- ĐỌC ĐÚNG NỘI DUNG NÀY
                    else: st.warning("Nhập nội dung!")

            else: # HỘI THOẠI 2 NGƯỜI
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
                if st.button("🗣️ Tạo & Đọc Hội Thoại"):
                    if topic:
                        with st.spinner("Đang viết kịch bản..."):
                            model = genai.GenerativeModel(best_model)
                            res = model.generate_content(f"""
                            Viết kịch bản hội thoại ngắn (khoảng 200 từ) giữa:
                            - A ({ga}, giọng {ra}) và B ({gb}, giọng {rb}).
                            - Chủ đề: {topic}.
                            - Dùng từ ngữ địa phương đặc trưng.
                            """).text
                            st.markdown(res)
                            st.divider()
                            play_text_to_speech(res) # <-- ĐỌC ĐÚNG NỘI DUNG NÀY
                    else: st.warning("Nhập chủ đề!")

    # =================================================================================
    # CÁC MODULE CHATBOT KHÁC
    # =================================================================================
    else:
        st.header(menu)
        
        # Logic Giáo dục
        edu_wrapper = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            col1, col2 = st.columns(2)
            sach = col1.selectbox("📚 Bộ Sách:", ["Cánh Diều", "Chân Trời Sáng Tạo", "Kết Nối Tri Thức", "Sách Cũ"])
            vai_tro = col2.radio("Bạn là:", ["Học sinh/Phụ huynh", "Giáo viên"], horizontal=True)
            if vai_tro == "Học sinh/Phụ huynh":
                edu_wrapper = f" .LƯU Ý: Tôi là HS học sách '{sach}'. Giải thích chi tiết, KHÔNG đưa đáp án ngay."
            else:
                edu_wrapper = f" .Tôi là GV dạy sách '{sach}'. Hỗ trợ soạn giáo án."

        # System Instruction
        consultant_logic = """
        QUY TẮC: 
        1. ƯU TIÊN SỐ 1: Nếu có File đính kèm -> Phân tích File trước.
        2. Nếu hỏi ngắn -> HỎI LẠI bối cảnh.
        3. Giải pháp thực chiến.
        """
        
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu gì?",
            "💰 Kinh Doanh & Marketing": "Chào bạn! Cần lên kế hoạch Marketing hay Chiến lược bán hàng?",
            "🎥 Chuyên Gia Video Google Veo": "Chào Đạo diễn! Bạn cần viết Prompt cho Veo, Sora hay Kling?"
        }
        
        # Chat logic
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            st.session_state.history[menu].append({"role": "assistant", "content": initial_greetings.get(menu, f"Xin chào chuyên gia {menu}.")})

        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

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
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
