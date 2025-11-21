import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Cố Vấn Chuyên Sâu", page_icon="🧠", layout="wide")

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

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI CONSULTANT")
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
        "📂 CHỌN PHÒNG BAN:",
        [
            "🏠 Sảnh Chờ (Giới Thiệu)",
            "🎨 Phòng Sáng Tạo (Tạo Ảnh)",
            "💰 Phòng Kinh Doanh & Marketing",
            "🏢 Phòng Giám Đốc (CEO)",
            "🍎 Phòng Đào Tạo (Giáo Viên)",
            "⚖️ Phòng Pháp Lý & Hợp Đồng"
        ]
    )

# --- NỘI DUNG CHÍNH ---

if menu != "🏠 Sảnh Chờ (Giới Thiệu)" and not final_key:
    st.warning("👉 Vui lòng nhập API Key để vào phòng gặp chuyên gia.")
    st.stop()

if final_key:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

# ==============================================================================
# TRANG CHỦ
# ==============================================================================
if menu == "🏠 Sảnh Chờ (Giới Thiệu)":
    st.title("👋 Chào mừng đến với Rin.Ai Consultant")
    st.markdown("""
    ### 💎 ĐIỂM KHÁC BIỆT: "TƯ DUY CỐ VẤN"
    Tại đây, AI sẽ không trả lời bạn ngay lập tức bằng những lý thuyết sáo rỗng.
    
    **Quy trình làm việc của Rin.Ai:**
    1.  **Lắng nghe:** Tiếp nhận vấn đề của bạn.
    2.  **Khai thác (Audit):** AI sẽ hỏi ngược lại bạn những câu hỏi quan trọng để hiểu rõ bối cảnh (Sản phẩm, mô hình, nhân sự...).
    3.  **Giải pháp (Solution):** Sau khi đủ thông tin, AI mới đưa ra chiến lược "may đo" riêng cho bạn.
    
    ---
    **Được phát triển bởi: Mr. Học (0901 108 788)**
    """)
    st.info("👈 **Mời bạn chọn phòng ban cần tư vấn bên tay trái.**")

# ==============================================================================
# CHỨC NĂNG 1: TẠO ẢNH
# ==============================================================================
elif menu == "🎨 Phòng Sáng Tạo (Tạo Ảnh)":
    st.header("🎨 Xưởng Vẽ Tranh AI")
    mode = st.selectbox("Chế độ:", ["🖼️ Vẽ ảnh ngay", "📝 Tư vấn Prompt"])
    
    if mode == "🖼️ Vẽ ảnh ngay":
        img_desc = st.text_area("Mô tả ý tưởng:", height=100)
        if st.button("🎨 Vẽ Ngay"):
            if img_desc:
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    trans = model.generate_content(f"Translate to English for Image Gen: {img_desc}").text
                    final = trans.replace(" ", "%20")
                    st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true")
    else:
        # Prompt chuyên gia tư vấn ảnh
        sys_art = """Bạn là Art Director. Khi người dùng đưa ý tưởng, ĐỪNG VIẾT PROMPT NGAY.
        Hãy hỏi họ: Phong cách mong muốn (Realistic, Anime, 3D)? Tỷ lệ khung hình? Ánh sáng? Màu sắc chủ đạo?
        Sau khi họ trả lời, mới viết Prompt tiếng Anh cho Midjourney."""
        model = genai.GenerativeModel(best_model, system_instruction=sys_art)
        prompt_req = st.text_area("Ý tưởng sơ khởi:")
        if st.button("📝 Gặp chuyên gia"):
            st.code(model.generate_content(prompt_req).text)

# ==============================================================================
# CÁC PHÒNG BAN CHUYÊN GIA (CORE UPGRADE)
# ==============================================================================
else:
    # ĐÂY LÀ PHẦN NÂNG CẤP "TƯ DUY CỐ VẤN"
    # Tôi sử dụng kỹ thuật "Chain-of-thought" và "Interrogation Prompting"
    
    personas = {
        "💰 Phòng Kinh Doanh & Marketing": """
            BẠN LÀ: Giám đốc Marketing (CMO) thực chiến.
            
            QUY TRÌNH LÀM VIỆC BẮT BUỘC:
            BƯỚC 1: KHI NGƯỜI DÙNG ĐƯA RA YÊU CẦU ĐẦU TIÊN (VD: "Viết bài quảng cáo", "Cách bán hàng").
            -> TUYỆT ĐỐI KHÔNG TRẢ LỜI NGAY LẬP TỨC.
            -> Hãy đóng vai người cố vấn, hỏi ngược lại người dùng 3-5 câu hỏi để thu thập dữ liệu (Context).
            -> Các câu hỏi cần khai thác: Sản phẩm là gì? Giá bán? Khách hàng mục tiêu (Chân dung)? Điểm USP (Lợi thế cạnh tranh)? Kênh bán (Facebook, Shopee...)?
            
            BƯỚC 2: SAU KHI NGƯỜI DÙNG TRẢ LỜI CÁC CÂU HỎI TRÊN.
            -> Lúc này mới sử dụng kiến thức Google Ecosystem để viết nội dung chi tiết, sát sườn, có số liệu và kịch bản mẫu.
            
            LƯU Ý: Giọng văn chuyên nghiệp, gắt gao, tập trung vào chuyển đổi ra tiền (Conversion).
        """,

        "🏢 Phòng Giám Đốc (CEO)": """
            BẠN LÀ: Cố vấn Quản trị Doanh nghiệp cấp cao (Senior Business Consultant).
            
            QUY TRÌNH LÀM VIỆC BẮT BUỘC:
            BƯỚC 1: KHAI THÁC BỐI CẢNH.
            Khi người dùng hỏi (VD: "Nhân viên lười", "Doanh thu giảm"), KHÔNG ĐƯỢC đưa lời khuyên chung chung.
            Hãy hỏi họ: Quy mô công ty bao nhiêu người? Mô hình kinh doanh (B2B/B2C)? Đã có quy trình/KPI chưa? Dòng tiền hiện tại thế nào?
            
            BƯỚC 2: ĐƯA GIẢI PHÁP.
            Dựa trên câu trả lời, hãy đưa ra lộ trình giải quyết 3 giai đoạn: Ngắn hạn (Xử lý ngay) -> Trung hạn -> Dài hạn.
            Sử dụng các mô hình quản trị (SWOT, OKR, 5W1H) để phân tích.
        """,

        "🍎 Phòng Đào Tạo (Giáo Viên)": """
            BẠN LÀ: Chuyên gia Phương pháp Sư phạm.
            
            QUY TRÌNH LÀM VIỆC BẮT BUỘC:
            BƯỚC 1: THU THẬP THÔNG TIN LỚP HỌC.
            Khi giáo viên yêu cầu soạn giáo án hay trò chơi, hãy hỏi: 
            - Đối tượng học sinh (Lớp mấy, trình độ)? 
            - Thời lượng tiết học? 
            - Cơ sở vật chất có gì (Máy chiếu, bảng, sân bãi)?
            - Mục tiêu bài học là gì (Kiến thức hay Kỹ năng)?
            
            BƯỚC 2: THIẾT KẾ BÀI GIẢNG.
            Soạn giáo án chi tiết dựa trên các thông tin trên.
        """,
        
        "⚖️ Phòng Pháp Lý & Hợp Đồng": """
            BẠN LÀ: Luật sư kinh tế 20 năm kinh nghiệm.
            
            QUY TRÌNH:
            1. Hỏi rõ: Loại hợp đồng gì? Giá trị bao nhiêu? Bên A và Bên B là ai? Điều khoản quan trọng nhất muốn bảo vệ là gì?
            2. Sau đó mới soạn thảo các điều khoản chặt chẽ để bảo vệ quyền lợi người dùng.
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
    model = genai.GenerativeModel(best_model, system_instruction=personas.get(menu))
    
    if prompt := st.chat_input(f"Gõ vấn đề của bạn (VD: Tôi muốn viết bài bán son)..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_sessions[menu].append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Chuyên gia đang phân tích bối cảnh..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.chat_sessions[menu].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Lỗi: {e}")
