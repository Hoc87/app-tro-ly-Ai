import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Hệ Sinh Thái AI", page_icon="💎", layout="wide")

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
    
    # 1. CẤU HÌNH KEY (ĐÃ SỬA THEO YÊU CẦU)
    st.subheader("🔑 Cấu hình tài khoản")
    
    key_option = st.radio(
        "Chọn chế độ:",
        ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn (VIP)"], # Đã sửa tên ngắn gọn
        captions=["Giới hạn tốc độ trải nghiệm.", "Tốc độ cao, bảo mật riêng tư."]
    )
    
    final_key = None
    
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối hệ thống")
        except:
            st.error("❌ Hệ thống chưa cấu hình Key chung")
            
    else: # Chế độ nhập Key cá nhân
        # HIỂN THỊ HƯỚNG DẪN NGAY LẬP TỨC (KHÔNG GIẤU)
        st.info("""
        **👇 Hướng dẫn lấy Key (30 giây):**
        1. Truy cập: **[Google AI Studio](https://aistudio.google.com/)**
        2. Đăng nhập Gmail -> Bấm nút **Get API key**.
        3. Bấm **Create API key** -> Copy mã.
        4. Dán vào ô bên dưới.
        """)
        
        final_key = st.text_input("Dán API Key vào đây:", type="password")
        
        if final_key:
            st.success("✅ Đã nhận Key VIP")

    st.divider()

    # 2. MENU CHỨC NĂNG (ĐÃ THÊM TRANG GIỚI THIỆU)
    st.subheader("📂 Chọn Lĩnh Vực")
    
    menu = st.radio(
        "Danh mục:",
        [
            "🏠 Giới Thiệu & Liên Hệ", # <-- Trang chủ mặc định
            "✨ Trợ Lý Đa Lĩnh Vực (Gemini)",
            "🏢 Trợ Lý Giám Đốc & Chiến Lược",
            "✍️ Marketing - Content - Social",
            "💰 Bán Hàng - Telesales - CSKH",
            "🛒 Kinh Doanh Online / TMĐT",
            "🌐 SEO - Website - Copywriting",
            "🎓 Học Tập - Giáo Dục - Tự Học",
            "💻 Lập Trình - Coding - Automation",
            "💸 Tài Chính - Startup - Kiếm Tiền",
            "🏠 Bất Động Sản & Xe Hơi",
            "🎨 Thiết Kế - Ảnh - Video (Media)",
            "❤️ Y Tế - Sức Khỏe - Gym"
        ]
    )

# --- NỘI DUNG CHÍNH ---

# ==============================================================================
# TRANG GIỚI THIỆU (LANDING PAGE)
# ==============================================================================
if menu == "🏠 Giới Thiệu & Liên Hệ":
    st.title("💎 Chào mừng đến với Hệ Sinh Thái Rin.Ai")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Rin.Ai là gì?
        **Rin.Ai** là một "Siêu Ứng Dụng" (Super App) được xây dựng dựa trên sức mạnh của hệ sinh thái **Google AI (Gemini 1.5/2.0)**. 
        
        Khác với các công cụ Chatbot thông thường, Rin.Ai được lập trình chuyên biệt hóa cho từng ngành nghề. Khi bạn chọn một lĩnh vực, AI sẽ tự động "biến hình" thành một chuyên gia thực chiến với 10 năm kinh nghiệm để tư vấn cho bạn.
        
        ### 👨‍🏫 Nhà Phát Triển & Bảo Trợ
        Ứng dụng này được xây dựng và phát triển trực tiếp bởi:
        
        ## **Chuyên gia: Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        
        > *Chuyên gia đào tạo và hướng dẫn ứng dụng AI thực chiến cho Doanh nghiệp và Cá nhân. Giúp bạn tối ưu hóa quy trình làm việc và bứt phá doanh số bằng công nghệ.*
        """)
        
        st.info("👈 **Hãy chọn một lĩnh vực bên menu trái để bắt đầu làm việc ngay!**")

    with col2:
        # Bạn có thể thay link ảnh này bằng ảnh chân dung của bạn nếu muốn
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg", caption="Rin.Ai Ecosystem")

# ==============================================================================
# LOGIC KIỂM TRA KEY (CHO CÁC TRANG KHÁC)
# ==============================================================================
elif not final_key:
    st.warning("👋 Vui lòng chọn chế độ Key bên tay trái để mở khóa tính năng này.")
    st.stop()

else:
    # Cấu hình AI
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # --- MODULE MEDIA (TẠO ẢNH) ---
    if menu == "🎨 Thiết Kế - Ảnh - Video (Media)":
        st.header("🎨 Studio Sáng Tạo Đa Phương Tiện")
        st.markdown("Tại đây bạn có thể tạo ảnh trực tiếp hoặc lên kịch bản cho Video/Voice.")
        
        media_tab = st.tabs(["🖼️ Tạo Ảnh (Imagen)", "🎬 Kịch Bản Video", "🎙️ Kịch Bản Voice"])
        
        with media_tab[0]:
            desc = st.text_area("Mô tả hình ảnh bạn muốn vẽ:", height=100)
            if st.button("🎨 Vẽ Ngay"):
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    trans = model.generate_content(f"Translate to English for Image Gen: {desc}").text
                    final = trans.replace(" ", "%20")
                    st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Rin.Ai generated")
        
        with media_tab[1]:
            st.info("AI đóng vai Đạo diễn viết kịch bản chi tiết.")
            video_topic = st.text_input("Chủ đề video:")
            if st.button("Viết Kịch Bản"):
                model = genai.GenerativeModel(best_model)
                st.write(model.generate_content(f"Viết kịch bản video ngắn 60s viral về chủ đề: {video_topic}.").text)

        with media_tab[2]:
            voice_topic = st.text_input("Nội dung cần thu âm:")
            if st.button("Tạo lời bình"):
                model = genai.GenerativeModel(best_model)
                st.write(model.generate_content(f"Viết lời bình cảm xúc cho nội dung: {voice_topic}.").text)

    # --- CÁC MODULE CHATBOT KHÁC ---
    else:
        st.header(menu)
        
        # SYSTEM INSTRUCTION (Tư duy cố vấn)
        base_logic = """
        QUY TRÌNH TƯ VẤN:
        1. Nếu người dùng hỏi chung chung -> HỎI LẠI 3-5 câu để lấy bối cảnh (Sản phẩm, Khách hàng, Ngân sách...).
        2. Nếu đã có đủ thông tin -> Đưa giải pháp chi tiết, bảng biểu, quy trình thực chiến.
        """
        
        personas = {
            "✨ Trợ Lý Đa Lĩnh Vực (Gemini)": "Bạn là Trợ lý AI hữu ích, trả lời nhanh, ngắn gọn, đi thẳng vào vấn đề. Không cần hỏi lại.",
            "🏢 Trợ Lý Giám Đốc & Chiến Lược": f"Bạn là Cố vấn Chiến lược cấp cao. {base_logic}",
            "✍️ Marketing - Content - Social": f"Bạn là Giám đốc Marketing (CMO). {base_logic}",
            "💰 Bán Hàng - Telesales - CSKH": f"Bạn là Chuyên gia Sales. {base_logic}",
            "🛒 Kinh Doanh Online / TMĐT": f"Bạn là Top Seller Shopee/TikTok. {base_logic}",
            "🌐 SEO - Website - Copywriting": f"Bạn là Chuyên gia SEO. {base_logic}",
            "💻 Lập Trình - Coding - Automation": "Bạn là Senior Developer. Chỉ đưa ra Code block và giải thích ngắn gọn.",
            "💸 Tài Chính - Startup - Kiếm Tiền": f"Bạn là Chuyên gia Tài chính. {base_logic}",
            "🏠 Bất Động Sản & Xe Hơi": f"Bạn là Chuyên gia Môi giới BĐS. {base_logic}",
            "❤️ Y Tế - Sức Khỏe - Gym": f"Bạn là Bác sĩ & PT Gym. {base_logic}",
            "🎓 Học Tập - Giáo Dục - Tự Học": "Bạn là Giáo sư Đại học. Giải thích dễ hiểu, sư phạm."
        }

        # Lịch sử chat
        if "history" not in st.session_state:
            st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []

        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Xử lý Chat
        system_prompt = personas.get(menu, "Bạn là trợ lý AI.")
        model = genai.GenerativeModel(best_model, system_instruction=system_prompt)
        
        if prompt := st.chat_input("Nhập yêu cầu của bạn..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang phân tích..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
