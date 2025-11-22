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
    
    # 1. CẤU HÌNH KEY
    st.subheader("🔑 Cấu hình tài khoản")
    key_option = st.radio("Chế độ:", ["🚀 Dùng Miễn Phí", "💎 Nhập Key VIP"], label_visibility="collapsed")
    
    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server")
        except:
            st.error("❌ Chưa cấu hình Key chung")
    else: 
        st.info("👉 [Bấm đây lấy Key Google AI (Miễn phí)](https://aistudio.google.com/)")
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
            "🏢 Giám Đốc Chiến Lược (CEO)",
            "✍️ Marketing & Content",
            "💰 Bán Hàng & Telesales",
            "🛒 Kinh Doanh Online (Shopee/TikTok)",
            "🌐 SEO & Website",
            "💻 Lập Trình (IT)",
            "💸 Tài Chính & Startup",
            "🏠 Bất Động Sản & Xe Sang",
            "🎨 Thiết Kế & Media (Ảnh/Video)",
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
        
        Đây không phải là Chatbot hỏi đáp thông thường. Đây là đội ngũ chuyên gia ảo được lập trình để **GIẢI QUYẾT VẤN ĐỀ** cho bạn.
        
        **Quy trình làm việc:**
        1.  **Tiếp nhận:** Bạn nêu vấn đề (ngắn gọn cũng được).
        2.  **Phân tích:** AI tự động xác định bối cảnh.
        3.  **Giải pháp:** Đưa ra kế hoạch hành động, bảng biểu, kịch bản mẫu ngay lập tức.
        
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

    # --- MODULE MEDIA (TẠO ẢNH) - ĐÃ NÂNG CẤP TƯ VẤN ---
    if menu == "🎨 Thiết Kế & Media (Ảnh/Video)":
        st.header("🎨 Giám Đốc Nghệ Thuật (Art Director)")
        
        # AI đóng vai tư vấn trước
        st.markdown("""
        **Chào bạn! Tôi là chuyên gia hình ảnh.**
        Bạn muốn tôi **Vẽ ngay tại đây** (nhanh, miễn phí) hay **Viết Prompt chuyên nghiệp** để bạn mang sang Midjourney/Canva dùng?
        """)
        
        media_mode = st.radio("👉 Lựa chọn của bạn:", ["🖼️ Vẽ Ngay Lập Tức (Tại đây)", "📝 Viết Prompt (Mang đi nơi khác)"], horizontal=True)
        st.divider()

        if media_mode == "🖼️ Vẽ Ngay Lập Tức (Tại đây)":
            desc = st.text_area("Mô tả ý tưởng của bạn (Tiếng Việt):", height=100, placeholder="VD: Một con mèo máy Doraemon ngầu, phong cách Cyberpunk...")
            if st.button("🎨 Tiến hành Vẽ"):
                if desc:
                    with st.spinner("Đang phác thảo..."):
                        model = genai.GenerativeModel(best_model)
                        trans = model.generate_content(f"Translate this to detailed English prompt for image generation: {desc}").text
                        final = trans.replace(" ", "%20")
                        st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Tác phẩm do Rin.Ai thực hiện")
                        st.success("Đã xong! Chuột phải để tải về.")
                else:
                    st.warning("Vui lòng nhập mô tả!")
                    
        else: # Viết Prompt
            model = genai.GenerativeModel(best_model)
            prompt_topic = st.text_area("Bạn muốn tạo ảnh gì? (Midjourney/Dall-E)", placeholder="VD: Logo quán cafe, Poster quảng cáo giày...")
            if st.button("📝 Viết Prompt Chuyên Nghiệp"):
                with st.spinner("Đang tối ưu Prompt..."):
                    res = model.generate_content(f"""
                    Bạn là Chuyên gia Prompt Engineering.
                    Nhiệm vụ: Viết 3 lựa chọn Prompt tiếng Anh tốt nhất cho Midjourney v6 dựa trên ý tưởng: "{prompt_topic}".
                    Yêu cầu: Thêm các thông số kỹ thuật (--ar 16:9, --v 6.0, --style raw).
                    Giải thích ngắn gọn tiếng Việt cho từng lựa chọn.
                    """).text
                    st.markdown(res)

    # --- CÁC MODULE CHATBOT (LOGIC MỚI: HỎI ÍT - LÀM NHIỀU) ---
    else:
        st.header(menu)
        
        # --- 1. LỜI CHÀO CHỦ ĐỘNG (GREETINGS) ---
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu thông tin hay giải quyết vấn đề gì ngay bây giờ?",
            "🏢 Giám Đốc Chiến Lược (CEO)": "Chào Sếp! Tôi đã sẵn sàng. Hôm nay Sếp cần xử lý vấn đề gì: Nhân sự, Dòng tiền hay Chiến lược phát triển?",
            "✍️ Marketing & Content": "Hello! Đồng đội Marketing đây. Bạn cần viết bài Facebook, Kịch bản TikTok hay Lên kế hoạch quảng cáo?",
            "💰 Bán Hàng & Telesales": "Sẵn sàng chiến đấu! Bạn đang gặp khó khăn gì: Khách chê đắt, Cần kịch bản gọi điện hay Xử lý từ chối?",
            "🛒 Kinh Doanh Online (Shopee/TikTok)": "Chào Shop! Tình hình đơn hàng thế nào? Cần tôi tối ưu SEO sản phẩm hay Phân tích đối thủ?",
            "💻 Lập Trình (IT)": "Chào Dev! Cần fix bug, viết code Python hay tạo Script tự động hóa?",
            "❤️ Y Tế & Sức Khỏe": "Chào bạn! Cần thực đơn giảm cân, Lịch tập gym hay Tư vấn sức khỏe?",
            "🎓 Giáo Dục & Đào Tạo": "Kính chào Thầy/Cô! Cần soạn giáo án, đề thi hay ý tưởng bài giảng mới?"
        }

        # --- 2. SYSTEM INSTRUCTION MỚI (QUYẾT ĐOÁN HƠN) ---
        # Logic: NẾU người dùng đã cung cấp thông tin -> TRẢ LỜI NGAY. KHÔNG HỎI LẠI.
        
        core_logic = """
        QUY TẮC ỨNG XỬ QUAN TRỌNG:
        1. PHÂN TÍCH INPUT: Nếu người dùng đã cung cấp đủ bối cảnh (Sản phẩm, Vấn đề, Mục tiêu) -> HÃY ĐƯA RA GIẢI PHÁP NGAY LẬP TỨC.
        2. CẤM HỎI LẠI KHI KHÔNG CẦN THIẾT: Tuyệt đối không hỏi kiểu "Bạn có muốn tôi làm không?", "Ngân sách bao nhiêu" nếu vấn đề có thể giải quyết sơ bộ ngay.
        3. PHONG CÁCH TRẢ LỜI: Đi thẳng vào vấn đề. Sử dụng gạch đầu dòng, bảng biểu, quy trình bước 1-2-3.
        4. TONE GIỌNG: Chuyên gia thực chiến, tự tin, không lý thuyết suông.
        """
        
        personas = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": f"Bạn là Trợ lý AI thông minh. {core_logic}",
            
            "🏢 Giám Đốc Chiến Lược (CEO)": f"""Bạn là Cố vấn Quản trị cấp cao. {core_logic}
            Khi Sếp hỏi về vấn đề công ty, hãy đưa ra mô hình phân tích (SWOT, 5W1H) và lộ trình hành động cụ thể.""",
            
            "✍️ Marketing & Content": f"""Bạn là Copywriter & CMO 10 năm kinh nghiệm. {core_logic}
            Nhiệm vụ: Viết content phải có Tiêu đề giật tít (Hook), Thân bài đánh vào nỗi đau, Kết bài kêu gọi hành động (CTA).""",
            
            "💰 Bán Hàng & Telesales": f"""Bạn là Top Sales. {core_logic}
            Nếu người dùng đưa tình huống khách từ chối, hãy viết ngay 3 mẫu câu đối đáp cụ thể để họ copy nói lại với khách.""",
            
            "🛒 Kinh Doanh Online (Shopee/TikTok)": f"Bạn là Chuyên gia E-commerce. {core_logic} Tập trung vào SEO từ khóa và Tối ưu chuyển đổi.",
            
            "💻 Lập Trình (IT)": "Bạn là Senior Developer. Chỉ đưa ra Code block chuẩn và giải thích cực ngắn gọn.",
            
            "❤️ Y Tế & Sức Khỏe": f"Bạn là Bác sĩ dinh dưỡng & PT. {core_logic} Đưa ra thực đơn/lịch tập cụ thể theo ngày.",
            
            "🎓 Giáo Dục & Đào Tạo": f"Bạn là Chuyên gia Sư phạm. {core_logic} Soạn giáo án phải chia cột rõ ràng."
        }

        # --- 3. KHỞI TẠO LỊCH SỬ & CHÈN LỜI CHÀO ---
        if "history" not in st.session_state:
            st.session_state.history = {}
        
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            # Chỉ chèn lời chào nếu có trong danh sách
            greeting_msg = initial_greetings.get(menu, "Xin chào! Tôi có thể giúp gì cho bạn?")
            st.session_state.history[menu].append({"role": "assistant", "content": greeting_msg})

        # Hiển thị lịch sử
        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # --- 4. XỬ LÝ CHAT ---
        # Lấy System Prompt đúng
        sys_prompt = personas.get(menu, f"Bạn là chuyên gia. {core_logic}")
        model = genai.GenerativeModel(best_model, system_instruction=sys_prompt)
        
        if prompt := st.chat_input("Nhập yêu cầu..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang thực hiện..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
