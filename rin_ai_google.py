import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Hệ Sinh Thái AI Toàn Diện", page_icon="💎", layout="wide")

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

# --- SIDEBAR: GIAO DIỆN MỚI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # 1. CẤU HÌNH KEY (GIAO DIỆN DỄ HIỂU NHƯ BẠN MUỐN)
    st.subheader("🔑 Cấu hình tài khoản")
    
    key_option = st.radio(
        "Chọn chế độ sử dụng:",
        ["🚀 Dùng Miễn Phí (Server Thầy)", "💎 Nhập Key Của Bạn (VIP)"],
        captions=["Giới hạn tốc độ, dành cho trải nghiệm.", "Tốc độ cao, không giới hạn, bảo mật."]
    )
    
    final_key = None
    
    if key_option == "🚀 Dùng Miễn Phí (Server Thầy)":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server chung")
        except:
            st.error("❌ Server đang bảo trì (Chưa có Key hệ thống)")
            
    else: # Chế độ nhập Key cá nhân
        final_key = st.text_input("Dán API Key của bạn vào đây:", type="password")
        
        # Hướng dẫn lấy Key (Dạng xổ xuống gọn gàng)
        with st.expander("❓ Hướng dẫn lấy Key (30 giây)"):
            st.markdown("""
            1. Truy cập: **[Google AI Studio](https://aistudio.google.com/)**
            2. Đăng nhập Gmail -> Bấm **Get API key**.
            3. Bấm **Create API key** -> Copy mã.
            4. Dán vào ô bên trên.
            """)
        
        if final_key:
            st.success("✅ Đã nhận Key VIP")

    st.divider()

    # 2. DANH MỤC CHUYÊN GIA (12 MODULE CHI TIẾT)
    st.subheader("📂 Chọn Lĩnh Vực")
    
    menu = st.radio(
        "Bạn cần hỗ trợ về:",
        [
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

if not final_key:
    st.info("👋 Chào mừng! Vui lòng chọn chế độ Key bên tay trái để bắt đầu.")
    st.stop()

# Cấu hình AI
best_model = get_best_model(final_key)
genai.configure(api_key=final_key)

# --- XỬ LÝ GIAO DIỆN MEDIA (TẠO ẢNH) RIÊNG BIỆT ---
if menu == "🎨 Thiết Kế - Ảnh - Video (Media)":
    st.header("🎨 Studio Sáng Tạo Đa Phương Tiện")
    st.markdown("Tại đây bạn có thể tạo ảnh trực tiếp hoặc lên kịch bản cho Video/Voice.")
    
    media_tab = st.tabs(["🖼️ Tạo Ảnh (Imagen)", "🎬 Kịch Bản Video (Veo/Sora)", "🎙️ Kịch Bản Voice (Lyria)"])
    
    with media_tab[0]: # Tạo ảnh
        desc = st.text_area("Mô tả hình ảnh bạn muốn vẽ:", height=100)
        if st.button("Vẽ Ngay"):
            with st.spinner("Đang vẽ..."):
                model = genai.GenerativeModel(best_model)
                trans = model.generate_content(f"Translate to English for Image Gen: {desc}").text
                final = trans.replace(" ", "%20")
                st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Rin.Ai generated")
    
    with media_tab[1]: # Video
        st.info("Hiện tại Google Veo chưa mở API công khai. Rin.Ai sẽ giúp bạn viết Prompt/Kịch bản chi tiết để bạn dùng khi công cụ đó ra mắt.")
        video_topic = st.text_input("Chủ đề video:")
        if st.button("Viết Kịch Bản Video"):
            model = genai.GenerativeModel(best_model)
            st.write(model.generate_content(f"Viết kịch bản video ngắn 60s viral về chủ đề: {video_topic}. Chia cột: Hình ảnh - Âm thanh - Lời bình.").text)

    with media_tab[2]: # Voice
        voice_topic = st.text_input("Nội dung cần thu âm:")
        if st.button("Tạo lời bình"):
            model = genai.GenerativeModel(best_model)
            st.write(model.generate_content(f"Viết lời bình (Voiceover) cảm xúc cho nội dung: {voice_topic}. Đánh dấu chỗ nào cần nhấn giọng, ngắt nghỉ.").text)

# --- XỬ LÝ CÁC MODULE CHATBOT KHÁC ---
else:
    st.header(menu)
    
    # SYSTEM INSTRUCTION (Linh hồn của từng chuyên gia)
    # Tôi sử dụng kỹ thuật "Consultative Prompting" (Hỏi trước - Trả lời sau) cho các module chuyên sâu
    
    base_consultant_logic = """
    QUY TRÌNH TƯ VẤN:
    1. Nếu người dùng hỏi chung chung -> HÃY HỎI LẠI 3-5 câu để lấy bối cảnh (Sản phẩm, Khách hàng, Ngân sách...).
    2. Nếu đã có đủ thông tin -> Đưa giải pháp chi tiết, bảng biểu, quy trình.
    """
    
    personas = {
        "✨ Trợ Lý Đa Lĩnh Vực (Gemini)": "Bạn là Trợ lý AI hữu ích, trả lời nhanh, ngắn gọn, đi thẳng vào vấn đề giống như ChatGPT/Gemini. Không cần hỏi lại.",
        
        "🏢 Trợ Lý Giám Đốc & Chiến Lược": f"""Bạn là Cố vấn Chiến lược cấp cao. {base_consultant_logic}
        Chuyên môn: Quản trị nhân sự, KPI, Dòng tiền, Xây dựng văn hóa doanh nghiệp.""",
        
        "✍️ Marketing - Content - Social": f"""Bạn là Giám đốc Marketing (CMO). {base_consultant_logic}
        Chuyên môn: Viết Content TikTok/FB, Lên plan 30 ngày, Ý tưởng Viral, Email Marketing.""",
        
        "💰 Bán Hàng - Telesales - CSKH": f"""Bạn là Chuyên gia Sales. {base_consultant_logic}
        Chuyên môn: Xử lý từ chối, Kịch bản gọi điện, Chốt sale, Chăm sóc khách hàng sau bán.""",
        
        "🛒 Kinh Doanh Online / TMĐT": f"""Bạn là Top Seller Shopee/TikTok Shop. {base_consultant_logic}
        Chuyên môn: SEO sàn, Tối ưu tiêu đề, Phân tích chân dung khách hàng, Viết mô tả sản phẩm chuẩn SEO.""",
        
        "🌐 SEO - Website - Copywriting": f"""Bạn là Chuyên gia SEO & Web. {base_consultant_logic}
        Chuyên môn: Viết bài Blog chuẩn SEO, Nghiên cứu từ khóa, Cấu trúc Sitemap.""",
        
        "💻 Lập Trình - Coding - Automation": """Bạn là Senior Fullstack Developer.
        Nhiệm vụ: Viết code (Python, Apps Script, SQL...), Debug, Giải thích code.
        Yêu cầu: Chỉ đưa ra Code block và giải thích ngắn gọn.""",
        
        "💸 Tài Chính - Startup - Kiếm Tiền": f"""Bạn là Chuyên gia Tài chính & Startup. {base_consultant_logic}
        Chuyên môn: Lập kế hoạch kinh doanh (Business Plan), Gọi vốn, Quản lý tài chính cá nhân.""",
        
        "🏠 Bất Động Sản & Xe Hơi": f"""Bạn là Chuyên gia Môi giới BĐS & Xe sang. {base_consultant_logic}
        Chuyên môn: Viết tin đăng bán nhà/xe hấp dẫn, Phân tích phong thủy, Tư vấn pháp lý.""",
        
        "❤️ Y Tế - Sức Khỏe - Gym": f"""Bạn là Bác sĩ & PT Gym. {base_consultant_logic}
        Chuyên môn: Lên thực đơn giảm cân (Eat clean), Lịch tập Gym/Yoga. Lưu ý: Luôn khuyên người dùng đi khám bác sĩ nếu bệnh nặng.""",
        
        "🎓 Học Tập - Giáo Dục - Tự Học": """Bạn là Gia sư & Giáo sư Đại học.
        Nhiệm vụ: Tóm tắt sách, Giải bài tập, Luyện thi IELTS, Hướng dẫn tự học.
        Phong cách: Sư phạm, dễ hiểu."""
    }

    # Quản lý lịch sử chat riêng cho từng phòng
    if "history" not in st.session_state:
        st.session_state.history = {}
    if menu not in st.session_state.history:
        st.session_state.history[menu] = []

    # Hiển thị lịch sử
    for msg in st.session_state.history[menu]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Xử lý Chat
    system_prompt = personas.get(menu, "Bạn là trợ lý AI.")
    model = genai.GenerativeModel(best_model, system_instruction=system_prompt)
    
    # Gợi ý trong ô nhập liệu
    placeholders = {
        "✨ Trợ Lý Đa Lĩnh Vực (Gemini)": "Hỏi bất cứ điều gì...",
        "✍️ Marketing - Content - Social": "VD: Viết kịch bản TikTok cho quán cafe...",
        "💻 Lập Trình - Coding - Automation": "VD: Viết code Python lấy giá vàng...",
        "🏠 Bất Động Sản & Xe Hơi": "VD: Viết bài đăng bán đất nền Bảo Lộc..."
    }
    
    if prompt := st.chat_input(placeholders.get(menu, "Nhập yêu cầu của bạn...")):
        # User
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.history[menu].append({"role": "user", "content": prompt})
        
        # Assistant
        with st.chat_message("assistant"):
            with st.spinner("Chuyên gia đang phân tích..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Lỗi: {e}")
