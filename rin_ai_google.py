import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import re
import requests 
from PIL import Image
import PyPDF2
import pandas as pd

# --- IMPORT FILE PROMPTS (GỌI TRỢ LÝ TỪ FILE BÊN KIA) ---
from prompts import get_expert_prompt

# =============================================================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ
# =============================================================================

st.set_page_config(page_title="Rin.Ai - Siêu Trợ Lý AI", page_icon="💎", layout="wide")

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

def clean_text_for_tts(text):
    if not text: return ""
    clean = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', text, flags=re.DOTALL)
    clean = re.sub(r'\([^)]*\)', '', clean)
    clean = re.sub(r'\[[^]]*\]', '', clean)
    clean = clean.replace('*', '').replace('#', '').replace('`', '')
    return clean.strip()

def play_text_to_speech(text_content, speed_slow=False):
    try:
        text_to_read = clean_text_for_tts(text_content)
        if len(text_to_read) < 5: return
        tts = gTTS(text=text_to_read, lang='vi', slow=speed_slow)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes, format='audio/mp3')
        status = "🐢 Đang đọc chậm..." if speed_slow else "🐇 Đang đọc tốc độ thường..."
        st.caption(f"🔊 {status}")
    except: pass

def generate_image_url(prompt):
    clean_prompt = prompt.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?nologo=true&model=turbo"

@st.cache_resource
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        for p in priority:
            for m in models:
                if p in m: return m
        return "gemini-pro"
    except: return None

# =============================================================================
# 2. GIAO DIỆN CHÍNH
# =============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222588.png", width=80)
    st.title("RIN.AI PRO")
    st.caption("Developed by Mr. Học")
    st.divider()
    
    # --- KEY ---
    st.subheader("🔑 Tài khoản sử dụng")
    key_option = st.radio("Chế độ:", ["🚀 Dùng Miễn Phí", "💎 Nhập Key Của Bạn"], label_visibility="collapsed")
    final_key = None
    if key_option == "🚀 Dùng Miễn Phí":
        try:
            final_key = st.secrets["GOOGLE_API_KEY"]
            st.success("✅ Đã kết nối Server")
        except: st.error("❌ Chưa cấu hình Key chung")
    else: 
        st.info("Nhập Google API Key của bạn:")
        final_key = st.text_input("API Key:", type="password")
        if final_key: st.success("✅ Đã nhận Key")
    
    st.divider()

    # --- LIÊN KẾT NGOÀI ---
    st.info("🤖 AI Nâng Cao & ChatGPT")
    st.link_button("👉 Trợ Lý ChatGPT (App Riêng)", "https://chatgpt.com/") 
    st.divider()
    
    st.subheader("🌐 Hệ Sinh Thái Google AI")
    with st.expander("Mở công cụ Google"):
        st.link_button("📚 NotebookLM (Tài liệu)", "https://notebooklm.google.com/")
        st.link_button("🛠️ Google AI Studio", "https://aistudio.google.com/")
        st.link_button("🎨 ImageFX (Tạo ảnh)", "https://aitestkitchen.withgoogle.com/tools/image-fx")
        st.link_button("🎥 VideoFX (Tạo Video)", "https://aitestkitchen.withgoogle.com/tools/video-fx")
    
    st.divider()
    
    # --- UPLOAD ---
    st.subheader("📎 Tài liệu đính kèm")
    uploaded_file = st.file_uploader("Upload...", type=['png', 'jpg', 'pdf', 'txt', 'csv', 'xlsx'], label_visibility="collapsed")
    file_content = process_uploaded_file(uploaded_file)
    if file_content: st.info(f"✅ Đã đọc: {uploaded_file.name}")
    
    st.divider()

    # 3. MENU CHỨC NĂNG (ĐÃ SỬA LỖI DÍNH DÒNG)
    st.subheader("📂 Chọn Chuyên Gia")
    menu = st.radio("Lĩnh vực:", [
        "🏠 Trang Chủ & Giới Thiệu", 
        "✨ Trợ Lý Đa Lĩnh Vực (Chung)",
        "🏛️ Dịch Vụ Hành Chính Công",
        "🏛️ Trợ Lý Cán bộ Ủy ban (Xã/Phường/TP)", # <--- NHỚ DẤU PHẨY NÀY
        "🏗️ Kiến Trúc - Nội Thất - Xây Dựng",     # <--- ĐÃ TÁCH RA THÀNH DÒNG RIÊNG
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

# --- LOGIC ---

if menu == "🏠 Trang Chủ & Giới Thiệu":
    st.title("💎 Hệ Sinh Thái AI Thực Chiến - Rin.Ai")
    st.markdown("""
    ### 🚀 Rin.Ai - Super App Đa Phương Tiện
    Chào mừng bạn đến với phiên bản Rin.Ai PRO.
    * **Kiến Trúc Sư AI:** Tự vẽ 2D/3D.
    * **Trợ Lý Ủy Ban:** Soạn thảo văn bản chuẩn Nghị định 30.
    * **Media Pro:** Tạo Prompt Video & Voice AI cảm xúc.
    
    ---
    ### 👨‍🏫 Liên hệ đào tạo & Hợp tác:
    ## **Mr. Học** - 📞 Hotline/Zalo: **0901 108 788**
    """)

elif not final_key:
    st.warning("👋 Vui lòng nhập Key bên tay trái để bắt đầu.")
    st.stop()

else:
    best_model = get_best_model(final_key)
    genai.configure(api_key=final_key)

    # 1. MODULE TIN TỨC
    if menu == "📰 Đọc Báo & Tóm Tắt Sách":
        st.header("📰 Chuyên Gia Tri Thức")
        task = st.radio("Chế độ:", ["🔎 Tin Tức", "📚 Tóm tắt Sách"], horizontal=True)
        if task == "🔎 Tin Tức":
            topic = st.text_input("Chủ đề:")
            if st.button("🔎 Tổng hợp"):
                with st.spinner("Đang xử lý..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Tổng hợp tin tức mới nhất về: {topic}").text
                    st.markdown(res)
                    play_text_to_speech(res)
        else:
            txt = st.text_area("Văn bản:")
            inp = file_content if file_content else txt
            if st.button("📚 Tóm tắt") and inp:
                with st.spinner("Đang đọc..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Tóm tắt: {inp}").text
                    st.markdown(res)
                    play_text_to_speech(res)

    # 2. MODULE MEDIA
    elif menu == "🎨 Thiết Kế & Media (Ảnh/Video/Voice)":
        st.header("🎨 Studio Đa Phương Tiện")
        mode = st.radio("Công cụ:", ["🖼️ Tạo Ảnh", "🎬 Tạo Video", "🎙️ Voice AI"], horizontal=True)
        
        if mode == "🖼️ Tạo Ảnh":
            desc = st.text_area("Mô tả ảnh:")
            if st.button("🎨 Vẽ"):
                with st.spinner("Đang vẽ..."):
                    model = genai.GenerativeModel(best_model)
                    p_en = model.generate_content(f"Translate to English prompt: {desc}").text
                    st.image(generate_image_url(p_en))
        
        elif mode == "🎬 Tạo Video":
            idea = st.text_area("Ý tưởng video:")
            if st.button("🎥 Tạo Prompt"):
                model = genai.GenerativeModel(best_model)
                p = model.generate_content(f"Create English Video Prompt (Sora/Runway) for: {idea}. Structure: [Subject] [Movement] [Style]").text
                st.code(p)

        elif mode == "🎙️ Voice AI":
            c1, c2 = st.columns(2)
            is_slow = c1.checkbox("🐢 Đọc chậm", value=False)
            tone = c2.selectbox("Cảm xúc:", ["Truyền cảm", "Vui tươi", "Nghiêm túc", "Hào hứng", "Buồn"])
            topic = st.text_area("Nội dung:")
            if st.button("🎙️ Tạo & Đọc"):
                with st.spinner("Đang xử lý..."):
                    model = genai.GenerativeModel(best_model)
                    res = model.generate_content(f"Viết kịch bản ngắn. Cảm xúc: {tone}. Chủ đề: {topic}. Ghi chú diễn xuất trong ngoặc đơn.").text
                    st.markdown(res)
                    play_text_to_speech(res, is_slow)

    # 3. MODULE CHUYÊN GIA (CHATBOTS) - GỌI TỪ FILE PROMPTS
    else:
        st.header(menu)
        
        # --- GỌI HÀM LẤY PROMPT TỪ FILE PROMPTS.PY ---
        expert_instruction = get_expert_prompt(menu)
        
        # Logic Giáo dục
        edu_append = ""
        if menu == "🎓 Giáo Dục & Đào Tạo":
            sach = st.selectbox("Sách:", ["Cánh Diều", "KNTT", "CTST"])
            edu_append = f". Sách: {sach}."

        # Chat History
        if "history" not in st.session_state: st.session_state.history = {}
        if menu not in st.session_state.history:
            st.session_state.history[menu] = []
            st.session_state.history[menu].append({"role": "assistant", "content": "Xin chào! Tôi là chuyên gia lĩnh vực này. Tôi có thể giúp gì cho bạn?"})

        # Hiện lịch sử (Text clean)
        for msg in st.session_state.history[menu]:
             if msg["role"] == "user":
                 with st.chat_message("user"): st.markdown(msg["content"])
             else:
                 clean_show = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', msg["content"], flags=re.DOTALL)
                 if clean_show.strip():
                     with st.chat_message("assistant"): st.markdown(clean_show)

        # Input mới
        if prompt := st.chat_input("Nhập câu hỏi..."):
            with st.chat_message("user"):
                st.markdown(prompt)
                if file_content: st.caption("📎 [Có file]")
            st.session_state.history[menu].append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Chuyên gia đang trả lời..."):
                    try:
                        full_p = [prompt + edu_append]
                        if file_content: full_p.append(f"FILE:\n{file_content}")
                        
                        model = genai.GenerativeModel(best_model, system_instruction=expert_instruction)
                        response = model.generate_content(full_p)
                        full_txt = response.text

                        # Tách ảnh & Text
                        p2d = re.search(r'###PROMPT_2D###(.*?)###END_PROMPT###', full_txt, re.DOTALL)
                        p3d = re.search(r'###PROMPT_3D###(.*?)###END_PROMPT###', full_txt, re.DOTALL)
                        txt_show = re.sub(r'###PROMPT_[23]D###.*?###END_PROMPT###', '', full_txt, flags=re.DOTALL)
                        
                        st.markdown(txt_show.strip())
                        
                        if p2d or p3d:
                            st.divider()
                            c_a, c_b = st.columns(2)
                            if p2d:
                                with c_a: st.image(generate_image_url("Blueprint. " + p2d.group(1)), caption="Bản vẽ 2D")
                            if p3d:
                                with c_b: st.image(generate_image_url("Architecture render. " + p3d.group(1)), caption="Phối cảnh 3D")
                        
                        st.session_state.history[menu].append({"role": "assistant", "content": full_txt})
                    except Exception as e: st.error(f"Lỗi: {e}")
