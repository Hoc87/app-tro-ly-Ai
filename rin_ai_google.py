import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai Ecosystem", page_icon="🌌", layout="wide")

# --- HÀM TỰ ĐỘNG CHỌN MODEL ---
@st.cache_resource
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except:
        return None
    # Ưu tiên tìm 2.5 -> Flash -> Pro
    priority = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
    for p in priority:
        for m in available_models:
            if p in m: return m
    return "gemini-pro"

# --- SIDEBAR: CẤU HÌNH & MENU CÔNG CỤ ---
with st.sidebar:
    st.title("🌌 HỆ SINH THÁI RIN.AI")
    
    # 1. Nhập Key
    st.subheader("1. Cấu hình Key")
    key_mode = st.radio("Nguồn Key:", ["🚀 Dùng thử (Thầy)", "🔑 Cá nhân"], horizontal=True)
    
    final_key = None
    if key_mode == "🚀 Dùng thử (Thầy)":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Key hệ thống")
        except:
            st.error("❌ Chưa có Key trong Secrets")
    else:
        final_key = st.text_input("Dán API Key của bạn:", type="password")
        if final_key: st.success("✅ Đã nhận Key cá nhân")

    st.divider()
    
    # 2. MENU CHỌN CÔNG CỤ (TRÁI TIM CỦA APP)
    st.subheader("2. Chọn Công Cụ AI")
    selected_tool = st.radio(
        "Bạn muốn làm gì hôm nay?",
        [
            "🏠 Trang chủ Dashboard",
            "✍️ Viết Content Marketing",
            "💰 Chuyên Gia Bán Hàng",
            "🎨 Tạo Prompt Ảnh (Midjourney)",
            "🎬 Viết Kịch Bản Video Ngắn",
            "🇬🇧 Gia Sư Tiếng Anh"
        ]
    )
    
    st.info("Mỗi công cụ sẽ kích hoạt một trợ lý AI chuyên biệt.")

# --- NỘI DUNG CHÍNH (THAY ĐỔI THEO MENU) ---

# Nếu chưa có Key thì dừng lại
if not final_key:
    st.warning("👉 Vui lòng cấu hình API Key ở cột bên trái để bắt đầu.")
    st.stop()

# Cấu hình AI chung
model_name = get_best_model(final_key)
genai.configure(api_key=final_key)

# --- XỬ LÝ TỪNG CÔNG CỤ ---

if selected_tool == "🏠 Trang chủ Dashboard":
    st.title("👋 Chào mừng đến với Rin.Ai Workspace")
    st.markdown("""
    Đây là bộ công cụ AI "Tất cả trong một" giúp bạn tăng tốc độ làm việc gấp 10 lần.
    
    ### 👈 Hãy chọn một công cụ bên tay trái:
    
    * **✍️ Marketing:** Viết bài Facebook, Blog, Email siêu cuốn.
    * **💰 Bán hàng:** Xử lý từ chối, kịch bản telesale.
    * **🎨 Tạo ảnh:** Viết mô tả chi tiết để vẽ tranh (Prompt Engineering).
    * **🎬 Video:** Kịch bản TikTok, YouTube Short triệu view.
    """)
    st.image("https://source.unsplash.com/random/800x400/?technology,ai", caption="Sức mạnh AI trong tay bạn")

else:
    # Thiết lập "NÃO" (System Instruction) cho từng chuyên gia
    system_prompts = {
        "✍️ Viết Content Marketing": """
            Bạn là một Chuyên gia Marketing hàng đầu với 10 năm kinh nghiệm (Copywriter).
            Phong cách viết: Sôi nổi, hấp dẫn, dùng nhiều icon, đánh trúng nỗi đau khách hàng.
            Nhiệm vụ: Viết bài quảng cáo, bài đăng Facebook, Email marketing.
            Luôn chia bài viết thành các phần: Tiêu đề giật gân, Nỗi đau, Giải pháp, Kêu gọi hành động (CTA).
        """,
        "💰 Chuyên Gia Bán Hàng": """
            Bạn là một "Sát thủ" bán hàng (Sales Master).
            Nhiệm vụ: Giúp người dùng xử lý từ chối, viết kịch bản chốt sale.
            Phong cách: Khéo léo, thấu hiểu tâm lý, thuyết phục nhưng không ép buộc.
            Hãy đưa ra các mẫu câu đối thoại cụ thể.
        """,
        "🎨 Tạo Prompt Ảnh (Midjourney)": """
            Bạn là một Chuyên gia Prompt Engineering cho các AI vẽ tranh (Midjourney, Stable Diffusion).
            Nhiệm vụ: Người dùng sẽ đưa ý tưởng sơ sài, bạn hãy viết lại thành một đoạn Prompt tiếng Anh chi tiết.
            Cấu trúc Prompt: [Chủ thể] + [Môi trường] + [Phong cách nghệ thuật] + [Ánh sáng/Màu sắc] + [Tỷ lệ khung hình --ar 16:9].
            Chỉ trả về Prompt tiếng Anh và phần giải thích tiếng Việt ngắn gọn.
        """,
        "🎬 Viết Kịch Bản Video Ngắn": """
            Bạn là Đạo diễn kiêm Biên kịch TikTok/Reels triệu view.
            Nhiệm vụ: Viết kịch bản video ngắn 30-60s.
            Yêu cầu: Phải chia dạng bảng gồm 2 cột: [Hình ảnh/Hành động] và [Lời thoại/Âm thanh].
            Bắt đầu bằng 3 giây đầu gây sốc (Hook).
        """,
        "🇬🇧 Gia Sư Tiếng Anh": """
            Bạn là giáo viên IELTS 8.5. Nhiệm vụ: Sửa lỗi ngữ pháp, dịch thuật và giải thích từ vựng cho người dùng.
        """
    }
    
    # Lấy System Prompt tương ứng
    current_instruction = system_prompts.get(selected_tool, "Bạn là trợ lý AI hữu ích.")
    
    # Hiển thị giao diện công cụ
    st.header(selected_tool)
    
    # Khởi tạo model với "NÃO" chuyên biệt
    model = genai.GenerativeModel(model_name, system_instruction=current_instruction)
    
    # Quản lý lịch sử chat riêng cho từng công cụ (để không bị lẫn lộn)
    session_key = f"history_{selected_tool}"
    if session_key not in st.session_state:
        st.session_state[session_key] = []

    # Hiển thị lịch sử
    for msg in st.session_state[session_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Ô nhập liệu
    placeholder_text = {
        "✍️ Viết Content Marketing": "Nhập chủ đề bài viết (VD: Bán nước hoa cho nam giới...)",
        "💰 Chuyên Gia Bán Hàng": "Nhập tình huống khó (VD: Khách chê giá đắt...)",
        "🎨 Tạo Prompt Ảnh (Midjourney)": "Mô tả bức tranh bạn muốn vẽ (VD: Mèo máy Doraemon phiên bản thực...)",
        "🎬 Viết Kịch Bản Video Ngắn": "Chủ đề video (VD: Hướng dẫn nấu ăn nhanh...)",
        "🇬🇧 Gia Sư Tiếng Anh": "Nhập đoạn văn cần sửa hoặc từ cần tra..."
    }
    
    if prompt := st.chat_input(placeholder_text.get(selected_tool, "Nhập nội dung...")):
        # Hiện câu hỏi
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state[session_key].append({"role": "user", "content": prompt})
        
        # AI trả lời
        with st.chat_message("assistant"):
            with st.spinner("Đang xử lý..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state[session_key].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Lỗi: {e}")
