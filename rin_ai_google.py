import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Trợ Lý Thực Chiến", page_icon="💎", layout="wide")

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
    st.subheader("🔑 Tài khoản sử dụng") # <-- Tiêu đề chuẩn
    key_option = st.radio("Chế độ:", ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn"], label_visibility="collapsed")
    
    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server")
        except:
            st.error("❌ Chưa cấu hình Key chung")
    else: 
        # HIỂN THỊ HƯỚNG DẪN LẤY KEY
        st.markdown("""
        **👇 Hướng dẫn lấy Key (30s):**
        1. Vào **[Google AI Studio](https://aistudio.google.com/)**
        2. Bấm **Get API key** -> **Create API key**.
        3. Copy và dán vào ô dưới.
        """)
        final_key = st.text_input("Dán API Key của bạn:", type="password") # <-- Sửa label theo yêu cầu
        if final_key: st.success("✅ Đã nhận Key")

    st.divider()

    # 2. MENU CHỨC NĂNG
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio(
        "Lĩnh vực:",
        [
            "🏠 Trang Chủ & Giới Thiệu", 
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "🏢 Giám Đốc Chiến Lược (CEO)",
            "✍️ Marketing & Content",
            "💰 Bán Hàng & Telesales",
            "🛒 Kinh Doanh Online (Shopee/TikTok)",
            "🌐 SEO & Website",
            "💻 Lập Trình (IT)",
            "💸 Tài Chính & Startup",
            "🏠 Bất Động Sản & Xe Sang",
            "🎨 Thiết Kế & Media (Ảnh/Voice)",
            "❤️ Y Tế & Sức Khỏe",
            "🎓 Giáo Dục & Đào Tạo"
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
        ### 🚀 Rin.Ai - Không Lý Thuyết, Chỉ Thực Chiến.
        
        Đây là đội ngũ chuyên gia ảo được lập trình chuyên biệt để **GIẢI QUYẾT VẤN ĐỀ** cho bạn.
        
        **Quy trình làm việc:**
        1.  **Tiếp nhận:** Lắng nghe vấn đề và bối cảnh.
        2.  **Phân tích:** Đóng vai chuyên gia (CEO, Giáo viên, Marketer...) để tư vấn sát sườn.
        3.  **Giải pháp:** Đưa ra kế hoạch hành động, bảng biểu, kịch bản mẫu.
        
        ---
        ### 👨‍🏫 Bảo trợ chuyên môn:
        ## **Mr. Học** (Chuyên gia AI Ứng Dụng)
        #### 📞 Liên hệ: **0901 108 788**
        """)
        st.info("👈 **Mời chọn Chuyên gia bên tay trái để bắt đầu!**")
    with col2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg")

# 2. KIỂM TRA KEY
elif not final_key:
    st.warning("👋 Vui lòng chọn chế độ Key bên tay trái để mở khóa tính năng này.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # --- MODULE MEDIA (TẠO ẢNH & VOICE NÂNG CẤP) ---
    if menu == "🎨 Thiết Kế & Media (Ảnh/Voice)":
        st.header("🎨 Studio Sáng Tạo Đa Phương Tiện")
        st.success("Chào bạn! Bạn muốn vẽ ảnh, viết Prompt hay tạo kịch bản Voice/Hội thoại?")
        
        media_mode = st.radio("👉 Chọn công cụ:", 
                              ["🖼️ Vẽ Ngay Lập Tức", 
                               "📝 Viết Prompt Ảnh",
                               "🎙️ Kịch Bản Voice (1 Người)",
                               "🗣️ Kịch Bản Hội Thoại (2 Người)"], horizontal=True)
        st.divider()

        # MODE 1: VẼ ẢNH
        if media_mode == "🖼️ Vẽ Ngay Lập Tức":
            desc = st.text_area("Mô tả ý tưởng (Tiếng Việt):", height=100, placeholder="VD: Mèo máy Doraemon phong cách Cyberpunk...")
            if st.button("🎨 Vẽ Ngay"):
                if desc:
                    with st.spinner("Đang phác thảo..."):
                        model = genai.GenerativeModel(best_model)
                        trans = model.generate_content(f"Translate to detailed English prompt: {desc}").text
                        final = trans.replace(" ", "%20")
                        st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Rin.Ai generated")
                        st.success("Đã xong! Chuột phải để tải về.")
                else:
                    st.warning("Nhập mô tả đi bạn ơi!")
        
        # MODE 2: PROMPT ẢNH
        elif media_mode == "📝 Viết Prompt Ảnh":
            model = genai.GenerativeModel(best_model)
            prompt_topic = st.text_area("Ý tưởng ảnh của bạn:", placeholder="VD: Logo cafe, Poster quảng cáo...")
            if st.button("📝 Viết Prompt"):
                with st.spinner("Đang tối ưu..."):
                    res = model.generate_content(f"Viết 3 prompt tiếng Anh cho Midjourney v6 về: {prompt_topic}. Thêm thông số --ar 16:9 --v 6.0. Giải thích tiếng Việt.").text
                    st.markdown(res)

        # MODE 3: VOICE 1 NGƯỜI (NÂNG CẤP)
        elif media_mode == "🎙️ Kịch Bản Voice (1 Người)":
            st.info("Dành cho Podcast đơn, Lời bình video, Thuyết minh.")
            col1, col2 = st.columns(2)
            gender = col1.radio("Chọn giọng đọc:", ["Nam 👨", "Nữ 👩"])
            tone = col2.selectbox("Cảm xúc:", ["Trầm ấm/Truyền cảm", "Vui tươi/Hào hứng", "Nghiêm túc/Thời sự", "Buồn/Sâu lắng"])
            
            topic = st.text_area("Nội dung/Chủ đề cần đọc:", placeholder="VD: Giới thiệu sản phẩm mới, Tâm sự đêm khuya...")
            
            if st.button("🎙️ Viết Kịch Bản"):
                if topic:
                    model = genai.GenerativeModel(best_model)
                    prompt = f"""
                    Viết kịch bản lời bình (Voiceover) cho 1 người đọc.
                    - Giọng: {gender}.
                    - Cảm xúc: {tone}.
                    - Chủ đề: {topic}.
                    Yêu cầu: Đánh dấu rõ các chỗ cần [Ngắt nghỉ], [Nhấn mạnh], [Thở dài], [Cười] để người đọc hoặc AI TTS thực hiện đúng cảm xúc.
                    """
                    st.markdown(model.generate_content(prompt).text)
                else:
                    st.warning("Nhập chủ đề nhé!")

        # MODE 4: HỘI THOẠI 2 NGƯỜI (NÂNG CẤP)
        else:
            st.info("Dành cho Podcast đối thoại, Video phỏng vấn, Kịch bản TikTok 2 người.")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Nhân vật A")
                gender_a = st.radio("Giới tính A:", ["Nam 👨", "Nữ 👩"], key="ga")
            with col2:
                st.markdown("### Nhân vật B")
                gender_b = st.radio("Giới tính B:", ["Nam 👨", "Nữ 👩"], key="gb")
            
            topic = st.text_area("Chủ đề cuộc trò chuyện:", placeholder="VD: Tranh luận về AI thay thế con người...")
            
            if st.button("🗣️ Tạo Hội Thoại"):
                if topic:
                    model = genai.GenerativeModel(best_model)
                    prompt = f"""
                    Viết kịch bản hội thoại giữa 2 người: Nhân vật A ({gender_a}) và Nhân vật B ({gender_b}).
                    - Chủ đề: {topic}.
                    - Độ dài: Khoảng 500 từ.
                    - Yêu cầu: Ngôn ngữ tự nhiên, đời thường. Có chỉ dẫn cảm xúc trong ngoặc đơn (Cười lớn), (Ngạc nhiên).
                    """
                    st.markdown(model.generate_content(prompt).text)
                else:
                    st.warning("Nhập chủ đề nhé!")

    # --- CÁC MODULE CHATBOT KHÁC (LOGIC CỐ VẤN) ---
    else:
        st.header(menu)
        
        # 1. LỜI CHÀO CHỦ ĐỘNG
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu thông tin hay giải quyết vấn đề gì ngay bây giờ?",
            "🏢 Giám Đốc Chiến Lược (CEO)": "Chào Sếp! Hôm nay chúng ta bàn về chiến lược, nhân sự hay dòng tiền?",
            "✍️ Marketing & Content": "Hello! Đồng đội Marketing đây. Cần viết content hay lên kế hoạch quảng cáo?",
            "💰 Bán Hàng & Telesales": "Sát thủ Sales đã sẵn sàng! Khách hàng nào đang làm khó bạn?",
            "🛒 Kinh Doanh Online (Shopee/TikTok)": "Chào Shop! Cần tối ưu SEO sản phẩm hay Phân tích đối thủ?",
            "💻 Lập Trình (IT)": "Chào Dev! Cần fix bug hay viết code?",
            "❤️ Y Tế & Sức Khỏe": "Chào bạn! Cần thực đơn giảm cân hay lịch tập gym?",
            "🎓 Giáo Dục & Đào Tạo": "Chào bạn! Cho tôi biết bạn là **Giáo viên, Phụ huynh hay Học sinh** để tôi hỗ trợ tốt nhất nhé?"
        }

        # 2. SYSTEM INSTRUCTION (NÂNG CẤP GIÁO DỤC & CỐ VẤN)
        
        # Logic chung cho các ngành Kinh doanh/CEO...
        consultant_logic = """
        QUY TẮC: 
        1. Nếu thông tin sơ sài -> HỎI LẠI NGAY ĐỂ LẤY BỐI CẢNH.
        2. Nếu đủ thông tin -> ĐƯA GIẢI PHÁP CHI TIẾT (Không nói lý thuyết).
        """
        
        # Logic đặc biệt cho GIÁO DỤC (Theo yêu cầu mới)
        edu_logic = """
        QUY TẮC CỐT LÕI CHO CHUYÊN GIA GIÁO DỤC:
        1. XÁC ĐỊNH ĐỐI TƯỢNG: 
           - Nếu người dùng là HỌC SINH/PHỤ HUYNH: Đóng vai Giáo viên giỏi, tận tâm. GIẢI THÍCH CHI TIẾT, KHÔNG ĐƯA ĐÁP ÁN NGAY. Hướng dẫn từng bước tư duy theo Sách Giáo Khoa Việt Nam. Kiên nhẫn, dễ hiểu.
           - Nếu người dùng là GIÁO VIÊN: Đóng vai Đồng nghiệp chuyên môn cao. Hỗ trợ soạn giáo án, phương pháp dạy học mới (STEM, 5E).
        2. PHƯƠNG PHÁP: Luôn đi từ lý thuyết -> ví dụ -> bài tập vận dụng.
        """

        personas = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": f"Bạn là Trợ lý AI thông minh. {consultant_logic}",
            "🏢 Giám Đốc Chiến Lược (CEO)": f"Bạn là Cố vấn Quản trị cấp cao. {consultant_logic}",
            "✍️ Marketing & Content": f"Bạn là CMO thực chiến. {consultant_logic}",
            "💰 Bán Hàng & Telesales": f"Bạn là Top Sales. {consultant_logic}",
            "🛒 Kinh Doanh Online (Shopee/TikTok)": f"Bạn là Chuyên gia E-commerce. {consultant_logic}",
            "💻 Lập Trình (IT)": "Bạn là Senior Developer. Code chuẩn, giải thích ngắn.",
            "❤️ Y Tế & Sức Khỏe": f"Bạn là Bác sĩ & PT. {consultant_logic}",
            "🎓 Giáo Dục & Đào Tạo": f"{edu_logic}" # <-- Đã áp dụng logic giáo dục mới
        }

        # 3. LỊCH SỬ CHAT
        if "history" not in st.session_state:
            st.session_state.history = {}
        
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            greeting_msg = initial_greetings.get(menu, "Xin chào! Tôi có thể giúp gì cho bạn?")
            st.session_state.history[menu].append({"role": "assistant", "content": greeting_msg})

        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 4. XỬ LÝ CHAT
        # Tự động thêm ngữ cảnh vào prompt nếu là Giáo dục để AI biết cách ứng xử
        user_prompt_wrapper = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            user_prompt_wrapper = " (Hãy xác định tôi là GV hay HS/PH để trả lời phù hợp. Nếu là HS, hãy giảng giải chi tiết, đừng chỉ đưa đáp án)"

        sys_prompt = personas.get(menu, f"Bạn là chuyên gia. {consultant_logic}")
        model = genai.GenerativeModel(best_model, system_instruction=sys_prompt)
        
        if prompt := st.chat_input("Nhập nội dung..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang thực hiện..."):
                    try:
                        # Gửi prompt kèm wrapper (nếu có)
                        final_prompt = prompt + user_prompt_wrapper
                        response = model.generate_content(final_prompt)
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
