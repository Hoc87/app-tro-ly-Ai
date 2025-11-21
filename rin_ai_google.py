import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Chuyên Gia Thực Chiến", page_icon="🔥", layout="wide")

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

# --- SIDEBAR: MENU & CẤU HÌNH ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI SUPER APP")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # 1. Cấu hình Key
    key_mode = st.radio("🔑 Nguồn Key:", ["🚀 Dùng thử (Thầy)", "👤 Cá nhân"], horizontal=True)
    final_key = None
    if key_mode == "🚀 Dùng thử (Thầy)":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Key hệ thống")
        except:
            st.error("❌ Chưa có Key trong Secrets")
    else:
        final_key = st.text_input("Dán API Key:", type="password")
        if final_key: st.success("✅ Đã nhận Key")

    st.divider()

    # 2. MENU CHỨC NĂNG
    menu = st.radio(
        "📂 DANH MỤC CHUYÊN GIA:",
        [
            "🏠 Giới Thiệu & Liên Hệ",
            "🎨 Xưởng Sáng Tạo (Tạo Ảnh)",
            "💰 Kinh Doanh & Marketing (Thực Chiến)",
            "🏢 CEO & Quản Trị Doanh Nghiệp",
            "🍎 Giáo Dục & Đào Tạo (Chuyên Sâu)",
            "🤖 Trợ Lý Đa Năng (Vạn Sự Thông)"
        ]
    )

# --- NỘI DUNG CHÍNH ---

if menu != "🏠 Giới Thiệu & Liên Hệ" and not final_key:
    st.warning("👉 Vui lòng nhập API Key bên tay trái để gặp chuyên gia.")
    st.stop()

if final_key:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

# ==============================================================================
# TRANG CHỦ
# ==============================================================================
if menu == "🏠 Giới Thiệu & Liên Hệ":
    st.title("👋 Rin.Ai - Trợ Lý AI Thực Chiến")
    st.markdown("""
    ### 🌟 Điểm Khác Biệt Của Rin.Ai
    Không giống các công cụ Chatbot thông thường chỉ trả lời lý thuyết, **Rin.Ai** được lập trình để đóng vai những **Chuyên gia hàng đầu với 10+ năm kinh nghiệm**.
    
    Chúng tôi tập trung vào: **GIẢI PHÁP THỰC TẾ - SỐ LIỆU CỤ THỂ - HÀNH ĐỘNG NGAY**.
    
    ---
    ### 👨‍🏫 Nhà Phát Triển
    ## **Chuyên gia: Mr. Học**
    #### 📞 Hotline/Zalo: **0901 108 788**
    
    > *Chuyên gia đào tạo ứng dụng AI thực chiến cho Doanh nghiệp & Cá nhân.*
    """)
    st.info("👈 **Chọn lĩnh vực bên trái để bắt đầu làm việc!**")

# ==============================================================================
# CHỨC NĂNG 1: TẠO ẢNH (GIỮ NGUYÊN TÍNH NĂNG VẼ)
# ==============================================================================
elif menu == "🎨 Xưởng Sáng Tạo (Tạo Ảnh)":
    st.header("🎨 Xưởng Vẽ Tranh AI")
    mode = st.selectbox("Chọn chế độ:", ["🖼️ Vẽ ảnh trực tiếp", "📝 Viết Prompt Midjourney"])
    
    if mode == "🖼️ Vẽ ảnh trực tiếp":
        img_desc = st.text_area("Mô tả ý tưởng (VD: Logo cafe phong cách vintage...):", height=100)
        if st.button("🎨 Vẽ Ngay"):
            if img_desc:
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    trans_prompt = model.generate_content(f"Translate to English for Image Gen: {img_desc}").text
                    final_prompt = trans_prompt.replace(" ", "%20")
                    st.image(f"https://image.pollinations.ai/prompt/{final_prompt}?nologo=true", caption="Kết quả từ Rin.Ai")
    else:
        # Prompt chuyên gia Art Director
        sys_art = """Bạn là Art Director (Giám đốc nghệ thuật) nổi tiếng. 
        Nhiệm vụ: Viết prompt tiếng Anh cho Midjourney v6. 
        Yêu cầu: Prompt phải cực kỳ chi tiết về ánh sáng (Lighting), góc máy (Camera angle), chất liệu (Texture), phong cách (Style). 
        Không giải thích dài dòng, chỉ đưa ra Prompt code."""
        model = genai.GenerativeModel(best_model, system_instruction=sys_art)
        prompt_req = st.text_area("Ý tưởng của bạn:")
        if st.button("📝 Sinh Prompt"):
            st.code(model.generate_content(prompt_req).text)

# ==============================================================================
# CÁC CHUYÊN GIA THỰC CHIẾN (PHẦN QUAN TRỌNG NHẤT)
# ==============================================================================
else:
    # ĐÂY LÀ PHẦN "CẤY NÃO" CHO AI - QUYẾT ĐỊNH ĐỘ THÔNG MINH
    personas = {
        "💰 Kinh Doanh & Marketing (Thực Chiến)": """
            BẠN LÀ: Một "Top Seller" và Chuyên gia Marketing thực chiến với 15 năm kinh nghiệm lăn lộn trên các sàn TMĐT (Shopee, Amazon), Facebook Ads và TikTok Shop.
            
            TÍNH CÁCH:
            - Thẳng thắn, thực dụng, tập trung vào DOANH SỐ (Sales) và LỢI NHUẬN (Profit).
            - Ghét lý thuyết suông. Luôn nói chuyện bằng con số, quy trình (Step-by-step) và kịch bản mẫu.
            
            NHIỆM VỤ CỦA BẠN KHI TRẢ LỜI:
            1. Tuyệt đối KHÔNG đưa ra lời khuyên chung chung kiểu "Hãy làm nội dung hay hơn".
            2. PHẢI đưa ra: Tiêu đề mẫu giật tít, Kịch bản chốt sale từng câu chữ, Công thức định giá sản phẩm, Cách target khách hàng cụ thể.
            3. Nếu người dùng hỏi về xử lý từ chối, hãy đóng vai người bán hàng và viết lại đoạn hội thoại mẫu để họ copy.
        """,

        "🏢 CEO & Quản Trị Doanh Nghiệp": """
            BẠN LÀ: Một CEO kỳ cựu đã từng điều hành các tập đoàn lớn và vực dậy nhiều công ty khởi nghiệp (Startup).
            
            TÍNH CÁCH:
            - Quyết đoán, tư duy chiến lược, nhìn xa trông rộng nhưng rất chi tiết trong quản trị.
            - Chuyên nghiệp, dùng ngôn ngữ quản trị cao cấp (KPI, OKR, ROI, Cashflow).
            
            NHIỆM VỤ CỦA BẠN KHI TRẢ LỜI:
            1. Đưa ra các bảng biểu mẫu, quy trình vận hành chuẩn (SOP).
            2. Giải quyết vấn đề nhân sự bằng tư duy "Củ cà rốt và Cây gậy".
            3. Khi tư vấn chiến lược, hãy vẽ ra lộ trình 30 ngày, 60 ngày, 90 ngày cụ thể.
            4. Luôn cảnh báo rủi ro (Risk Management) mà chủ doanh nghiệp có thể gặp phải.
        """,

        "🍎 Giáo Dục & Đào Tạo (Chuyên Sâu)": """
            BẠN LÀ: Một Thạc sĩ Giáo dục và Chuyên gia đào tạo giáo viên với 20 năm đứng lớp.
            
            TÍNH CÁCH:
            - Sư phạm, chỉn chu, kiên nhẫn nhưng đầy sáng tạo.
            - Am hiểu sâu sắc tâm lý học sinh/học viên và các phương pháp dạy học hiện đại (STEM, Gamification, Flipped Classroom).
            
            NHIỆM VỤ CỦA BẠN KHI TRẢ LỜI:
            1. Khi soạn giáo án: Phải chia cột rõ ràng (Hoạt động GV - Hoạt động HS - Thời gian).
            2. Khi thiết kế trò chơi: Phải có luật chơi, cách tính điểm, và ý nghĩa giáo dục.
            3. Cung cấp các bảng kiểm (Rubric) đánh giá chi tiết.
            4. Không nói lý thuyết giáo điều, hãy đưa ra ví dụ thực tế áp dụng trong lớp học.
        """,

        "🤖 Trợ Lý Đa Năng (Vạn Sự Thông)": """
            BẠN LÀ: Một trợ lý AI siêu việt, thông minh, hài hước và tận tụy.
            Nhiệm vụ: Giải quyết mọi vấn đề trong cuộc sống từ Lập trình, Sửa văn bản, Dịch thuật, Nấu ăn, Tâm sự...
            Yêu cầu: Câu trả lời phải ngắn gọn, súc tích, đi thẳng vào vấn đề.
        """
    }

    st.header(menu)
    
    # Lịch sử chat
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    if menu not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[menu] = []

    for msg in st.session_state.chat_sessions[menu]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Xử lý Chat
    # Kích hoạt "NÃO" chuyên gia tương ứng
    model = genai.GenerativeModel(best_model, system_instruction=personas.get(menu))
    
    if prompt := st.chat_input(f"Nhập vấn đề bạn cần chuyên gia hỗ trợ..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_sessions[menu].append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Chuyên gia đang phân tích & soạn giải pháp..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.chat_sessions[menu].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Lỗi: {e}")
