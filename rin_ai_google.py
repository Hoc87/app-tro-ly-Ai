import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai - Trợ Lý Đa Năng", page_icon="✨", layout="wide")

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

    # 2. MENU CHỨC NĂNG (Thêm trang chủ lên đầu)
    menu = st.radio(
        "📂 DANH MỤC:",
        [
            "🏠 Giới Thiệu & Liên Hệ",  # <-- TRANG CHỦ MỚI
            "🎨 Xưởng Sáng Tạo (Tạo Ảnh)",
            "💰 Kinh Doanh Online & Affiliate",
            "🏢 Góc Chủ Doanh Nghiệp (CEO)",
            "🍎 Trợ Lý Giáo Viên & Giáo Án",
            "🤖 Trợ Lý Đời Sống (Đa Năng)"
        ]
    )

# --- NỘI DUNG CHÍNH ---

# Logic kiểm tra Key (Trừ trang giới thiệu ra thì các trang khác cần Key)
if menu != "🏠 Giới Thiệu & Liên Hệ" and not final_key:
    st.warning("👉 Vui lòng nhập API Key bên tay trái để sử dụng tính năng này.")
    st.stop()

if final_key:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

# ==============================================================================
# TRANG CHỦ: GIỚI THIỆU (THEO YÊU CẦU CỦA BẠN)
# ==============================================================================
if menu == "🏠 Giới Thiệu & Liên Hệ":
    st.title("👋 Xin chào, tôi là Rin.Ai")
    
    st.markdown("""
    ### 🌟 Giới thiệu chung
    **Rin.Ai** là một công cụ AI đa lĩnh vực dựa trên hệ sinh thái mạnh mẽ của Google (Gemini), được thiết kế để trở thành trợ lý đắc lực cho mọi nhu cầu.
    
    ---
    ### 👨‍🏫 Về Tác Giả & Nhà Phát Triển
    Ứng dụng được xây dựng và phát triển trực tiếp bởi:
    
    ## **Chuyên gia: Mr. Học**
    #### 📞 Hotline/Zalo: **0901 108 788**
    
    > *Chuyên gia đào tạo và hướng dẫn ứng dụng AI cho Doanh nghiệp và Cá nhân trong mọi lĩnh vực công việc và đời sống.*
    
    ---
    ### 🚀 Rin.Ai có thể giúp gì cho bạn?
    Hãy chọn một công cụ ở menu bên tay trái để bắt đầu:
    
    * **🎨 Xưởng Sáng Tạo:** Vẽ tranh AI, tạo ý tưởng thiết kế.
    * **💰 Kinh Doanh:** Viết bài quảng cáo, kịch bản Livestream, Affiliate.
    * **🏢 Doanh Nghiệp:** Tư vấn chiến lược, nhân sự, quản trị.
    * **🍎 Giáo Dục:** Soạn giáo án, đề thi, phương pháp dạy học.
    * **🤖 Đời Sống:** Trợ lý ảo đa năng giải đáp mọi thắc mắc.
    """)
    
    st.info("👈 **Hãy chọn một chức năng bên thanh menu trái để bắt đầu làm việc!**")

# ==============================================================================
# CHỨC NĂNG 1: XƯỞNG SÁNG TẠO (VẼ ẢNH TRỰC TIẾP)
# ==============================================================================
elif menu == "🎨 Xưởng Sáng Tạo (Tạo Ảnh)":
    st.header("🎨 Xưởng Vẽ Tranh AI & Tạo Prompt")
    mode = st.selectbox("Chọn chế độ:", ["🖼️ Vẽ ảnh trực tiếp (Miễn phí)", "📝 Viết Prompt Midjourney"])
    
    if mode == "🖼️ Vẽ ảnh trực tiếp (Miễn phí)":
        img_desc = st.text_area("Mô tả bức tranh bạn muốn vẽ:", height=100)
        if st.button("🎨 Vẽ Ngay"):
            if img_desc:
                with st.spinner("Đang vẽ tranh..."):
                    model = genai.GenerativeModel(best_model)
                    trans_prompt = model.generate_content(f"Translate to English for Image Gen: {img_desc}").text
                    final_prompt = trans_prompt.replace(" ", "%20")
                    st.image(f"https://image.pollinations.ai/prompt/{final_prompt}?nologo=true", caption="Kết quả từ Rin.Ai")
    else:
        model = genai.GenerativeModel(best_model, system_instruction="Bạn là Chuyên gia Prompt. Hãy viết prompt tiếng Anh chi tiết cho Midjourney.")
        prompt_req = st.text_area("Ý tưởng của bạn:")
        if st.button("📝 Sinh Prompt"):
            st.code(model.generate_content(prompt_req).text)

# ==============================================================================
# CÁC CHỨC NĂNG KHÁC (CHATBOT CHUYÊN GIA)
# ==============================================================================
else:
    # Định nghĩa System Prompt
    personas = {
        "💰 Kinh Doanh Online & Affiliate": "Bạn là Chuyên gia E-commerce & Copywriter thực chiến. Giúp viết content bán hàng, kịch bản live, tư vấn Affiliate.",
        "🏢 Góc Chủ Doanh Nghiệp (CEO)": "Bạn là Cố vấn Chiến lược Doanh nghiệp. Tư vấn quản trị, nhân sự, tài chính, KPI chuyên nghiệp.",
        "🍎 Trợ Lý Giáo Viên & Giáo Án": "Bạn là Chuyên gia Giáo dục. Hỗ trợ soạn giáo án, đề thi, phương pháp sư phạm.",
        "🤖 Trợ Lý Đời Sống (Đa Năng)": "Bạn là Trợ lý ảo thân thiện, biết tuốt mọi thứ."
    }

    st.header(menu)
    
    # Quản lý lịch sử chat
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    if menu not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[menu] = []

    for msg in st.session_state.chat_sessions[menu]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Xử lý Chat
    model = genai.GenerativeModel(best_model, system_instruction=personas.get(menu))
    
    if prompt := st.chat_input(f"Nhập câu hỏi cho {menu}..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_sessions[menu].append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Đang xử lý..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.chat_sessions[menu].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Lỗi: {e}")
