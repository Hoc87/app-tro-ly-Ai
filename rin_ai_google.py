import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Siêu Ứng Dụng AI", page_icon="💎", layout="wide")

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
        st.markdown("""
        **👇 Hướng dẫn lấy Key (30s):**
        1. Vào **[Google AI Studio](https://aistudio.google.com/)**
        2. Bấm **Get API key** -> **Create API key**.
        3. Copy và dán vào ô dưới.
        """)
        final_key = st.text_input("Dán API Key của bạn:", type="password")
        if final_key: st.success("✅ Đã nhận Key")

    st.divider()

    # 2. MENU CHỨC NĂNG (ĐÃ BỔ SUNG ĐẦY ĐỦ 12 LĨNH VỰC + BÁO CHÍ)
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio(
        "Lĩnh vực:",
        [
            "🏠 Trang Chủ & Giới Thiệu", 
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
            "📰 Đọc Báo & Tóm Tắt Sách", # <-- MỚI
            "🎨 Thiết Kế & Media (Ảnh/Voice)",
            "👔 Nhân Sự - Tuyển Dụng - CV", # <-- MỚI
            "⚖️ Luật - Hợp Đồng - Hành Chính", # <-- MỚI
            "💰 Kinh Doanh & Marketing", 
            "🏢 Giám Đốc & Quản Trị (CEO)",
            "🛒 TMĐT (Shopee/TikTok Shop)",
            "💻 Lập Trình - Freelancer - Digital", # <-- Gộp Freelancer vào đây
            "❤️ Y Tế - Sức Khỏe - Gym",
            "✈️ Du Lịch - Lịch Trình - Vi Vu", # <-- MỚI
            "🧠 Tâm Lý - Cảm Xúc - Tinh Thần", # <-- MỚI
            "🎓 Giáo Dục & Đào Tạo",
            "🍽️ Nhà Hàng - F&B - Ẩm Thực", # <-- MỚI
            "📦 Logistic - Vận Hành - Kho Bãi", # <-- MỚI
            "📊 Kế Toán - Báo Cáo - Số Liệu", # <-- MỚI
            "🏗️ Kiến Trúc - Nội Thất - Xây Dựng", # <-- MỚI
            "🎤 Sự Kiện - MC - Hội Nghị", # <-- MỚI
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
        ### 🚀 Rin.Ai - Siêu Ứng Dụng Đa Năng
        
        Chào mừng bạn đến với danh sách trợ lý AI hàng đầu. Chúng tôi không nói lý thuyết, chúng tôi **GIẢI QUYẾT VẤN ĐỀ** cho bạn.
        
        **Quy trình tư vấn chuẩn chuyên gia:**
        1.  **Tiếp nhận:** Lắng nghe vấn đề.
        2.  **Khai thác:** Hỏi sâu về bối cảnh (Context).
        3.  **Giải pháp:** Đưa ra kế hoạch, quy trình, tài liệu mẫu.
        
        ---
        ### 👨‍🏫 Hỗ trợ chuyên môn:
        ## **Mr. Học** (Chuyên gia AI Ứng Dụng). 
        #### Nếu bạn muốn áp dụng Ai vào công việc thì vui lòng 📞 Liên hệ: **0901 108 788**
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

    # --- MODULE MEDIA (TẠO ẢNH & VOICE NÂNG CẤP VÙNG MIỀN) ---
    if menu == "🎨 Thiết Kế & Media (Ảnh/Voice)":
        st.header("🎨 Studio Sáng Tạo Đa Phương Tiện")
        st.success("Chào bạn! Bạn muốn vẽ ảnh hay tạo kịch bản Voice/Hội thoại?")
        
        media_mode = st.radio("👉 Chọn công cụ:", 
                              ["🖼️ Vẽ Ngay Lập Tức", 
                               "📝 Viết Prompt Ảnh",
                               "🎙️ Kịch Bản Voice (1 Người)",
                               "🗣️ Kịch Bản Hội Thoại (2 Người)"], horizontal=True)
        st.divider()

        if media_mode == "🖼️ Vẽ Ngay Lập Tức":
            desc = st.text_area("Mô tả ý tưởng:", height=100)
            if st.button("🎨 Vẽ Ngay"):
                if desc:
                    with st.spinner("Đang vẽ..."):
                        model = genai.GenerativeModel(best_model)
                        trans = model.generate_content(f"Translate to detailed English prompt: {desc}").text
                        final = trans.replace(" ", "%20")
                        st.image(f"https://image.pollinations.ai/prompt/{final}?nologo=true", caption="Rin.Ai generated")

        elif media_mode == "📝 Viết Prompt Ảnh":
            model = genai.GenerativeModel(best_model)
            prompt_topic = st.text_area("Ý tưởng ảnh:", placeholder="VD: Poster quảng cáo giày...")
            if st.button("📝 Viết Prompt"):
                st.markdown(model.generate_content(f"Viết 3 prompt Midjourney v6 về: {prompt_topic}. Thêm --ar 16:9. Giải thích tiếng Việt.").text)

        # VOICE 1 NGƯỜI (CÓ CHỌN VÙNG MIỀN)
        elif media_mode == "🎙️ Kịch Bản Voice (1 Người)":
            col1, col2, col3 = st.columns(3)
            gender = col1.radio("Giọng đọc:", ["Nam 👨", "Nữ 👩"])
            region = col2.selectbox("Vùng miền:", ["Giọng Bắc (Chuẩn)", "Giọng Trung (Huế/Đà Nẵng)", "Giọng Nam (Sài Gòn)"])
            tone = col3.selectbox("Cảm xúc:", ["Trầm ấm", "Vui tươi", "Nghiêm túc", "Buồn"])
            
            topic = st.text_area("Nội dung cần đọc:", placeholder="VD: Giới thiệu sản phẩm...")
            if st.button("🎙️ Viết Kịch Bản"):
                if topic:
                    model = genai.GenerativeModel(best_model)
                    prompt = f"""
                    Viết kịch bản Voiceover cho 1 người đọc.
                    - Giọng: {gender} - {region}.
                    - Cảm xúc: {tone}.
                    - Chủ đề: {topic}.
                    YÊU CẦU ĐẶC BIỆT:
                    - Sử dụng từ ngữ địa phương phù hợp với {region}.
                    - Đánh dấu [Ngắt nghỉ], [Nhấn mạnh], [Cười] để tạo cảm xúc.
                    """
                    st.markdown(model.generate_content(prompt).text)

        # HỘI THOẠI 2 NGƯỜI (CÓ CHỌN VÙNG MIỀN)
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Nhân vật A")
                ga = st.radio("Giới tính A:", ["Nam", "Nữ"], key="ga")
                ra = st.selectbox("Vùng miền A:", ["Bắc", "Trung", "Nam"], key="ra")
            with c2:
                st.markdown("### Nhân vật B")
                gb = st.radio("Giới tính B:", ["Nam", "Nữ"], key="gb")
                rb = st.selectbox("Vùng miền B:", ["Bắc", "Trung", "Nam"], key="rb")
            
            topic = st.text_area("Chủ đề trò chuyện:", placeholder="VD: Tranh luận về AI...")
            if st.button("🗣️ Tạo Hội Thoại"):
                if topic:
                    model = genai.GenerativeModel(best_model)
                    prompt = f"""
                    Viết kịch bản hội thoại giữa:
                    - NV A: {ga}, Giọng {ra}.
                    - NV B: {gb}, Giọng {rb}.
                    - Chủ đề: {topic}.
                    YÊU CẦU: 
                    - Phải thể hiện rõ phương ngữ của từng vùng miền trong lời thoại (VD: Nam nói 'chén', Bắc nói 'bát').
                    - Kịch bản tự nhiên, đời thường.
                    """
                    st.markdown(model.generate_content(prompt).text)

    # --- MODULE MỚI: ĐỌC BÁO & TÓM TẮT SÁCH ---
    elif menu == "📰 Đọc Báo & Tóm Tắt Sách":
        st.header("📰 Chuyên Gia Thông Tin & Tri Thức")
        task = st.radio("Bạn muốn làm gì?", ["🔎 Tìm & Tổng hợp tin tức", "📚 Tóm tắt Sách/Tài liệu"])
        
        model = genai.GenerativeModel(best_model)
        
        if task == "🔎 Tìm & Tổng hợp tin tức":
            st.info("Nhập lĩnh vực bạn quan tâm, AI sẽ tổng hợp kiến thức và xu hướng mới nhất.")
            topic = st.text_input("Lĩnh vực/Chủ đề (VD: Xu hướng Marketing 2025, Tin tức AI hôm nay...):")
            if st.button("🔎 Tìm kiếm & Tổng hợp") and topic:
                with st.spinner("Đang quét thông tin..."):
                    res = model.generate_content(f"""
                    Bạn là Chuyên gia Phân tích tin tức. Người dùng muốn biết về: "{topic}".
                    Nhiệm vụ:
                    1. Tổng hợp các xu hướng/thông tin quan trọng nhất liên quan đến chủ đề này (dựa trên kiến thức của bạn).
                    2. Trình bày dạng bản tin vắn: Tiêu đề - Nội dung chính - Tác động.
                    """).text
                    st.markdown(res)
                    
        else:
            st.info("Tóm tắt sách hoặc một đoạn văn bản dài.")
            book_name = st.text_area("Nhập tên sách hoặc dán nội dung văn bản vào đây:")
            if st.button("📚 Tóm tắt ngay") and book_name:
                with st.spinner("Đang đọc & Tóm tắt..."):
                    res = model.generate_content(f"""
                    Hãy tóm tắt cuốn sách/nội dung sau: "{book_name}".
                    Yêu cầu đầu ra:
                    1. Ý chính (Key Takeaways).
                    2. 5 Bài học cốt lõi áp dụng được vào cuộc sống.
                    3. Trích dẫn hay nhất.
                    """).text
                    st.markdown(res)

    # --- CÁC MODULE CHATBOT KHÁC (SYSTEM PROMPT ĐÃ NÂNG CẤP) ---
    else:
        st.header(menu)
        
        # 1. LỜI CHÀO CHỦ ĐỘNG (GREETINGS) - CẬP NHẬT CHO 12 MODULE MỚI
        initial_greetings = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": "Xin chào! Tôi là Gemini. Bạn cần tra cứu thông tin hay giải quyết vấn đề gì?",
            "🏢 Giám Đốc & Quản Trị (CEO)": "Chào Sếp! Hôm nay chúng ta bàn về: Nhân sự, Vận hành hay Chiến lược dòng tiền?",
            "💰 Kinh Doanh & Marketing": "Hello! Cần lên kế hoạch Marketing, Viết Content hay Chiến lược quảng cáo?",
            "👔 Nhân Sự - Tuyển Dụng - CV": "Chào bạn! Tôi là HR Manager. Bạn cần viết JD, lọc CV hay phỏng vấn thử ứng viên?",
            "⚖️ Luật - Hợp Đồng - Hành Chính": "Chào bạn. Tôi là Luật sư AI. Bạn cần rà soát hợp đồng hay soạn thảo văn bản hành chính?",
            "✈️ Du Lịch - Lịch Trình - Vi Vu": "Chào bạn! Muốn đi đâu nào? Tôi sẽ lên lịch trình ăn chơi từ A-Z cho bạn.",
            "🧠 Tâm Lý - Cảm Xúc - Tinh Thần": "Chào bạn. Có chuyện gì làm bạn phiền lòng không? Hãy chia sẻ nhé, tôi ở đây để lắng nghe.",
            "🍽️ Nhà Hàng - F&B - Ẩm Thực": "Chào Chủ quán! Cần lên Menu mới, Decor quán hay Tính Cost món ăn?",
            "📦 Logistic - Vận Hành - Kho Bãi": "Chào bạn. Cần tối ưu quy trình kho, vận chuyển hay xây dựng SOP vận hành?",
            "📊 Kế Toán - Báo Cáo - Số Liệu": "Chào bạn. Cần giải thích báo cáo tài chính, làm bảng tính hay tối ưu thuế?",
            "🏗️ Kiến Trúc - Nội Thất - Xây Dựng": "Chào KTS/Gia chủ. Bạn cần ý tưởng Concept, Moodboard hay Bố trí mặt bằng?",
            "🎤 Sự Kiện - MC - Hội Nghị": "Chào bạn. Cần kịch bản MC, Lời dẫn chương trình hay Plan tổ chức sự kiện?",
            "💻 Lập Trình - Freelancer - Digital": "Hello! Cần viết Code, viết Proposal hay quản lý dự án Freelance?",
            "🎓 Giáo Dục & Đào Tạo": "Chào bạn! Cho tôi biết bạn là **Giáo viên, Phụ huynh hay Học sinh** để tôi hỗ trợ nhé?",
            "❤️ Y Tế - Sức Khỏe - Gym": "Chào bạn! Cần thực đơn Eat Clean, Lịch tập Gym hay Tư vấn sức khỏe?"
        }

        # 2. SYSTEM INSTRUCTION (TƯ DUY CỐ VẤN - HỎI TRƯỚC TRẢ LỜI SAU)
        consultant_logic = """
        QUY TẮC CỐT LÕI: 
        1. KHI BẮT ĐẦU: Nếu người dùng hỏi ngắn gọn -> HỎI LẠI 3 câu để lấy bối cảnh (Ai? Cái gì? Ngân sách?...).
        2. KHI ĐÃ ĐỦ THÔNG TIN: Đưa giải pháp chi tiết, bảng biểu, quy trình, file mẫu.
        3. KHÔNG NÓI LÝ THUYẾT SUÔNG.
        """
        
        # Logic Giáo dục đặc biệt
        edu_logic = """
        NẾU LÀ HỌC SINH/PHỤ HUYNH: Đóng vai Giáo viên giỏi. GIẢI THÍCH CHI TIẾT, KHÔNG ĐƯA ĐÁP ÁN NGAY. Hướng dẫn tư duy theo SGK Việt Nam.
        NẾU LÀ GIÁO VIÊN: Hỗ trợ soạn giáo án, phương pháp 5E/STEM.
        """

        personas = {
            "✨ Trợ Lý Đa Lĩnh Vực (Chung)": f"Bạn là Trợ lý AI thông minh. {consultant_logic}",
            "🏢 Giám Đốc & Quản Trị (CEO)": f"Bạn là Cố vấn Quản trị. {consultant_logic} Tập trung vào KPI, OKR, Dòng tiền.",
            "💰 Kinh Doanh & Marketing": f"Bạn là CMO thực chiến. {consultant_logic}",
            "👔 Nhân Sự - Tuyển Dụng - CV": f"Bạn là Giám đốc Nhân sự (HRD). {consultant_logic} Chuyên viết JD, CV, Bộ câu hỏi phỏng vấn STAR.",
            "⚖️ Luật - Hợp Đồng - Hành Chính": f"Bạn là Luật sư kinh tế. {consultant_logic} Phân tích rủi ro pháp lý trong hợp đồng.",
            "✈️ Du Lịch - Lịch Trình - Vi Vu": f"Bạn là Hướng dẫn viên du lịch 5 sao. {consultant_logic} Lên lịch trình chi tiết giờ giấc, chi phí.",
            "🧠 Tâm Lý - Cảm Xúc - Tinh Thần": f"Bạn là Chuyên gia Tâm lý. {consultant_logic} Lắng nghe, thấu hiểu, không phán xét.",
            "🍽️ Nhà Hàng - F&B - Ẩm Thực": f"Bạn là Quản lý nhà hàng 5 sao. {consultant_logic} Tư vấn Menu, Concept, Cost.",
            "📦 Logistic - Vận Hành - Kho Bãi": f"Bạn là Giám đốc Vận hành (COO). {consultant_logic} Tối ưu quy trình SOP.",
            "📊 Kế Toán - Báo Cáo - Số Liệu": f"Bạn là Kế toán trưởng. {consultant_logic} Giải thích số liệu đơn giản dễ hiểu.",
            "🏗️ Kiến Trúc - Nội Thất - Xây Dựng": f"Bạn là Kiến trúc sư trưởng. {consultant_logic} Tư vấn phong cách, vật liệu, phong thủy.",
            "🎤 Sự Kiện - MC - Hội Nghị": f"Bạn là Đạo diễn sự kiện. {consultant_logic} Viết kịch bản chi tiết từng phút.",
            "💻 Lập Trình - Freelancer - Digital": f"Bạn là Senior Developer & Top Freelancer. {consultant_logic} Viết Proposal chinh phục khách hàng.",
            "❤️ Y Tế - Sức Khỏe - Gym": f"Bạn là Bác sĩ & PT. {consultant_logic} Lên thực đơn/lịch tập.",
            "🎓 Giáo Dục & Đào Tạo": f"{edu_logic}"
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
        # Wrapper cho Giáo dục
        user_prompt_wrapper = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            user_prompt_wrapper = " (Hãy xác định tôi là GV hay HS/PH để trả lời phù hợp. Nếu là HS, hãy giảng giải chi tiết, đừng chỉ đưa đáp án)"

        sys_prompt = personas.get(menu, f"Bạn là chuyên gia. {consultant_logic}")
        model = genai.GenerativeModel(best_model, system_instruction=sys_prompt)
        
        if prompt := st.chat_input("Nhập yêu cầu..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.history[menu].append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang soạn thảo..."):
                    try:
                        final_prompt = prompt + user_prompt_wrapper
                        response = model.generate_content(final_prompt)
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
