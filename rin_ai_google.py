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
    # Ảnh
    if uploaded_file.type.startswith('image'):
        return Image.open(uploaded_file)
    # PDF
    elif uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except: return "Lỗi đọc PDF"
    # Excel/CSV
    elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type or "csv" in uploaded_file.type:
        try:
            if "csv" in uploaded_file.type: df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            return df.to_string()
        except: return "Lỗi đọc file Excel/CSV"
    # Text
    else: return uploaded_file.getvalue().decode("utf-8")

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
    
    # 1. CẤU HÌNH TÀI KHOẢN (ĐÃ SỬA: HIỆN HƯỚNG DẪN RÕ RÀNG)
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
        # SHOW LUÔN HƯỚNG DẪN NGAY TẠI ĐÂY (KHÔNG ẨN)
        st.info("""
        **👇 Hướng dẫn lấy Key (30s):**
        1. Vào **[Google AI Studio](https://aistudio.google.com/)**
        2. Bấm **Get API key** -> **Create API key**.
        3. Copy mã và dán vào ô dưới.
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
            "🎨 Thiết Kế & Media (Ảnh/Video)",
            "🎥 Chuyên Gia Video Google Veo",
            "🎓 Giáo Dục & Đào Tạo",
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

# 1. TRANG GIỚI THIỆU (ĐÃ THÊM CÂU CTA MR. HỌC)
if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 🚀 Rin.Ai - Super App Đa Phương Tiện
        Chào mừng bạn đến với phiên bản Rin.Ai PRO. Chúng tôi tích hợp sức mạnh của Google để xử lý mọi định dạng dữ liệu: hình ảnh, tài liệu, giọng nói.
        
        ---
        ### 👨‍🏫 Đào tạo & Liên hệ:
        ## **Chuyên gia: Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        
        > **📢 ĐẶC BIỆT: Nếu bạn có nhu cầu học AI bài bản để áp dụng vào công việc thực tế hoặc đời sống, hãy liên hệ ngay Mr. Học để được hướng dẫn trực tiếp.**
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

    # --- MODULE RIÊNG: GOOGLE VEO ---
    if menu == "🎥 Chuyên Gia Video Google Veo":
        st.header("🎥 Chuyên Gia Tạo Video (Google Veo)")
        st.info("AI viết Prompt chuyên sâu cho Google Veo/Sora.")
        veo_idea = st.text_area("Mô tả ý tưởng video:", height=100)
        if st.button("🎬 Viết Prompt"):
             model = genai.GenerativeModel(best_model)
             st.write(model.generate_content(f"Viết prompt video AI chi tiết cho: {veo_idea}").text)

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
                        st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true")
        # ... (Các phần khác của Media giữ nguyên để tiết kiệm chỗ, đã có trong logic cũ)

    # --- CÁC MODULE CHATBOT (CÓ NÚT UPLOAD FILE NGAY TRONG KHUNG CHAT) ---
    else:
        st.header(menu)
        
        # KHUNG UPLOAD FILE (NẰM NGAY TRÊN CÙNG MÀN HÌNH CHÍNH)
        with st.expander("📎 Đính kèm tài liệu cho Trợ lý (Ảnh/PDF/Excel)", expanded=False):
            uploaded_file = st.file_uploader("Chọn file:", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx'])
            file_content = None
            if uploaded_file:
                file_content = process_uploaded_file(uploaded_file)
                st.success(f"Đã tải lên: {uploaded_file.name}")
        
        # LOGIC & PERSONAS
        edu_wrapper = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            col1, col2 = st.columns(2)
            sach = col1.selectbox("Bộ sách:", ["Cánh Diều", "Chân Trời Sáng Tạo", "Kết Nối Tri Thức", "Sách Cũ"])
            vai_tro = col2.radio("Vai trò:", ["Học sinh/Phụ huynh", "Giáo viên"], horizontal=True)
            if vai_tro == "Học sinh/Phụ huynh":
                edu_wrapper = f" .LƯU Ý: Tôi là HS học sách '{sach}'. Hãy giảng giải chi tiết, KHÔNG đưa đáp án ngay."
            else:
                edu_wrapper = f" .Tôi là GV dạy sách '{sach}'. Hỗ trợ soạn giáo án."

        # Greeting Logic
        consultant_logic = "Hỏi lại bối cảnh nếu thiếu thông tin. Đưa giải pháp thực chiến."
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu gì?",
            "💰 Kinh Doanh & Marketing": "Chào bạn! Cần lên kế hoạch Marketing hay Chiến lược bán hàng?",
             # ... (Giữ nguyên các greeting khác)
        }
        greeting = initial_greetings.get(menu, f"Xin chào! Tôi là chuyên gia về {menu}.")

        # History
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            st.session_state.history[menu].append({"role": "assistant", "content": greeting})

        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input & Processing
        sys_prompt = f"Bạn là chuyên gia {menu}. {consultant_logic}"
        model = genai.GenerativeModel(best_model, system_instruction=sys_prompt)

       # ... (Đoạn code hiển thị lịch sử chat ở trên)

    # THÊM ĐOẠN NÀY ĐỂ NHẮC NGƯỜI DÙNG
    if not file_content:
        st.caption("💡 Mẹo: Bạn có thể tải ảnh/tài liệu lên ở cột bên trái 👈 để AI phân tích.")
    else:
        st.info(f"📎 Đang đính kèm file: {uploaded_file.name}. Hãy đặt câu hỏi bên dưới 👇")

    # Khung nhập liệu (Giữ nguyên)
    if prompt := st.chat_input("Nhập yêu cầu..."):
        # ... 
        if prompt := st.chat_input("Nhập câu hỏi..."):
            with st.chat_message("user"):
                st.markdown(prompt)
                if file_content: st.caption(f"📎 [Có đính kèm file]")
            
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
                        
                        # PLAYER VOICE
                        try:
                            tts = gTTS(text=response.text[:300], lang='vi')
                            audio_bytes = io.BytesIO()
                            tts.write_to_fp(audio_bytes)
                            st.audio(audio_bytes, format='audio/mp3')
                        except: pass

                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
