import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai Google", page_icon="✨")
st.title("✨ Rin.Ai Google")
st.caption("Trợ lý AI Tự Động Chọn Model - Enter là gửi!")

# --- THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Cấu hình")
    option = st.radio(
        "Chọn chế độ:",
        ["🚀 Dùng thử miễn phí", "🔑 Dùng Key cá nhân"],
        index=0
    )
    st.divider()
    st.markdown("Dev by **Học Viện Rin.Ai**")

# --- HÀM THÔNG MINH: TỰ ĐỘNG CHỌN MODEL TỐT NHẤT ---
@st.cache_resource
def get_best_model(api_key):
    """Hàm này tự động dò tìm model xịn nhất có trong tài khoản"""
    genai.configure(api_key=api_key)
    
    # 1. Lấy danh sách tất cả model
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except:
        return None

    # 2. Quy tắc ưu tiên: Tìm 2.5 -> 2.0 -> 1.5 -> Flash -> Pro
    priority_keywords = [
        "gemini-2.5-flash", 
        "gemini-2.0-flash", 
        "gemini-1.5-flash", 
        "gemini-flash",     # Các bản flash chung
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    # Dò tìm theo thứ tự ưu tiên
    for keyword in priority_keywords:
        for model_name in available_models:
            if keyword in model_name:
                return model_name
    
    # 3. Nếu không tìm thấy cái nào trong ưu tiên, lấy cái Gemini đầu tiên tìm được
    for model_name in available_models:
        if "gemini" in model_name:
            return model_name
            
    return "gemini-pro" # Phương án cuối cùng (Fallback)

# --- XỬ LÝ KEY ---
final_key = None
if option == "🚀 Dùng thử miễn phí":
    try:
        final_key = st.secrets["GOOGLE_API_KEY"]
    except:
        st.error("❌ Giảng viên chưa cài Key vào Secrets.")
else:
    user_api_key = st.text_input("🔑 Nhập API Key của bạn:", type="password")
    if user_api_key:
        final_key = user_api_key

# --- LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- PHẦN XỬ LÝ CHAT ---
if final_key:
    try:
        # Gọi hàm tự động chọn model
        best_model_name = get_best_model(final_key)
        
        if best_model_name:
            # Hiển thị tên model đang dùng (để bạn biết nó chọn cái nào)
            st.toast(f"🤖 Đang sử dụng động cơ: {best_model_name}", icon="✅")
            
            genai.configure(api_key=final_key)
            model = genai.GenerativeModel(best_model_name)

            if prompt := st.chat_input("Nhập câu hỏi rồi Enter..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                with st.chat_message("assistant"):
                    with st.spinner("Rin.Ai đang suy nghĩ..."):
                        try:
                            response = model.generate_content(prompt)
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
        else:
            st.error("Không tìm thấy model phù hợp trong Key này.")
            
    except Exception as e:
        st.error(f"Lỗi cấu hình: {e}")
