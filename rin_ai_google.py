import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Kiểm tra Model", page_icon="🛠️")
st.title("🛠️ CÔNG CỤ KIỂM TRA MODEL")

# 1. Lấy Key
try:
    # Thử lấy từ Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ Đã tìm thấy Key trong Két sắt.")
except:
    st.warning("⚠️ Chưa có Key trong Secrets.")
    api_key = st.text_input("Nhập Key của bạn vào đây để test:", type="password")

# 2. Kiểm tra
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        st.write("⏳ Đang kết nối với Google để lấy danh sách...")
        
        # Lệnh liệt kê tất cả model
        found_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                found_models.append(m.name)
        
        if found_models:
            st.success(f"🎉 Thành công! Tìm thấy {len(found_models)} model khả dụng:")
            st.divider()
            for name in found_models:
                # Hiển thị tên model dạng Code để bạn copy
                st.code(name)
                # Gợi ý model nên dùng
                if "gemini" in name:
                    st.caption("👆 Đây là model Gemini!")
        else:
            st.error("❌ Kết nối thành công nhưng không tìm thấy model nào. Có thể Key bị hạn chế.")
            
    except Exception as e:
        st.error(f"❌ Lỗi kết nối nghiêm trọng: {e}")
        st.info("Gợi ý: Hãy kiểm tra lại file requirements.txt xem đã có dòng 'google-generativeai>=0.8.3' chưa.")
