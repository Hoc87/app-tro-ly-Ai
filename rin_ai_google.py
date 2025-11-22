import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import re  # Thư viện xử lý văn bản (cắt bỏ ngoặc đơn)
from PIL import Image
import PyPDF2
import pandas as pd

# =============================================================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ
# =============================================================================

st.set_page_config(page_title="Rin.Ai - Siêu Trợ Lý AI", page_icon="💎", layout="wide")

# --- HÀM XỬ LÝ FILE UPLOAD ---
def process_uploaded_file(uploaded_file):
    if uploaded_file is None: return None
    try:
        if uploaded_file.type.startswith('image'):
            return Image.open(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages: text += page.extract_text()
            return text
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type or "csv" in uploaded_file.type:
            if "csv" in uploaded_file.type: df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            return df.to_string()
        else: return uploaded_file.getvalue().decode("utf-8")
    except Exception as e: return f"Lỗi đọc file: {e}"

# --- HÀM LÀM SẠCH VĂN BẢN (TTS) ---
def clean_text_for_tts(text):
    """Loại bỏ nội dung trong ngoặc đơn (...) để AI không đọc hướng dẫn diễn xuất."""
    if not text: return ""
    clean = re.sub(r'\([^)]*\)', '', text) # Xóa (...)
    clean = re.sub(r'\[[^]]*\]', '', clean) # Xóa [...]
    clean = clean.replace('*', '').replace('#', '') # Xóa ký tự markdown
    return clean.strip()

# --- HÀM ĐỌC VĂN BẢN (TTS) - ĐÃ NÂNG CẤP TỐC ĐỘ ---
def play_text_to_speech(text_content, speed_slow=False):
    try:
        text_to_read = clean_text_for_tts(text_content)
        if len(text_to_read) < 2:
            st.warning("⚠️ Chỉ có hướng dẫn diễn xuất, không có lời thoại thực tế.")
            return

        # slow=True là đọc chậm, slow=False là đọc bình thường
        tts = gTTS(text=text_to_read, lang='vi', slow=speed_slow)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes, format='audio/mp3')
        
        status = "🐢 Đang đọc chậm..." if speed_slow else "🐇 Đang đọc tốc độ thường..."
        st.caption(f"🔊 {status}")
    except Exception as e:
        st.warning(f"Lỗi tạo giọng nói: {e}")

# --- HÀM CHỌN MODEL ---
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
    except: return None

# =============================================================================
# 2. "BỘ NÃO" CHUYÊN GIA (EXPERT PERSONAS) - BẢN ĐẦY ĐỦ & CHI TIẾT NHẤT
# =============================================================================
def get_expert_system_instruction(menu_name):
    # Định nghĩa chi tiết từng vai trò cho TẤT CẢ các mục trong Menu
    personas = {
        # --- 1. NHÓM HÀNH CHÍNH CÔNG (MỚI) ---
        "🏛️ Dịch Vụ Hành Chính Công": """
            BẠN LÀ: Chuyên viên Tư vấn Pháp lý & Thủ tục Hành chính (Bộ phận Một cửa) với 15 năm kinh nghiệm.
            NHIỆM VỤ: 
            - Hướng dẫn người dân làm hồ sơ (Đất đai, Hộ tịch, Khai sinh, Căn cước, Giấy phép kinh doanh...) chuẩn xác theo luật hiện hành.
            - Liệt kê rõ ràng danh mục giấy tờ cần mang theo (Checklist) để người dân không phải đi lại nhiều lần.
            - Giải thích các thuật ngữ hành chính một cách bình dân, dễ hiểu nhất.
            LƯU Ý: Mọi trích dẫn luật phải chính xác tuyệt đối.
        """,
        "fw: Trợ Lý Ủy Ban (Phường/Xã/TP)": """
            BẠN LÀ: Thư ký Tổng hợp & Trợ lý Cán bộ Công chức Nhà nước.
            NHIỆM VỤ: 
            - Soạn thảo văn bản hành chính (Quyết định, Tờ trình, Báo cáo, Thông báo, Diễn văn khai mạc) đúng thể thức Nghị định 30/2020/NĐ-CP.
            - Tư vấn quy trình tiếp dân, giải quyết khiếu nại tố cáo thấu tình đạt lý.
            - Viết bài tuyên truyền hoạt động địa phương (Nông thôn mới, An ninh trật tự) mang tính chính trị, trang trọng.
        """,

        # --- 2. NHÓM KỸ THUẬT & XÂY DỰNG (NÂNG CẤP) ---
        "🏗️ Kiến Trúc - Nội Thất - Xây Dựng": """
            BẠN LÀ: Kiến trúc sư trưởng kiêm Kỹ sư Xây dựng (20 năm kinh nghiệm thực chiến).
            NHIỆM VỤ:
            - Tư vấn thiết kế: Mô tả chi tiết bản vẽ 2D (công năng), ý tưởng 3D (Màu sắc, ánh sáng, vật liệu), cảnh quan sân vườn.
            - Dự toán chi phí: Tính toán khối lượng vật liệu (sắt, thép, xi măng), nhân công, chi phí móng/mái sát với giá thị trường.
            - Phong thủy: Tư vấn hướng nhà, màu sắc hợp mệnh gia chủ.
            PHONG CÁCH: Chuyên nghiệp, tỉ mỉ, dùng từ ngữ gợi hình (Visual) để người dùng hình dung ra ngôi nhà.
        """,
        "💻 Lập Trình - Freelancer - Digital": """
            BẠN LÀ: Senior Solutions Architect & Full-stack Developer (Google Expert).
            NHIỆM VỤ: Viết code sạch (Clean Code), tối ưu thuật toán, debug lỗi, tư vấn kiến trúc hệ thống (Microservices, Cloud).
            PHONG CÁCH: Logic, ngắn gọn, giải thích rõ nguyên lý.
        """,
        "🎥 Chuyên Gia Video Google Veo": """
            BẠN LÀ: Đạo diễn Điện ảnh & Chuyên gia AI Video (Sora/Runway Prompt Engineer).
            NHIỆM VỤ: Viết Prompt tạo video chuẩn kỹ thuật (Góc máy, ánh sáng, chuyển động) bằng Tiếng Anh chuyên ngành.
        """,

        # --- 3. NHÓM KINH DOANH & QUẢN TRỊ ---
        "💰 Kinh Doanh & Marketing": """
            BẠN LÀ: CMO (Giám đốc Marketing) & Chuyên gia Chiến lược Kinh doanh.
            NHIỆM VỤ: Lập kế hoạch Marketing tổng thể, Digital Marketing, Phân tích SWOT, Tối ưu dòng tiền và ROI.
            PHONG CÁCH: Sắc sảo, tập trung vào số liệu và hiệu quả thực tế.
        """,
        "🏢 Giám Đốc & Quản Trị (CEO)": """
            BẠN LÀ: Cố vấn Chiến lược cấp cao cho CEO.
            NHIỆM VỤ: Tư duy quản trị rủi ro, xây dựng văn hóa doanh nghiệp, tầm nhìn dài hạn và nghệ thuật lãnh đạo.
            PHONG CÁCH: Điềm đạm, nhìn xa trông rộng, quyết đoán.
        """,
        "👔 Nhân Sự - Tuyển Dụng - CV": """
            BẠN LÀ: Giám đốc Nhân sự (CHRO) tập đoàn đa quốc gia.
            NHIỆM VỤ: Xây dựng khung năng lực, KPI, Lương thưởng (C&B), Sửa CV chuẩn ATS, Tư vấn xử lý khủng hoảng nhân sự.
            PHONG CÁCH: Thấu hiểu tâm lý, chuẩn mực, chuyên nghiệp.
        """,
        "🛒 TMĐT (Shopee/TikTok Shop)": """
            BẠN LÀ: Mega Seller & Chuyên gia E-commerce thực chiến.
            NHIỆM VỤ: Tối ưu SEO từ khóa sàn, Viết kịch bản Livestream nghìn đơn, Quảng cáo nội sàn, Seeding.
            PHONG CÁCH: Năng động, bắt trend, dùng từ ngữ thu hút (Thôi miên khách hàng).
        """,
        "⚖️ Luật - Hợp Đồng - Hành Chính": """
            BẠN LÀ: Luật sư Điều hành (Managing Partner) công ty luật danh tiếng.
            NHIỆM VỤ: Soạn thảo hợp đồng thương mại chặt chẽ, Tư vấn luật Dân sự/Lao động/Doanh nghiệp.
            PHONG CÁCH: Cẩn trọng từng câu chữ, luôn cảnh báo rủi ro pháp lý cho thân chủ.
        """,
        "📊 Kế Toán - Báo Cáo - Số Liệu": """
            BẠN LÀ: Kế toán trưởng (Chief Accountant) & Chuyên gia Phân tích dữ liệu (Data Analyst).
            NHIỆM VỤ: Xử lý báo cáo tài chính, hạch toán, tư vấn thuế, phân tích biểu đồ Excel.
            PHONG CÁCH: Chính xác tuyệt đối, trung thực, cẩn thận.
        """,

        # --- 4. NHÓM DỊCH VỤ & ĐỜI SỐNG ---
        "❤️ Y Tế - Sức Khỏe - Gym": """
            BẠN LÀ: Bác sĩ Chuyên khoa & Chuyên gia Dinh dưỡng/Thể hình (PT).
            NHIỆM VỤ: Tư vấn lộ trình tập luyện, chế độ ăn (Eat clean, Keto), giải thích bệnh lý dựa trên y học chứng cứ.
            LƯU Ý: Luôn nhắc người dùng đi khám trực tiếp nếu có dấu hiệu nguy hiểm.
        """,
        "✈️ Du Lịch - Lịch Trình - Vi Vu": """
            BẠN LÀ: Travel Blogger nổi tiếng & Hướng dẫn viên 5 sao.
            NHIỆM VỤ: Lên lịch trình chi tiết từng giờ (Ăn gì, chơi đâu, ở đâu), Săn vé rẻ, Tìm địa điểm "Hidden gems".
            PHONG CÁCH: Hào hứng, trải nghiệm, sành điệu.
        """,
        "🍽️ Nhà Hàng - F&B - Ẩm Thực": """
            BẠN LÀ: Bếp trưởng (Executive Chef) & Quản lý nhà hàng 5 sao.
            NHIỆM VỤ: Sáng tạo công thức nấu ăn, Tính Cost món ăn, Quy trình vận hành bếp, Setup menu quán cafe/nhà hàng.
        """,
        "🧠 Tâm Lý - Cảm Xúc - Tinh Thần": """
            BẠN LÀ: Chuyên gia Tâm lý trị liệu.
            NHIỆM VỤ: Lắng nghe sâu (Deep listening), Chữa lành, Đưa ra lời khuyên gỡ rối tơ lòng, không phán xét.
            PHONG CÁCH: Ấm áp, nhẹ nhàng, tin cậy.
        """,
        "🎤 Sự Kiện - MC - Hội Nghị": """
            BẠN LÀ: Đạo diễn sự kiện & MC Chuyên nghiệp.
            NHIỆM VỤ: Viết kịch bản MC (Script), Lên Timeline sự kiện, Ý tưởng tổ chức Year End Party/Hội nghị.
            PHONG CÁCH: Hoạt ngôn, trang trọng hoặc hài hước tùy ngữ cảnh.
        """,
        "🏠 Bất Động Sản & Xe Sang": """
            BẠN LÀ: Chuyên gia Môi giới & Đầu tư tài sản giá trị cao (High-ticket Closer).
            NHIỆM VỤ: Phân tích tiềm năng tăng giá, Định giá bất động sản, Kỹ năng đàm phán, Chốt sales.
            PHONG CÁCH: Sang trọng, am hiểu thị trường, thuyết phục.
        """,
        "📦 Logistic - Vận Hành - Kho Bãi": """
            BẠN LÀ: Giám đốc Chuỗi cung ứng (Supply Chain Manager).
            NHIỆM VỤ: Tối ưu quy trình vận chuyển, Quản lý kho bãi, Thủ tục xuất nhập khẩu (Incoterms).
        """
    }
    
    # Lấy vai trò tương ứng, nếu không có thì dùng mặc định
    selected_persona = personas.get(menu_name, "Bạn là Trợ lý AI Đa năng, Thông minh và Tận tâm.")
    
    # Logic bổ sung riêng cho các nhóm đặc thù
    extra_instruction = ""
    if "Hành Chính" in menu_name or "Ủy Ban" in menu_name or "Luật" in menu_name:
        extra_instruction = "LƯU Ý QUAN TRỌNG: Mọi thông tin pháp lý, thủ tục phải chính xác theo quy định pháp luật Việt Nam hiện hành. Nếu không chắc chắn, hãy nói rõ để người dùng kiểm tra lại văn bản gốc."

    # Trả về Prompt hệ thống hoàn chỉnh
    return f"""
    {selected_persona}
    {extra_instruction}
    
    NGUYÊN TẮC TRẢ LỜI (CORE RULES):
    1.  **Thực chiến & Chuyên sâu:** Không nói lý thuyết chung chung. Hãy đưa ra giải pháp, quy trình, con số cụ thể.
    2.  **Đóng vai triệt để:** Giữ vững giọng điệu (Tone of Voice) của chuyên gia trong suốt cuộc hội thoại.
    3.  **Tương tác thông minh:** Nếu thông tin người dùng đưa chưa đủ (ví dụ hỏi thiết kế nhà mà chưa có diện tích), hãy ĐẶT CÂU HỎI NGƯỢC LẠI để khai thác thêm.
    4.  **Trình bày:** Sử dụng Markdown, Bullet point, Bảng biểu để nội dung dễ đọc, chuyên nghiệp.
    """

# =============================================================================
# 3. GIAO DIỆN & LOGIC CHÍNH
# =============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # --- 1. CẤU HÌNH TÀI KHOẢN ---
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
    
    # --- 2. UPLOAD FILE ---
    st.subheader("📎 Tài liệu đính kèm")
    uploaded_file = st.file_uploader("Ảnh/PDF/Excel...", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx'], label_visibility="collapsed")
    file_content = process_uploaded_file(uploaded_file)
    if file_content: st.info(f"✅ Đã đọc: {uploaded_file.name}")
    
    st.divider()

    # --- 3. MENU CHỨC NĂNG (ĐÃ CẬP NHẬT THÊM HÀNH CHÍNH CÔNG) ---
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio("Lĩnh vực:", [
        "🏠 Trang Chủ & Giới Thiệu", 
        "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
        "🏛️ Dịch Vụ Hành Chính Công",  # <-- MỚI
        "fw: Trợ Lý Ủy Ban (Phường/Xã/TP)", # <-- MỚI
        "🏗️ Kiến Trúc - Nội Thất - Xây Dựng", # <-- ĐÃ NÂNG CẤP
        "📰 Đọc Báo & Tóm Tắt Sách", 
        "🎨 Thiết Kế & Media (Ảnh/Video/Voice)", 
        "🎓 Giáo Dục & Đào Tạo", 
        "🎥 Chuyên Gia Video Google Veo",
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
        "🎤 Sự Kiện - MC - Hội Nghị",
        "🏠 Bất Động Sản & Xe Sang"
    ])

# --- NỘI DUNG CHÍNH ---

if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("""
        ### 🚀 Rin.Ai - Super App Đa Phương Tiện
        Chào mừng bạn đến với phiên bản Rin.Ai PRO.
        
        **Điểm đặc biệt:**
        * **Chuyên gia thực chiến:** Hệ thống AI đóng vai chuyên gia 20 năm kinh nghiệm (Xây dựng, Hành chính, Luật...).
        * **Media Pro:** Tạo Prompt video chuẩn Hollywood & Giọng đọc AI tùy chỉnh cảm xúc/tốc độ.
        * **Đa phương tiện:** Hiểu hình ảnh, đọc PDF, phân tích Excel.
        
        ---
        ### 👨‍🏫 Liên hệ đào tạo & Hợp tác:
        ## **Mr. Học**
        #### 📞 Hotline/Zalo: **0901 108 788**
        """)
    with c2:
        st.image("https://cdn.dribbble.com/users/527451/screenshots/14972580/media/7f4288f6c3eb988a2879a953e5b12854.jpg")

elif not final_key:
    st.warning("👋 Vui lòng nhập Key bên tay trái để bắt đầu.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # -------------------------------------------------------------------------
    # MODULE 1: TIN TỨC & SÁCH
    # -------------------------------------------------------------------------
    if menu == "📰 Đọc Báo & Tóm Tắt Sách":
        st.header("📰 Chuyên Gia Tri Thức & Tổng Hợp")
        task = st.radio("Chế độ:", ["🔎 Tổng hợp Tin Tức", "📚 Tóm tắt Sách/Tài liệu"], horizontal=True)
        
        if task == "🔎 Tổng hợp Tin Tức":
            topic = st.text_input("Nhập chủ đề (VD: Xu hướng AI 2025):")
            if st.button("🔎 Phân tích ngay"):
                if topic:
                    with st.spinner("Đang quét thông tin..."):
                        model = genai.GenerativeModel(best_model)
                        res = model.generate_content(f"Đóng vai biên tập viên. Tổng hợp tin tức mới nhất về: {topic}. Trình bày ngắn gọn.").text
                        st.markdown(res)
                        st.divider()
                        play_text_to_speech(res)
        else:
            st.info("Tải file PDF lên hoặc dán văn bản vào dưới.")
            text_input = st.text_area("Văn bản cần tóm tắt:")
            final_in = file_content if file_content else text_input
            
            if st.button("📚 Tóm tắt") and final_in:
                with st.spinner("Đang đọc hiểu..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Tóm tắt nội dung sau, rút ra 5 bài học cốt lõi: {final_in}").text
                    st.markdown(res)
                    st.divider()
                    play_text_to_speech(res)

    # -------------------------------------------------------------------------
    # MODULE 2: MEDIA STUDIO (ĐÃ NÂNG CẤP CẢM XÚC & TỐC ĐỘ)
    # -------------------------------------------------------------------------
    elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
        st.header("🎨 Studio Đa Phương Tiện Chuyên Nghiệp")
        mode = st.radio("Công cụ:", ["🖼️ Tạo Ảnh", "🎬 Tạo Video (Sora/Veo)", "🎙️ Kịch Bản & Voice"], horizontal=True)
        st.divider()

        # 2.1 TẠO ẢNH
        if mode == "🖼️ Tạo Ảnh":
            desc = st.text_area("Mô tả ảnh muốn vẽ:", height=100)
            if st.button("🎨 Vẽ Ngay"):
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    prompt_en = model.generate_content(f"Translate to detailed English prompt for image generation: {desc}").text
                    final_url = f"https://image.pollinations.ai/prompt/{prompt_en.replace(' ', '%20')}?nologo=true"
                    st.image(final_url)
        
        # 2.2 TẠO VIDEO
        elif mode == "🎬 Tạo Video (Sora/Veo)":
            st.info("🔥 Chế độ này sẽ tạo Prompt Tiếng Anh chuẩn Hollywood cho Sora, Runway, Kling.")
            idea = st.text_area("Mô tả ý tưởng video (Tiếng Việt):", height=100)
            if st.button("🎥 Viết Prompt Chuẩn"):
                if idea:
                    with st.spinner("Đang thiết kế góc máy & ánh sáng..."):
                        model = genai.GenerativeModel(best_model)
                        sys_video = """
                        ACT AS: Expert AI Video Prompt Engineer.
                        TASK: Convert user idea into a HIGH-END VIDEO PROMPT.
                        RULES: 
                        1. OUTPUT ONLY ENGLISH.
                        2. Structure: [Subject] + [Action] + [Camera Movement] + [Lighting] + [Tech Specs].
                        3. Keywords required: 8k, cinematic, photorealistic, depth of field, slow motion, Unreal Engine 5.
                        """
                        res = model.generate_content(f"{sys_video}\nInput: {idea}").text
                        st.success("✅ Prompt (Copy dòng dưới để tạo video):")
                        st.code(res, language="text")
                else: st.warning("Nhập ý tưởng trước!")

        # 2.3 TẠO VOICE (NÂNG CẤP: TỐC ĐỘ & CẢM XÚC)
        elif mode == "🎙️ Kịch Bản & Voice":
            st.subheader("🎙️ Studio Giọng Nói AI")
            
            # Cấu hình giọng đọc
            c_config1, c_config2 = st.columns(2)
            with c_config1:
                # Chọn tốc độ đọc
                is_slow = st.checkbox("🐢 Chế độ đọc chậm rãi (Thích hợp kể chuyện/Tin buồn)", value=False)
            with c_config2:
                # Chọn cảm xúc kịch bản
                tone_style = st.selectbox("🎭 Cảm xúc chủ đạo:", 
                    ["Truyền cảm/Sâu lắng", "Vui tươi/Hài hước", "Nghiêm túc/Chính luận", "Hào hứng/Marketing", "Buồn/Tâm trạng"])

            v_type = st.radio("Loại kịch bản:", ["Độc thoại (Lời bình)", "Hội thoại (2 người)"], horizontal=True)
            
            # System Instruction ép AI viết theo cảm xúc
            sys_writer = "Bạn là biên kịch tài ba. Quy tắc: Hướng dẫn diễn xuất/âm thanh phải để trong ngoặc đơn (...). Lời thoại phải tự nhiên."
            model = genai.GenerativeModel(best_model, system_instruction=sys_writer)

            if v_type == "Độc thoại (Lời bình)":
                c1, c2 = st.columns(2)
                gender = c1.selectbox("Giới tính:", ["Nam", "Nữ"])
                region = c2.selectbox("Giọng:", ["Bắc (Chuẩn)", "Trung", "Nam"])
                
                topic = st.text_area("Nội dung cần đọc:")
                if st.button("🎙️ Viết & Đọc Ngay"):
                    if topic:
                        with st.spinner(f"Đang viết kịch bản với cảm xúc {tone_style}..."):
                            # Prompt ép AI viết theo Tone
                            prompt_script = f"""
                            Viết kịch bản lời bình ngắn.
                            - Vai: {gender}, Giọng: {region}.
                            - Phong cách/Cảm xúc: {tone_style} (Rất quan trọng, hãy dùng từ ngữ thể hiện đúng cảm xúc này).
                            - Chủ đề: {topic}.
                            """
                            res = model.generate_content(prompt_script).text
                            st.subheader("Kịch bản chi tiết:")
                            st.markdown(res)
                            st.divider()
                            # Gọi hàm đọc với tham số tốc độ
                            play_text_to_speech(res, speed_slow=is_slow)
            else:
                st.info("Hội thoại 2 người")
                topic = st.text_area("Chủ đề hội thoại:")
                if st.button("🗣️ Tạo & Đọc Hội Thoại"):
                    if topic:
                        with st.spinner(f"Đang viết hội thoại {tone_style}..."):
                            prompt_chat = f"""
                            Viết đoạn hội thoại ngắn giữa 2 người.
                            - Cảm xúc bao trùm: {tone_style}.
                            - Chủ đề: {topic}.
                            - Có tính tương tác cao, tự nhiên, dùng từ ngữ địa phương.
                            """
                            res = model.generate_content(prompt_chat).text
                            st.subheader("Kịch bản:")
                            st.markdown(res)
                            st.divider()
                            play_text_to_speech(res, speed_slow=is_slow)

    # -------------------------------------------------------------------------
    # MODULE 3: CÁC CHUYÊN GIA TƯ VẤN (CHATBOTS)
    # -------------------------------------------------------------------------
    else:
        st.header(menu)
        
        # Lấy System Instruction "xịn" từ hàm cấu hình ở trên
        expert_instruction = get_expert_system_instruction(menu)
        
        # Xử lý riêng cho Giáo Dục
        edu_append = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            c1, c2 = st.columns(2)
            sach = c1.selectbox("Bộ sách:", ["Cánh Diều", "Kết Nối Tri Thức", "Chân Trời Sáng Tạo"])
            role = c2.radio("Vai trò:", ["Học sinh", "Giáo viên"], horizontal=True)
            edu_append = f". Lưu ý: Đang dùng sách '{sach}'. Vai trò người hỏi: {role}."

        # Khởi tạo Chat History
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            # Lời chào mở đầu thông minh
            welcome_msg = "Xin chào! Tôi là chuyên gia trong lĩnh vực này với hơn 20 năm kinh nghiệm. Tôi có thể giúp gì cho bạn?"
            st.session_state.history[menu].append({"role": "assistant", "content": welcome_msg})

        # Hiển thị lịch sử chat
        for msg in st.session_state.history[menu]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Ô nhập liệu
        if prompt := st.chat_input("Nhập câu hỏi cho chuyên gia..."):
            with st.chat_message("user"):
                st.markdown(prompt)
                if file_content: st.caption("📎 [Đã đính kèm file]")
            st.session_state.history[menu].append({"role": "user", "content": prompt})

            # Xử lý trả lời
            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang phân tích..."):
                    try:
                        # Ghép Prompt + File + Edu Logic
                        full_prompt = [prompt + edu_append]
                        if file_content:
                            if isinstance(file_content, str): full_prompt.append(f"\n\nCONTEXT FILE:\n{file_content}")
                            else: full_prompt.append(file_content) # Nếu là ảnh

                        # Gọi Model với System Instruction chuyên sâu
                        model = genai.GenerativeModel(best_model, system_instruction=expert_instruction)
                        response = model.generate_content(full_prompt)
                        
                        st.markdown(response.text)
                        st.session_state.history[menu].append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi kết nối: {e}")
