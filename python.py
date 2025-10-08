import streamlit as st
import pandas as pd
from google import genai
from google.genai.errors import APIError

# --- Cấu hình Trang Streamlit ---
st.set_page_config(
    page_title="Phân Tích Báo Cáo Tài Chính - TrungDev x Agribank",
    layout="wide"
)
import streamlit.components.v1 as components

# --- Chức năng 6: Chat nổi dạng bong bóng và cửa sổ di chuyển ---
st.subheader("6. Chat nổi với Gemini 💬")

components.html("""
<style>
  #chatBubble {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background-color: #9E1B32;
    border-radius: 50%;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    cursor: move;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 28px;
    font-weight: bold;
    user-select: none;
  }

  #chatWindow {
    position: fixed;
    bottom: 100px;
    right: 30px;
    width: 350px;
    height: 450px;
    background: rgba(255,255,255,0.95);
    border: 2px solid #9E1B32;
    border-radius: 15px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    z-index: 9998;
    display: none;
    flex-direction: column;
    overflow: hidden;
    backdrop-filter: blur(8px);
    user-select: none;
  }

  #chatHeader {
    background-color: #9E1B32;
    color: white;
    padding: 10px;
    font-weight: bold;
    text-align: center;
    cursor: move;
  }

  #chatBody {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    font-size: 14px;
  }

  #chatInput {
    padding: 10px;
    border-top: 1px solid #ccc;
    display: flex;
  }

  #chatInput input {
    flex: 1;
    padding: 8px;
    border: 1px solid #9E1B32;
    border-radius: 5px;
  }

  #chatInput button {
    margin-left: 8px;
    background-color: #9E1B32;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
  }

  #chatInput button:hover {
    background-color: #00703C;
  }
</style>

<div id="chatBubble" onclick="toggleChat()">💬</div>

<div id="chatWindow">
  <div id="chatHeader">Gemini Chat</div>
  <div id="chatBody">
    <p><i>Xin chào! Bạn muốn hỏi gì hôm nay?</i></p>
  </div>
  <div id="chatInput">
    <input type="text" id="userInput" placeholder="Nhập câu hỏi...">
    <button onclick="sendMessage()">Gửi</button>
  </div>
</div>

<script>
  // Toggle chat window
  function toggleChat() {
    const chatWindow = document.getElementById("chatWindow");
    chatWindow.style.display = chatWindow.style.display === "none" ? "flex" : "none";
  }

  // Gửi tin nhắn
  function sendMessage() {
    const input = document.getElementById("userInput");
    const chatBody = document.getElementById("chatBody");
    const userText = input.value.trim();
    if (userText === "") return;

    const userMsg = document.createElement("p");
    userMsg.innerHTML = "<b>Bạn:</b> " + userText;
    chatBody.appendChild(userMsg);

    const aiMsg = document.createElement("p");
    aiMsg.innerHTML = "<b>Gemini:</b> Đang xử lý câu hỏi...";
    chatBody.appendChild(aiMsg);

    input.value = "";
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // Di chuyển cửa sổ chat
  makeDraggable("chatWindow", "chatHeader");
  makeDraggable("chatBubble", null);

  function makeDraggable(elementId, handleId) {
    const el = document.getElementById(elementId);
    const handle = handleId ? document.getElementById(handleId) : el;
    let offsetX = 0, offsetY = 0, isDragging = false;

    handle.addEventListener("mousedown", function(e) {
      isDragging = true;
      offsetX = e.clientX - el.getBoundingClientRect().left;
      offsetY = e.clientY - el.getBoundingClientRect().top;
      document.body.style.userSelect = "none";
    });

    document.addEventListener("mouseup", function() {
      isDragging = false;
      document.body.style.userSelect = "auto";
    });

    document.addEventListener("mousemove", function(e) {
      if (isDragging) {
        el.style.left = (e.clientX - offsetX) + "px";
        el.style.top = (e.clientY - offsetY) + "px";
        el.style.right = "auto";
        el.style.bottom = "auto";
      }
    });
  }
</script>
""", height=600)
# --- Tuỳ chỉnh giao diện Agribank ---
st.markdown("""
    <style>
        .main {
            background-color: #ffffff;
        }
        h1 {
            color: #9E1B32;
            font-size: 36px;
            font-weight: bold;
        }
        h2, h3 {
            color: #00703C;
        }
        div.stButton > button {
            background-color: #9E1B32;
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #00703C;
            color: white;
        }
        .chatbox {
            background-color: #f9f9f9;
            border: 2px solid #00703C;
            padding: 1em;
            border-radius: 10px;
        }
        textarea {
            border: 1px solid #9E1B32 !important;
        }
        .stSpinner > div > div {
            color: #9E1B32 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Phân Tích Báo Cáo Tài Chính 📊")

@st.cache_data
def process_financial_data(df):
    numeric_cols = ['Năm trước', 'Năm sau']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Tốc độ tăng trưởng (%)'] = (
        (df['Năm sau'] - df['Năm trước']) / df['Năm trước'].replace(0, 1e-9)
    ) * 100

    tong_tai_san_row = df[df['Chỉ tiêu'].str.contains('TỔNG CỘNG TÀI SẢN', case=False, na=False)]
    if tong_tai_san_row.empty:
        raise ValueError("Không tìm thấy chỉ tiêu 'TỔNG CỘNG TÀI SẢN'.")

    tong_tai_san_N_1 = tong_tai_san_row['Năm trước'].iloc[0]
    tong_tai_san_N = tong_tai_san_row['Năm sau'].iloc[0]

    divisor_N_1 = tong_tai_san_N_1 if tong_tai_san_N_1 != 0 else 1e-9
    divisor_N = tong_tai_san_N if tong_tai_san_N != 0 else 1e-9

    df['Tỷ trọng Năm trước (%)'] = (df['Năm trước'] / divisor_N_1) * 100
    df['Tỷ trọng Năm sau (%)'] = (df['Năm sau'] / divisor_N) * 100

    return df

def get_ai_analysis(data_for_ai, api_key):
    try:
        client = genai.Client(api_key=api_key)
        model_name = 'gemini-2.5-flash'

        prompt = f"""
        Bạn là một chuyên gia phân tích tài chính chuyên nghiệp. Dựa trên các chỉ số tài chính sau, hãy đưa ra một nhận xét khách quan, ngắn gọn (khoảng 3-4 đoạn) về tình hình tài chính của doanh nghiệp. Đánh giá tập trung vào tốc độ tăng trưởng, thay đổi cơ cấu tài sản và khả năng thanh toán hiện hành.

        Dữ liệu thô và chỉ số:
        {data_for_ai}
        """

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text

    except APIError as e:
        return f"Lỗi gọi Gemini API: {e}"
    except KeyError:
        return "Lỗi: Không tìm thấy Khóa API 'GEMINI_API_KEY'."
    except Exception as e:
        return f"Đã xảy ra lỗi không xác định: {e}"

uploaded_file = st.file_uploader(
    "1. Tải file Excel Báo cáo Tài chính (Chỉ tiêu | Năm trước | Năm sau)",
    type=['xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = ['Chỉ tiêu', 'Năm trước', 'Năm sau']
        df_processed = process_financial_data(df_raw.copy())

        st.subheader("2. Tốc độ Tăng trưởng & 3. Tỷ trọng Cơ cấu Tài sản")
        st.dataframe(df_processed.style.format({
            'Năm trước': '{:,.0f}',
            'Năm sau': '{:,.0f}',
            'Tốc độ tăng trưởng (%)': '{:.2f}%',
            'Tỷ trọng Năm trước (%)': '{:.2f}%',
            'Tỷ trọng Năm sau (%)': '{:.2f}%'
        }), use_container_width=True)

        st.subheader("4. Các Chỉ số Tài chính Cơ bản")
        try:
            tsnh_n = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]
            tsnh_n_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]
            no_ngan_han_N = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]
            no_ngan_han_N_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]

            thanh_toan_hien_hanh_N = tsnh_n / no_ngan_han_N
            thanh_toan_hien_hanh_N_1 = tsnh_n_1 / no_ngan_han_N_1

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chỉ số Thanh toán Hiện hành (Năm trước)", f"{thanh_toan_hien_hanh_N_1:.2f} lần")
            with col2:
                st.metric("Chỉ số Thanh toán Hiện hành (Năm sau)", f"{thanh_toan_hien_hanh_N:.2f} lần", delta=f"{thanh_toan_hien_hanh_N - thanh_toan_hien_hanh_N_1:.2f}")
        except IndexError:
            st.warning("Thiếu chỉ tiêu 'TÀI SẢN NGẮN HẠN' hoặc 'NỢ NGẮN HẠN'.")
            thanh_toan_hien_hanh_N = "N/A"
            thanh_toan_hien_hanh_N_1 = "N/A"

        st.subheader("5. Nhận xét Tình hình Tài chính (AI)")
        data_for_ai = pd.DataFrame({
            'Chỉ tiêu': [
                'Toàn bộ Bảng phân tích (dữ liệu thô)',
                'Tăng trưởng Tài sản ngắn hạn (%)',
                'Thanh toán hiện hành (N-1)',
                'Thanh toán hiện hành (N)'
            ],
            'Giá trị': [
                df_processed.to_markdown(index=False),
                f"{df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Tốc độ tăng trưởng (%)'].iloc[0]:.2f}%",
                f"{thanh_toan_hien_hanh_N_1}",
                f"{thanh_toan_hien_hanh_N}"
            ]
        }).to_markdown(index=False)

        if st.button("Yêu cầu AI Phân tích"):
            api_key = st.secrets.get("GEMINI_API_KEY")
            if api_key:
                with st.spinner("Đang gửi dữ liệu đến Gemini..."):
                    ai_result = get_ai_analysis(data_for_ai, api_key)
                    st.markdown("**Kết quả Phân tích từ Gemini AI:**")
                    st.info(ai_result)
            else:
                st.error("Không tìm thấy Khóa API. Vui lòng cấu hình 'GEMINI_API_KEY' trong Streamlit Secrets.")

    except Exception as e:
        st.error(f"Lỗi xử lý file: {e}")
else:
    st.info("Vui lòng tải lên file Excel để bắt đầu phân tích.")

