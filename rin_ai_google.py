import streamlit as st
import google.generativeai as genai
import os

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Rin.Ai Google", page_icon="🤖")
st.title("✨ Rin.Ai Google")

# --- LOGIC XỬ LÝ API KEY ---
# 1. Lấy Key mặc định (nếu bạn có cài trong Secrets - dành cho Thầy test)
try:
    default_api_key = st.secrets["GOOGLE_API_KEY"]
except:
    default_api_key = ""

# 2. Giao diện nhập Key (Dành cho Học viên)
with st.expander("⚙️ Cài đặt (Nhập API Key của bạn)"):
    st.info("Để sử dụng miễn phí và không giới hạn, hãy nhập API Key của bạn.")
    user_api_key = st.text_input("Nhập Google API Key:", type="password")
    st.markdown("[Bấm vào đây để lấy Key miễn phí](https://aistudio.google.com/)")

# 3. Quyết định dùng Key nào
if user_api_key:
    final_key = user_api_key
    st.success("✅ Đang sử dụng Key của bạn.")
elif default_api_key:
    final_key = default_api_key
    st.info("ℹ️ Đang sử dụng Key hệ thống.")
else:
    final_key = None
    st.warning("⚠️ Vui lòng nhập API Key để bắt đầu.")

# --- PHẦN CHAT ---
if final_key:
    try:
        genai.configure(api_key=final_key)
        # Dùng model Flash cho nhanh
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Khung chat
        user_input = st.text_area("Nhập nội dung cần Rin.Ai hỗ trợ:", height=120)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_btn = st.button("🚀 Gửi")
            
        if submit_btn:
            if user_input:
                with st.spinner("Rin.Ai đang suy nghĩ..."):
                    try:
                        response = model.generate_content(user_input)
                        st.markdown("### Kết quả:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Lỗi kết nối: {e}")
            else:
                st.warning("Bạn chưa nhập nội dung!")
    except:
        st.error("API Key không hợp lệ.")
