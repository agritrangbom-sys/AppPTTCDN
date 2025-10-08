import streamlit as st
import pandas as pd
from google import genai
from google.genai.errors import APIError

# --- Cấu hình Trang Streamlit ---
st.set_page_config(
    page_title="Phân Tích Báo Cáo Tài Chính - TrungDev x Agribank",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Tuỳ chỉnh giao diện Agribank với hiệu ứng 3D và chuyên nghiệp ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f2f6; /* Nền xám nhạt */
        }
        .main {
            background-color: #ffffff; /* Nền trắng cho nội dung chính */
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1); /* Hiệu ứng bóng đổ nhẹ */
            padding: 30px;
            margin-top: 20px;
        }
        h1 {
            color: #9E1B32; /* Đỏ đô Agribank */
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1); /* Hiệu ứng chữ nổi */
        }
        h2 {
            color: #00703C; /* Xanh lá Agribank */
            font-size: 28px;
            font-weight: 700;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        h3 {
            color: #9E1B32; /* Đỏ đô Agribank */
            font-size: 22px;
            font-weight: 700;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        div.stButton > button {
            background-color: #9E1B32; /* Đỏ đô */
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.8em 1.8em;
            font-weight: bold;
            font-size: 16px;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(158, 27, 50, 0.3); /* Bóng đổ nút */
            transition: all 0.3s ease-in-out;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #00703C; /* Xanh lá khi hover */
            box-shadow: 0 6px 15px rgba(0, 112, 60, 0.4);
            transform: translateY(-2px); /* Hiệu ứng nhấn */
        }
        .stFileUploader label {
            font-size: 18px;
            font-weight: 500;
            color: #333333;
        }
        .stFileUploader div[data-testid="stFileUploaderDropzone"] {
            border: 2px dashed #9E1B32;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .stFileUploader div[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #00703C;
            background-color: #f9f9f9;
        }
        .stSpinner > div > div {
            color: #9E1B32 !important;
        }
        .stProgress > div > div > div > div {
            background-color: #9E1B32 !important;
        }
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .stMetric {
            background-color: #f8f8f8;
            border-left: 5px solid #00703C;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        .stMetric:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stMetric > div[data-testid="stMetricLabel"] {
            color: #333333;
            font-weight: 500;
        }
        .stMetric > div[data-testid="stMetricValue"] {
            color: #9E1B32;
            font-size: 28px;
            font-weight: 700;
        }
        .stAlert {
            border-left: 5px solid;
            border-radius: 8px;
            padding: 10px;
            margin-top: 20px;
            font-size: 16px;
        }
        .stAlert.info { border-color: #00703C; background-color: #e6f7ed; color: #005a30; }
        .stAlert.warning { border-color: #ffc107; background-color: #fff3cd; color: #856404; }
        .stAlert.error { border-color: #dc3545; background-color: #f8d7da; color: #721c24; }

        /* Chatbox styles */
        #chatBubble {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 70px; /* To hơn */
            height: 70px;
            background-color: #9E1B32; /* Đỏ đô Agribank */
            border-radius: 50%;
            box-shadow: 0 8px 25px rgba(0,0,0,0.4); /* Bóng đổ mạnh hơn */
            cursor: grab; /* Thay đổi con trỏ */
            z-index: 10000; /* Đảm bảo nổi trên tất cả */
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 32px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        #chatBubble:active {
            cursor: grabbing;
        }
        #chatBubble:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        #chatWindow {
            position: fixed;
            bottom: 110px; /* Vị trí mặc định cao hơn một chút so với bubble */
            right: 30px;
            width: 380px; /* Rộng hơn */
            height: 500px; /* Cao hơn */
            background: rgba(255,255,255,0.98); /* Gần như trắng hoàn toàn */
            border: 2px solid #9E1B32; /* Viền đỏ đô */
            border-radius: 18px; /* Bo tròn nhiều hơn */
            box-shadow: 0 12px 35px rgba(0,0,0,0.45); /* Bóng đổ mạnh và rõ */
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(10px); /* Blur mạnh hơn */
            font-family: 'Roboto', sans-serif;
        }

        #chatHeader {
            background-color: #9E1B32; /* Đỏ đô */
            color: white;
            padding: 12px 15px;
            font-weight: 700;
            font-size: 18px;
            text-align: center;
            cursor: grab;
            position: relative;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #chatHeader:active {
            cursor: grabbing;
        }

        #closeBtn {
            background: transparent;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        #closeBtn:hover {
            transform: rotate(90deg);
        }

        #chatBody {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            font-size: 15px;
            color: #333;
            background-color: #fdfdfd;
        }
        #chatBody p {
            margin-bottom: 8px;
            line-height: 1.5;
        }
        #chatBody p:last-child {
            margin-bottom: 0;
        }
        .user-message {
            text-align: right;
            color: #9E1B32;
        }
        .ai-message {
            text-align: left;
            color: #00703C;
        }
        .ai-message strong, .user-message strong {
            font-weight: 700;
        }

        #chatInput {
            padding: 12px 15px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            background-color: #f0f2f6;
        }

        #chatInput input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #9E1B32;
            border-radius: 25px; /* Bo tròn hơn */
            margin-right: 10px;
            font-size: 15px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        #chatInput input:focus {
            border-color: #00703C;
            box-shadow: 0 0 0 3px rgba(0, 112, 60, 0.2);
            outline: none;
        }

        #chatInput button {
            background-color: #9E1B32; /* Đỏ đô */
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px; /* Bo tròn hơn */
            cursor: pointer;
            font-weight: bold;
            font-size: 15px;
            box-shadow: 0 3px 8px rgba(158, 27, 50, 0.25);
            transition: all 0.3s ease;
        }
        #chatInput button:hover {
            background-color: #00703C; /* Xanh lá khi hover */
            box-shadow: 0 4px 10px rgba(0, 112, 60, 0.3);
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

# Thêm logo Agribank
st.sidebar.image("https://www.agribank.com.vn/assets/theme_v2/images/logo.png", width=200)
st.sidebar.header("Hướng dẫn sử dụng")
st.sidebar.markdown("""
1.  **Tải file Excel:** Chọn file Báo cáo tài chính của bạn.
2.  **Xem kết quả:** Bảng phân tích tốc độ tăng trưởng và tỷ trọng cơ cấu sẽ hiển thị.
3.  **Kiểm tra chỉ số:** Xem nhanh các chỉ số tài chính cơ bản.
4.  **Phân tích AI:** Nhấn nút để nhận nhận xét từ Gemini AI.
---
**Liên hệ:** [TrungDev](mailto:your.email@example.com)
""")


st.title("Phân Tích Báo Cáo Tài Chính")
st.markdown("### <span style='color:#00703C;'>Giải pháp AI cho Agribank</span>", unsafe_allow_html=True)

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
        # Khởi tạo client Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') # Sử dụng gemini-pro cho khả năng hiểu tốt hơn

        prompt = f"""
        Bạn là một chuyên gia phân tích tài chính chuyên nghiệp của Agribank, có kiến thức sâu rộng về thị trường Việt Nam. Dựa trên các chỉ số tài chính của một doanh nghiệp được cung cấp bên dưới, hãy đưa ra một nhận xét khách quan, chuyên sâu, ngắn gọn (khoảng 3-4 đoạn văn) về tình hình tài chính của doanh nghiệp. Đánh giá tập trung vào các điểm sau:
        1.  **Tốc độ tăng trưởng:** Đánh giá sự tăng trưởng hoặc suy giảm của các chỉ tiêu chính (đặc biệt là Tài sản).
        2.  **Cơ cấu tài sản:** Phân tích sự thay đổi trong cơ cấu tài sản giữa hai kỳ (Năm trước và Năm sau), nhận định về xu hướng đầu tư hoặc quản lý tài sản.
        3.  **Khả năng thanh toán hiện hành:** Đánh giá khả năng đáp ứng các nghĩa vụ nợ ngắn hạn của doanh nghiệp.
        4.  **Đưa ra khuyến nghị sơ bộ (nếu có):** Dựa trên phân tích, có thể đề xuất một hướng nghiên cứu sâu hơn hoặc một lưu ý quan trọng cho Agribank khi xem xét doanh nghiệp này.

        Dữ liệu thô và các chỉ số được tính toán:
        {data_for_ai}

        Hãy đảm bảo nhận xét của bạn chuyên nghiệp, dễ hiểu và mang tính ứng dụng cao cho việc ra quyết định của ngân hàng.
        """

        response = model.generate_content(prompt)
        return response.text

    except APIError as e:
        return f"Lỗi gọi Gemini API: {e}. Vui lòng kiểm tra lại Khóa API hoặc kết nối mạng."
    except ValueError as e:
        return f"Lỗi cấu hình hoặc dữ liệu: {e}. Vui lòng kiểm tra lại định dạng file hoặc Khóa API."
    except Exception as e:
        return f"Đã xảy ra lỗi không xác định: {e}"

uploaded_file = st.file_uploader(
    "1. Tải lên file Excel Báo cáo Tài chính của doanh nghiệp (định dạng 'Chỉ tiêu | Năm trước | Năm sau')",
    type=['xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file)
        # Đảm bảo cột có tên chính xác, nếu không sẽ gán lại
        if len(df_raw.columns) >= 3:
            df_raw.columns = ['Chỉ tiêu', 'Năm trước', 'Năm sau']
        else:
            st.error("File Excel phải có ít nhất 3 cột: 'Chỉ tiêu', 'Năm trước', 'Năm sau'.")
            st.stop()

        df_processed = process_financial_data(df_raw.copy())

        st.subheader("2. Bảng Phân tích Tốc độ Tăng trưởng & 3. Tỷ trọng Cơ cấu Tài sản")
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

            thanh_toan_hien_hanh_N = tsnh_n / no_ngan_han_N if no_ngan_han_N != 0 else float('inf')
            thanh_toan_hien_hanh_N_1 = tsnh_n_1 / no_ngan_han_N_1 if no_ngan_han_N_1 != 0 else float('inf')

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chỉ số Thanh toán Hiện hành (Năm trước)", f"{thanh_toan_hien_hanh_N_1:.2f} lần")
            with col2:
                st.metric("Chỉ số Thanh toán Hiện hành (Năm sau)",
                          f"{thanh_toan_hien_hanh_N:.2f} lần",
                          delta=f"{(thanh_toan_hien_hanh_N - thanh_toan_hien_hanh_N_1):.2f}")
        except IndexError:
            st.warning("Thiếu chỉ tiêu 'TÀI SẢN NGẮN HẠN' hoặc 'NỢ NGẮN HẠN' để tính Chỉ số Thanh toán Hiện hành.")
            thanh_toan_hien_hanh_N = "N/A"
            thanh_toan_hien_hanh_N_1 = "N/A"
        except ZeroDivisionError:
            st.error("Nợ ngắn hạn bằng 0, không thể tính chỉ số thanh toán hiện hành. Vui lòng kiểm tra dữ liệu.")
            thanh_toan_hien_hanh_N = "N/A"
            thanh_toan_hien_hanh_N_1 = "N/A"

        st.subheader("5. Nhận xét Tình hình Tài chính (AI)")
        # Chuẩn bị dữ liệu để gửi cho AI
        data_for_ai_summary = df_processed[['Chỉ tiêu', 'Năm trước', 'Năm sau', 'Tốc độ tăng trưởng (%)', 'Tỷ trọng Năm trước (%)', 'Tỷ trọng Năm sau (%)']].copy()
        data_for_ai_summary.loc[len(data_for_ai_summary)] = ['Chỉ số Thanh toán Hiện hành (Năm trước)', thanh_toan_hien_hanh_N_1, None, None, None, None]
        data_for_ai_summary.loc[len(data_for_ai_summary)] = ['Chỉ số Thanh toán Hiện hành (Năm sau)', thanh_toan_hien_hanh_N, None, None, None, None]

        # Chuyển đổi toàn bộ dataframe thành markdown để AI dễ đọc
        data_for_ai = data_for_ai_summary.to_markdown(index=False)


        if st.button("Yêu cầu AI Phân tích Tình hình Tài chính", help="Nhấn để Gemini AI phân tích báo cáo và đưa ra nhận xét"):
            api_key = st.secrets.get("GEMINI_API_KEY")
            if api_key:
                with st.spinner("Gemini AI đang tổng hợp và phân tích dữ liệu... Vui lòng chờ giây lát."):
                    ai_result = get_ai_analysis(data_for_ai, api_key)
                    st.markdown("---")
                    st.markdown("<h3 style='color:#9E1B32;'>📝 Kết quả Phân tích từ Gemini AI:</h3>", unsafe_allow_html=True)
                    st.info(ai_result)
            else:
                st.error("Không tìm thấy Khóa API. Vui lòng cấu hình 'GEMINI_API_KEY' trong Streamlit Secrets để sử dụng tính năng AI phân tích.")

    except ValueError as ve:
        st.error(f"Lỗi dữ liệu: {ve}. Vui lòng kiểm tra định dạng file Excel hoặc các chỉ tiêu tài chính cần thiết.")
    except Exception as e:
        st.error(f"Đã xảy ra lỗi không mong muốn khi xử lý file: {e}. Vui lòng đảm bảo file Excel của bạn đúng định dạng.")
else:
    st.info("Vui lòng tải lên file Excel Báo cáo Tài chính để bắt đầu quá trình phân tích bởi TrungDev và Agribank AI.")

# Thêm một chút không gian ở cuối để tránh chatbox che mất nội dung cuối cùng
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)


# --- Draggable Chatbox (JavaScript) ---
import streamlit.components.v1 as components
components.html("""
<style>
  /* CSS cho chatbox đã được đưa vào phần Streamlit Markdown ở trên để dễ quản lý */
</style>

<div id="chatBubble" onclick="openChat()">💬</div>

<div id="chatWindow">
  <div id="chatHeader">
    Gemini Chat Agribank
    <button id="closeBtn" onclick="closeChat()">❌</button>
  </div>
  <div id="chatBody">
    <p><i>Xin chào! Tôi là trợ lý AI của Agribank. Bạn muốn hỏi gì về báo cáo tài chính hoặc các dịch vụ khác?</i></p>
  </div>
  <div id="chatInput">
    <input type="text" id="userInput" placeholder="Nhập câu hỏi của bạn...">
    <button onclick="sendMessage()">Gửi</button>
  </div>
</div>

<script>
  const bubble = document.getElementById("chatBubble");
  const chatWindow = document.getElementById("chatWindow");
  const chatHeader = document.getElementById("chatHeader");
  const chatBody = document.getElementById("chatBody");
  const userInput = document.getElementById("userInput");

  let chatWindowPosX = 0;
  let chatWindowPosY = 0;
  let bubblePosX = 0;
  let bubblePosY = 0;
  let isDraggingChatWindow = false;
  let isDraggingChatBubble = false;

  // Set initial positions based on CSS 'right' and 'bottom'
  function setInitialPositions() {
    const windowRect = chatWindow.getBoundingClientRect();
    chatWindowPosX = window.innerWidth - windowRect.width - parseInt(window.getComputedStyle(chatWindow).right);
    chatWindowPosY = window.innerHeight - windowRect.height - parseInt(window.getComputedStyle(chatWindow).bottom);

    const bubbleRect = bubble.getBoundingClientRect();
    bubblePosX = window.innerWidth - bubbleRect.width - parseInt(window.getComputedStyle(bubble).right);
    bubblePosY = window.innerHeight - bubbleRect.height - parseInt(window.getComputedStyle(bubble).bottom);
  }
  window.onload = setInitialPositions;
  window.onresize = setInitialPositions; // Recalculate on resize

  function openChat() {
    bubble.style.display = "none";
    chatWindow.style.display = "flex";
    // Đảm bảo chat window không bị ẩn sau khi mở
    if (chatWindow.style.right === "" || chatWindow.style.bottom === "") {
        chatWindow.style.right = "30px";
        chatWindow.style.bottom = "110px";
    }
  }

  function closeChat() {
    chatWindow.style.display = "none";
    bubble.style.display = "flex";
    // Đảm bảo chat bubble không bị ẩn sau khi đóng
    if (bubble.style.right === "" || bubble.style.bottom === "") {
        bubble.style.right = "30px";
        bubble.style.bottom = "30px";
    }
  }

  // Handle messages (placeholder for now)
  function sendMessage() {
    const userText = userInput.value.trim();
    if (userText === "") return;

    const userMsg = document.createElement("p");
    userMsg.className = "user-message";
    userMsg.innerHTML = "<b>Bạn:</b> " + userText;
    chatBody.appendChild(userMsg);

    const aiMsg = document.createElement("p");
    aiMsg.className = "ai-message";
    aiMsg.innerHTML = "<b>Gemini:</b> Cảm ơn bạn đã hỏi. Tính năng trả lời trực tiếp sẽ sớm được cập nhật. Hiện tại, bạn có thể sử dụng chức năng phân tích báo cáo tài chính phía trên nhé!";
    chatBody.appendChild(aiMsg);

    userInput.value = "";
    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
  }

  // Draggable logic for Chat Window
  chatHeader.addEventListener("mousedown", function(e) {
    isDraggingChatWindow = true;
    chatWindowPosX = e.clientX - chatWindow.getBoundingClientRect().left;
    chatWindowPosY = e.clientY - chatWindow.getBoundingClientRect().top;
    chatWindow.style.cursor = "grabbing";
    document.body.style.userSelect = "none";
  });

  // Draggable logic for Chat Bubble
  bubble.addEventListener("mousedown", function(e) {
    isDraggingChatBubble = true;
    bubblePosX = e.clientX - bubble.getBoundingClientRect().left;
    bubblePosY = e.clientY - bubble.getBoundingClientRect().top;
    bubble.style.cursor = "grabbing";
    document.body.style.userSelect = "none";
  });

  document.addEventListener("mouseup", function() {
    isDraggingChatWindow = false;
    isDraggingChatBubble = false;
    chatWindow.style.cursor = "grab";
    bubble.style.cursor = "grab";
    document.body.style.userSelect = "auto";
  });

  document.addEventListener("mousemove", function(e) {
    if (isDraggingChatWindow) {
      chatWindow.style.left = (e.clientX - chatWindowPosX) + "px";
      chatWindow.style.top = (e.clientY - chatWindowPosY) + "px";
      chatWindow.style.right = "auto"; // Override right/bottom for dragging
      chatWindow.style.bottom = "auto";
    }
    if (isDraggingChatBubble) {
      bubble.style.left = (e.clientX - bubblePosX) + "px";
      bubble.style.top = (e.clientY - bubblePosY) + "px";
      bubble.style.right = "auto";
      bubble.style.bottom = "auto";
    }
  });

  // Prevent default submit on Enter key for input field
  userInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent form submission
      sendMessage();
    }
  });
</script>
""", height=30) # Chiều cao có thể điều chỉnh để không làm ảnh hưởng layout chính
