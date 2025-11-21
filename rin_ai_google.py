import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai Google", page_icon="✨")
st.title("✨ Rin.Ai Google")
st.caption("Trợ lý AI thông minh - Enter là gửi!")

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

# --- XỬ LÝ LOGIC KEY ---
final_key = None

if option == "🚀 Dùng thử miễn phí":
    try:
        final_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Đang dùng chế độ Dùng Thử.")
    except:
        st.error("❌ Giảng viên chưa cài Key vào Secrets.")
else:
    st.markdown("### 🔑 Nhập API Key")
    user_api_key = st.text_input("Dán Key vào đây:", type="password")
    if user_api_key:
        final_key = user_api_key
        st.success("✅ Đã nhận Key cá nhân.")

# --- LỊCH SỬ CHAT (Để lưu tin nhắn cũ trên màn hình) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lại các tin nhắn cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- PHẦN XỬ LÝ CHAT CHÍNH (QUAN TRỌNG) ---
if final_key:
    try:
        genai.configure(api_key=final_key)
        # Dùng gemini-pro cho ổn định (hoặc flash nếu bạn đã fix xong requirements)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # 🌟 ĐÂY LÀ CHỖ THAY ĐỔI: Dùng st.chat_input (Enter là gửi)
        if prompt := st.chat_input("Nhập câu hỏi ở đây rồi Enter..."):
            
            # 1. Hiển thị tin nhắn người dùng ngay lập tức
            with st.chat_message("user"):
                st.markdown(prompt)
            # Lưu vào lịch sử
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 2. AI suy nghĩ và trả lời
            with st.chat_message("assistant"):
                with st.spinner("Rin.Ai đang soạn tin..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        # Lưu câu trả lời vào lịch sử
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
                        
    except Exception as e:
        st.error(f"Lỗi cấu hình Key: {e}")
