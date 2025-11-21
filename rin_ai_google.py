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
    
    # 1. CẤU HÌNH KEY
    st.subheader("🔑 Cấu hình tài khoản")
    
    key_option = st.radio(
        "Chọn chế độ:",
        ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn (VIP)"],
        captions=["Dành cho trải nghiệm.", "Tốc độ cao, bảo mật."]
    )
    
    final_key = None
    
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối hệ thống")
        except:
            st.error("❌ Hệ thống chưa cấu hình Key chung")
            
    else: 
        st.info("""
        **👇 Hướng dẫn lấy Key (30 giây):**
        1. Truy cập: **[Google AI Studio](https://aistudio.google.com/)**
        2. Đăng nhập Gmail -> Bấm nút **Get API key**.
        3. Bấm **Create API key** -> Copy mã.
        4. Dán vào ô bên dưới.
        """)
        final_key = st.text_input("Dán API Key vào đây:", type="password")
        if final_key: st.success("✅ Đã nhận Key VIP")

    st.divider()

    # 2. MENU CHỨC NĂNG
    st.subheader("📂 Chọn Lĩnh Vực")
    
    menu = st.radio(
        "Danh mục:",
        [
            "🏠 Giới Thiệu & Liên Hệ", 
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

# 1. TRANG GIỚI THIỆU
if menu == "🏠 Giới Thiệu & Liên Hệ":
    st.title("💎 Chào mừng đến với Hệ Sinh Thái Rin.Ai")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 🚀 Rin.Ai là gì?
        **Rin.Ai** là "Siêu Ứng Dụng" AI được chuyên biệt hóa cho từng ngành nghề.
        
        ### 👨‍🏫 Nhà Phát Triển & Bảo Trợ
        ## **Chuyên gia: Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        > *Chuyên gia đào tạo AI thực chiến cho Doanh nghiệp và Cá nhân.*
        """)
        st.info("👈 **Hãy chọn một lĩnh vực bên menu trái để bắt đầu làm việc ngay!**")
    with col2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg", caption="Rin.Ai Ecosystem")

# 2. KIỂM TRA KEY (CÁC TRANG KHÁC)
elif not final_key:
    st.warning("👋 Vui lòng chọn chế độ Key bên tay trái để mở khóa tính năng này.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # --- MODULE MEDIA (GIAO DIỆN RIÊNG) ---
    if menu == "🎨 Thiết Kế - Ảnh - Video (Media)":
        st.header("🎨 Studio Sáng Tạo Đa Phương Tiện")
        st.success("👋 Xin chào Designer! Bạn muốn vẽ ảnh, làm video hay thu âm hôm nay?")
        
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
            video_topic = st.text_input("Chủ đề video:")
            if st.button("Viết Kịch Bản"):
                model = genai.GenerativeModel(best_model)
                st.write(model.generate_content(f"Viết kịch bản video ngắn 60s viral về: {video_topic}.").text)
        with media_tab[2]:
            voice_topic = st.text_input("Nội dung cần thu âm:")
            if st.button("Tạo lời bình"):
                model = genai.GenerativeModel(best_model)
                st.write(model.generate_content(f"Viết lời bình cảm xúc cho: {voice_topic}.").text)

    # --- CÁC MODULE CHATBOT (CÓ LỜI CHÀO TỰ ĐỘNG) ---
    else:
        st.header(menu)
        
        # --- 1. ĐỊNH NGHĨA LỜI CHÀO TỰ ĐỘNG (GREETINGS) ---
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Gemini)": "Xin chào! Tôi là Trợ lý AI đa năng. Bạn đang gặp khó khăn gì cần tôi giải quyết ngay không?",
            
            "🏢 Trợ Lý Giám Đốc & Chiến Lược": "Chào Sếp! Bạn là Giám đốc phải không? Hôm nay chúng ta sẽ bàn về chiến lược, nhân sự hay dòng tiền của công ty?",
            
            "✍️ Marketing - Content - Social": "Chào bạn! Tôi là chuyên gia Marketing thực chiến đây. Bạn đang bí ý tưởng content hay cần lên kế hoạch quảng cáo?",
            
            "💰 Bán Hàng - Telesales - CSKH": "Alo! Sát thủ Sales đã sẵn sàng. Khách hàng nào đang từ chối bạn? Hay bạn cần kịch bản chốt đơn 'bách phát bách trúng'?",
            
            "🛒 Kinh Doanh Online / TMĐT": "Chào Chủ Shop! Tình hình đơn hàng Shopee/TikTok hôm nay thế nào? Cần tôi tối ưu SEO hay phân tích đối thủ không?",
            
            "🌐 SEO - Website - Copywriting": "Chào đồng nghiệp! Website của bạn đang ở trang mấy Google rồi? Cần tôi viết bài chuẩn SEO hay Audit lại web không?",
            
            "💻 Lập Trình - Coding - Automation": "Hello Dev! Đang bug chỗ nào à? Hay cần tôi viết script tự động hóa gì cho Google Sheet?",
            
            "💸 Tài Chính - Startup - Kiếm Tiền": "Chào Founder! Vốn liếng thế nào rồi? Cần tôi lập kế hoạch kinh doanh (Business Plan) hay dự báo dòng tiền không?",
            
            "🏠 Bất Động Sản & Xe Hơi": "Chào Sale triệu đô! Hôm nay bán đất nền, chung cư hay xe sang? Cần viết tin đăng 'thôi miên' khách hàng không?",
            
            "❤️ Y Tế - Sức Khỏe - Gym": "Chào bạn! Sức khỏe là vàng. Bạn cần thực đơn Eat Clean giảm cân, lịch tập Gym hay tư vấn sức khỏe sơ bộ?",
            
            "🎓 Học Tập - Giáo Dục - Tự Học": "Chào Thầy/Cô và các bạn! Soạn giáo án, làm đề thi hay tóm tắt sách? Tôi đã sẵn sàng hỗ trợ."
        }

        # --- 2. ĐỊNH NGHĨA SYSTEM INSTRUCTION (Tư duy cố vấn) ---
        base_logic = """
        QUY TRÌNH TƯ VẤN:
        1. Nếu người dùng hỏi chung chung -> HỎI LẠI 3-5 câu để lấy bối cảnh (Sản phẩm, Khách hàng, Ngân sách...).
        2. Nếu đã có đủ thông tin -> Đưa giải pháp chi tiết, bảng biểu, quy trình thực chiến.
        """
        
        personas = {
            "✨ Trợ Lý Đa Lĩnh Vực (Gemini)": "Bạn là Trợ lý AI hữu ích, trả lời nhanh, ngắn gọn.",
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

        # --- 3. KHỞI TẠO LỊCH SỬ & CHÈN LỜI CHÀO ---
        if "history" not in st.session_state:
            st.session_state.history = {}
        
        # Nếu vào mục mới chưa có lịch sử -> Tự động thêm lời chào vào
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            if menu in initial_greetings:
                st.session_state.history[menu].append({
                    "role": "assistant", 
                    "content": initial_greetings[menu]
                })

        # Hiển thị lịch sử
        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # --- 4. XỬ LÝ CHAT ---
        system_prompt = personas.get(menu, "Bạn là trợ lý AI.")
        model = genai.GenerativeModel(best_model, system_instruction=system_prompt)
        
        if prompt := st.chat_input("Nhập câu trả lời hoặc yêu cầu của bạn..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang soạn tin..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
