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
    """Chuyển đổi file upload thành dạng mà Gemini hiểu được"""
    if uploaded_file is None:
        return None
    
    # Xử lý ảnh
    if uploaded_file.type.startswith('image'):
        return Image.open(uploaded_file)
    
    # Xử lý PDF
    elif uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except:
            return "Lỗi đọc PDF"
    
    # Xử lý Excel/CSV
    elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type or "csv" in uploaded_file.type:
        try:
            if "csv" in uploaded_file.type:
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            return df.to_string()
        except:
            return "Lỗi đọc file Excel/CSV"
            
    # Xử lý Text
    else:
        return uploaded_file.getvalue().decode("utf-8")

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
    
    # 1. CẤU HÌNH TÀI KHOẢN (SHOW HƯỚNG DẪN LUÔN)
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
    
    # 2. UPLOAD FILE (CHO TẤT CẢ TRỢ LÝ)
    st.subheader("📂 Gửi tài liệu cho AI")
    uploaded_file = st.file_uploader("Tải lên Ảnh, PDF, Excel, Word...", type=['png', 'jpg', 'jpeg', 'pdf', 'txt', 'csv', 'xlsx'])
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        st.success(f"Đã nhận file: {uploaded_file.name}")

    st.divider()

    # 3. MENU CHỨC NĂNG
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio(
        "Lĩnh vực:",
        [
            "🏠 Trang Chủ & Giới Thiệu", 
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "📰 Đọc Báo & Tóm Tắt Sách",
            "🎨 Thiết Kế & Media (Ảnh/Video)",
            "🎥 Chuyên Gia Video Google Veo", # <-- MỚI
            "🎓 Giáo Dục & Đào Tạo", # <-- NÂNG CẤP
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
        
        Chào mừng bạn đến với phiên bản Rin.Ai PRO. Chúng tôi tích hợp sức mạnh của Google để xử lý mọi định dạng dữ liệu:
        
        * **👁️ Thị giác:** Phân tích hình ảnh, biểu đồ.
        * **🧠 Trí tuệ:** Đọc hiểu PDF, Excel, Báo cáo.
        * **🎨 Sáng tạo:** Vẽ tranh, viết Prompt Video Veo.
        * **🗣️ Giọng nói:** Đọc văn bản thành tiếng (Text-to-Speech).
        
        ---
        ### 👨‍🏫 Bảo trợ chuyên môn:
        ## **Mr. Học** (Chuyên gia AI Ứng Dụng)
        #### 📞 Liên hệ: **0901 108 788**
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

    # --- MODULE RIÊNG: GOOGLE VEO (VIDEO) ---
    if menu == "🎥 Chuyên Gia Video Google Veo":
        st.header("🎥 Chuyên Gia Tạo Video (Google Veo)")
        st.info("AI sẽ viết Prompt chuyên sâu (Góc máy, ánh sáng, chuyển động) để bạn dán vào Google Veo (VideoFX).")
        
        veo_mode = st.selectbox("Phong cách video:", ["Điện ảnh (Cinematic)", "Hoạt hình 3D (Pixar style)", "Drone quay trên cao", "Quảng cáo sản phẩm"])
        veo_idea = st.text_area("Mô tả ý tưởng video của bạn:", height=100)
        
        if st.button("🎬 Viết Prompt Veo Chuẩn"):
            if veo_idea:
                model = genai.GenerativeModel(best_model)
                prompt = f"""
                Đóng vai chuyên gia Google Veo. Viết prompt tiếng Anh chi tiết tạo video chủ đề: "{veo_idea}".
                Phong cách: {veo_mode}.
                Yêu cầu kỹ thuật:
                - Mô tả chi tiết chuyển động (Camera movement).
                - Ánh sáng (Lighting), Màu sắc (Color grading).
                - Âm thanh/Lời thoại (nếu có).
                - Độ phân giải: 4K, 60fps.
                """
                with st.spinner("Đang xử lý kỹ thuật..."):
                    res = model.generate_content(prompt).text
                    st.code(res, language="text")
                    st.markdown("👉 **Truy cập để tạo video:** [Google VideoFX / Veo](https://labs.google/videofx)")
            else:
                st.warning("Nhập ý tưởng đi bạn!")

    # --- MODULE MEDIA (TẠO ẢNH & VOICE) ---
    elif menu == "🎨 Thiết Kế & Media (Ảnh/Voice)":
        st.header("🎨 Studio Đa Phương Tiện")
        media_mode = st.radio("Công cụ:", ["🖼️ Vẽ Ảnh Ngay", "📝 Prompt Ảnh", "🎙️ Kịch Bản Voice"], horizontal=True)
        
        if media_mode == "🖼️ Vẽ Ảnh Ngay":
            desc = st.text_area("Mô tả ảnh:", height=100)
            if st.button("🎨 Vẽ Luôn"):
                if desc:
                    with st.spinner("Đang vẽ..."):
                        model = genai.GenerativeModel(best_model)
                        trans = model.generate_content(f"Translate to detailed English prompt: {desc}").text
                        final = trans.replace(" ", "%20")
                        st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Rin.Ai Generated")

        elif media_mode == "📝 Prompt Ảnh":
            st.info("Tạo prompt cho Midjourney/Dall-E")
            idea = st.text_area("Ý tưởng:")
            if st.button("Tạo Prompt"):
                model = genai.GenerativeModel(best_model)
                st.write(model.generate_content(f"Viết 3 prompt Midjourney v6 cho: {idea}").text)
                
        else: # Voice
            st.info("Tạo kịch bản để thu âm.")
            voice_topic = st.text_area("Nội dung:")
            if st.button("Viết kịch bản"):
                 model = genai.GenerativeModel(best_model)
                 st.write(model.generate_content(f"Viết kịch bản thu âm diễn cảm cho: {voice_topic}").text)

    # --- CÁC MODULE CHATBOT KHÁC ---
    else:
        st.header(menu)
        
        # LOGIC GIÁO DỤC ĐẶC BIỆT (SÁCH GIÁO KHOA)
        edu_wrapper = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            sach = st.selectbox("📚 Chọn Bộ Sách Giáo Khoa:", ["Cánh Diều", "Chân Trời Sáng Tạo", "Kết Nối Tri Thức", "Sách Cũ (2006)", "Chương trình Quốc tế"])
            vai_tro = st.radio("Bạn là:", ["Học sinh/Phụ huynh", "Giáo viên"], horizontal=True)
            
            if vai_tro == "Học sinh/Phụ huynh":
                edu_wrapper = f" .LƯU Ý QUAN TRỌNG: Tôi là Học sinh đang học bộ sách '{sach}'. Hãy đóng vai Giáo viên giỏi, giải thích chi tiết từng bước, KHÔNG đưa đáp án ngay. Giúp tôi hiểu bản chất."
            else:
                edu_wrapper = f" .Tôi là Giáo viên dạy bộ sách '{sach}'. Hãy hỗ trợ soạn giáo án và phương pháp giảng dạy phù hợp."

        # SYSTEM INSTRUCTION & GREETINGS
        consultant_logic = """
        QUY TẮC: 
        1. Nếu có File đính kèm -> Ưu tiên phân tích File.
        2. Nếu người dùng hỏi ngắn -> HỎI LẠI để lấy bối cảnh.
        3. Đưa giải pháp thực chiến, chi tiết.
        """
        
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu gì? (Có thể upload file để tôi đọc)",
            "🎓 Giáo Dục & Đào Tạo": "Chào bạn! Hãy chọn Bộ sách giáo khoa ở trên để tôi hỗ trợ sát sườn nhất nhé.",
            # ... (Các câu chào khác giữ nguyên như bản trước)
        }
        
        # Lấy lời chào mặc định nếu chưa có trong dict
        greeting = initial_greetings.get(menu, f"Xin chào! Tôi là chuyên gia về {menu}. Bạn cần hỗ trợ gì?")

        # Lịch sử chat
        if "history" not in st.session_state:
            st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            st.session_state.history[menu].append({"role": "assistant", "content": greeting})

        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # XỬ LÝ CHAT
        model = genai.GenerativeModel(best_model, system_instruction=f"Bạn là chuyên gia {menu}. {consultant_logic}")
        
        if prompt := st.chat_input("Nhập câu hỏi..."):
            # User
            with st.chat_message("user"):
                st.markdown(prompt)
                # Nếu có file, hiển thị thông báo đã gửi file
                if file_content:
                    st.caption(f"📎 Đã đính kèm file: {uploaded_file.name}")
            
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            # Assistant
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang phân tích..."):
                    try:
                        # Ghép nội dung: Prompt + File (nếu có) + Edu Wrapper (nếu có)
                        final_input = [prompt + edu_wrapper]
                        if file_content:
                            if isinstance(file_content, str):
                                final_input.append(f"\n\nNỘI DUNG FILE ĐÍNH KÈM:\n{file_content}")
                            else:
                                final_input.append(file_content) # Ảnh

                        response = model.generate_content(final_input)
                        
                        # Hiển thị Text
                        st.markdown(response.text)
                        
                        # NÚT NGHE GIỌNG ĐỌC (TTS)
                        try:
                            tts = gTTS(text=response.text[:500], lang='vi') # Đọc 500 ký tự đầu cho nhanh
                            audio_bytes = io.BytesIO()
                            tts.write_to_fp(audio_bytes)
                            st.audio(audio_bytes, format='audio/mp3')
                        except:
                            pass # Bỏ qua nếu lỗi âm thanh

                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                        
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
