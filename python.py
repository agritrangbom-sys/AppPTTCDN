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

# --- Tuỳ chỉnh giao diện Agribank với hiệu ứng 3D, nổi khối và chuyên nghiệp tối ưu ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #f0f2f6 0%, #e9ebee 100%); /* Nền gradient nhẹ nhàng */
            color: #333333;
        }
        .main {
            background-color: #ffffff;
            border-radius: 16px; /* Bo tròn nhiều hơn */
            box-shadow: 0 12px 30px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.08); /* Bóng đổ đa lớp, sâu hơn */
            padding: 40px;
            margin-top: 25px;
            border: 1px solid #e0e0e0; /* Viền nhẹ tạo khối */
        }
        h1 {
            color: #9E1B32; /* Đỏ đô Agribank */
            font-size: 48px; /* To hơn */
            font-weight: 900; /* Rất đậm */
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.15); /* Bóng đổ chữ rõ hơn */
            letter-spacing: -0.5px; /* Tối ưu khoảng cách chữ */
            position: relative;
        }
        h1::after { /* Đường gạch dưới 3D cho H1 */
            content: '';
            display: block;
            width: 100px;
            height: 5px;
            background: linear-gradient(90deg, #9E1B32 0%, #00703C 100%);
            margin: 15px auto 0 auto;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        h2 {
            color: #00703C; /* Xanh lá Agribank */
            font-size: 32px; /* To hơn */
            font-weight: 700;
            border-bottom: 3px solid #e0e0e0; /* Gạch dưới đậm hơn */
            padding-bottom: 12px;
            margin-top: 50px;
            margin-bottom: 25px;
            position: relative;
        }
        h2::before { /* Icon hoặc hình ảnh nhỏ đầu H2 */
            content: '✨';
            position: absolute;
            left: -30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            color: #9E1B32;
        }
        h3 {
            color: #9E1B32; /* Đỏ đô Agribank */
            font-size: 24px; /* To hơn */
            font-weight: 700;
            margin-top: 35px;
            margin-bottom: 20px;
            border-left: 5px solid #00703C; /* Viền trái xanh lá */
            padding-left: 10px;
            line-height: 1.2;
        }
        div.stButton > button {
            background: linear-gradient(135deg, #9E1B32 0%, #B03A50 100%); /* Gradient cho nút */
            color: white;
            border: none;
            border-radius: 10px; /* Bo tròn nhiều hơn */
            padding: 1em 2em; /* To hơn */
            font-weight: 700; /* Đậm hơn */
            font-size: 17px;
            letter-spacing: 0.8px;
            box-shadow: 0 6px 15px rgba(158, 27, 50, 0.4), inset 0 1px 3px rgba(255,255,255,0.4); /* Bóng đổ 3D */
            transition: all 0.3s ease-in-out;
            cursor: pointer;
            text-transform: uppercase; /* Chữ hoa */
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #00703C 0%, #008C4A 100%); /* Gradient xanh lá khi hover */
            box-shadow: 0 8px 20px rgba(0, 112, 60, 0.5), inset 0 1px 5px rgba(255,255,255,0.5);
            transform: translateY(-3px) scale(1.02); /* Nhấn và phóng to nhẹ */
        }
        .stFileUploader label {
            font-size: 20px; /* To hơn */
            font-weight: 500;
            color: #222222;
        }
        .stFileUploader div[data-testid="stFileUploaderDropzone"] {
            border: 3px dashed #9E1B32; /* Viền đậm hơn */
            background-color: #fcfdff;
            border-radius: 12px;
            padding: 25px; /* Đệm to hơn */
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .stFileUploader div[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #00703C;
            background-color: #e9f5ed; /* Màu nền nhẹ khi hover */
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stSpinner > div > div {
            color: #9E1B32 !important;
        }
        .stProgress > div > div > div > div {
            background-color: #9E1B32 !important;
        }
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.05); /* Bóng đổ sâu hơn */
            border: 1px solid #e0e0e0;
            margin-top: 20px;
        }
        .stMetric {
            background-color: #f8f8f8;
            border-left: 6px solid #00703C; /* Viền đậm hơn */
            padding: 20px; /* Đệm to hơn */
            border-radius: 10px; /* Bo tròn nhiều hơn */
            box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Bóng đổ sâu hơn */
            margin-bottom: 20px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .stMetric::before { /* Hiệu ứng ánh sáng nhẹ */
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(120deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 70%);
            transition: all 0.5s ease;
            transform: translateX(-100%);
        }
        .stMetric:hover::before {
            transform: translateX(100%);
        }
        .stMetric:hover {
            transform: translateY(-5px) scale(1.01); /* Nổi lên và phóng to nhẹ */
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .stMetric > div[data-testid="stMetricLabel"] {
            color: #444444;
            font-weight: 500;
            font-size: 16px;
        }
        .stMetric > div[data-testid="stMetricValue"] {
            color: #9E1B32;
            font-size: 34px; /* To hơn */
            font-weight: 900; /* Rất đậm */
            margin-top: 5px;
            letter-spacing: -0.5px;
        }
        .stAlert {
            border-left: 6px solid; /* Viền đậm hơn */
            border-radius: 10px; /* Bo tròn nhiều hơn */
            padding: 15px;
            margin-top: 25px;
            font-size: 17px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .stAlert.info { border-color: #00703C; background-color: #e6f7ed; color: #005a30; }
        .stAlert.warning { border-color: #ffc107; background-color: #fff3cd; color: #856404; }
        .stAlert.error { border-color: #dc3545; background-color: #f8d7da; color: #721c24; }
        .stAlert p { margin: 0; }

        /* Chatbox styles */
        #chatBubble {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 75px; /* Lớn hơn */
            height: 75px;
            background: linear-gradient(135deg, #9E1B32 0%, #B03A50 100%); /* Gradient Agribank */
            border-radius: 50%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 2px 5px rgba(255,255,255,0.5); /* Bóng đổ 3D sâu */
            cursor: grab;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 36px; /* To hơn */
            font-weight: 900;
            transition: all 0.3s ease;
            user-select: none;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }
        #chatBubble:active {
            cursor: grabbing;
            transform: scale(0.98); /* Hiệu ứng nhấn */
        }
        #chatBubble:hover {
            transform: scale(1.1); /* Phóng to nhẹ khi hover */
            box-shadow: 0 12px 35px rgba(0,0,0,0.6), inset 0 2px 6px rgba(255,255,255,0.6);
        }

        #chatWindow {
            position: fixed;
            bottom: 120px; /* Vị trí mặc định cao hơn một chút so với bubble */
            right: 30px;
            width: 400px; /* Rộng hơn */
            height: 550px; /* Cao hơn */
            background: rgba(255,255,255,0.98);
            border: 2px solid #9E1B32; /* Viền đỏ đô */
            border-radius: 20px; /* Bo tròn nhiều hơn */
            box-shadow: 0 15px 45px rgba(0,0,0,0.5), 0 5px 15px rgba(0,0,0,0.2); /* Bóng đổ 3D rõ nét */
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(12px); /* Blur mạnh hơn */
            font-family: 'Roboto', sans-serif;
            user-select: none;
        }

        #chatHeader {
            background: linear-gradient(90deg, #9E1B32 0%, #B03A50 100%); /* Gradient cho header */
            color: white;
            padding: 15px 20px;
            font-weight: 700;
            font-size: 20px;
            text-align: center;
            cursor: grab;
            position: relative;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top-left-radius: 18px; /* Bo tròn theo cửa sổ */
            border-top-right-radius: 18px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            box-shadow: inset 0 -2px 5px rgba(0,0,0,0.2); /* Bóng đổ phía trong */
        }
        #chatHeader:active {
            cursor: grabbing;
        }

        #closeBtn {
            background: none;
            border: none;
            color: white;
            font-size: 28px; /* To hơn */
            cursor: pointer;
            transition: transform 0.2s ease, color 0.2s ease;
            padding: 0;
            line-height: 1;
        }
        #closeBtn:hover {
            transform: rotate(180deg) scale(1.1); /* Xoay và phóng to */
            color: #f0f0f0;
        }

        #chatBody {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            font-size: 16px;
            color: #333;
            background-color: #fcfdff;
            line-height: 1.6;
            scroll-behavior: smooth;
        }
        #chatBody p {
            margin-bottom: 10px;
            padding: 8px 12px;
            border-radius: 12px;
            word-wrap: break-word; /* Đảm bảo ngắt dòng */
            max-width: 90%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .user-message {
            text-align: right;
            background-color: #e6f7ed; /* Nền xanh nhạt */
            color: #005a30;
            margin-left: auto; /* Đẩy sang phải */
            border-bottom-right-radius: 2px;
            border: 1px solid #cce8d6;
        }
        .ai-message {
            text-align: left;
            background-color: #f0f2f6; /* Nền xám nhạt */
            color: #444;
            margin-right: auto; /* Đẩy sang trái */
            border-bottom-left-radius: 2px;
            border: 1px solid #e0e0e0;
        }
        .ai-message strong, .user-message strong {
            font-weight: 700;
        }

        #chatInput {
            padding: 15px 20px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            background-color: #f0f2f6;
            border-bottom-left-radius: 18px;
            border-bottom-right-radius: 18px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
        }

        #chatInput input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #9E1B32; /* Viền đậm hơn */
            border-radius: 28px; /* Bo tròn nhiều hơn */
            margin-right: 12px;
            font-size: 16px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            background-color: white;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }
        #chatInput input:focus {
            border-color: #00703C;
            box-shadow: 0 0 0 4px rgba(0, 112, 60, 0.25), inset 0 1px 5px rgba(0,0,0,0.15);
            outline: none;
        }

        #chatInput button {
            background: linear-gradient(135deg, #00703C 0%, #008C4A 100%); /* Gradient xanh lá */
            color: white;
            border: none;
            padding: 12px 22px;
            border-radius: 28px; /* Bo tròn nhiều hơn */
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 10px rgba(0, 112, 60, 0.3), inset 0 1px 3px rgba(255,255,255,0.4);
            transition: all 0.3s ease;
            text-transform: uppercase;
        }
        #chatInput button:hover {
            background: linear-gradient(135deg, #9E1B32 0%, #B03A50 100%); /* Đỏ đô khi hover */
            box-shadow: 0 6px 15px rgba(158, 27, 50, 0.4), inset 0 1px 5px rgba(255,255,255,0.5);
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

# Thêm logo Agribank
st.sidebar.image("https://www.agribank.com.vn/assets/theme_v2/images/logo.png", width=220) # Logo lớn hơn một chút
st.sidebar.markdown("---")
st.sidebar.header("Hướng dẫn sử dụng")
st.sidebar.markdown("""
<div style="font-size: 16px; line-height: 1.8;">
<p>1.  **Tải file Excel:** Chọn file Báo cáo tài chính của bạn (định dạng 'Chỉ tiêu | Năm trước | Năm sau').</p>
<p>2.  **Xem kết quả:** Bảng phân tích tốc độ tăng trưởng và tỷ trọng cơ cấu sẽ hiển thị rõ ràng.</p>
<p>3.  **Kiểm tra chỉ số:** Xem nhanh các chỉ số tài chính cơ bản đã được tính toán.</p>
<p>4.  **Phân tích AI:** Nhấn nút để nhận nhận xét chuyên sâu từ Gemini AI.</p>
<p>5.  **Chatbot hỗ trợ:** Sử dụng biểu tượng chat để hỏi đáp nhanh về các vấn đề liên quan.</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### <span style='color:#9E1B32;'>Trung tâm phát triển AI Agribank</span>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 14px; color: #555;'>Phiên bản: 1.2.0</p>", unsafe_allow_html=True)


st.title("Hệ Thống Phân Tích Báo Cáo Tài Chính")
st.markdown("### <span style='color:#00703C;'>Giải pháp AI đột phá dành cho Agribank</span>", unsafe_allow_html=True)

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
        raise ValueError("Không tìm thấy chỉ tiêu 'TỔNG CỘNG TÀI SẢN' trong báo cáo. Vui lòng kiểm tra lại file.")

    tong_tai_san_N_1 = tong_tai_san_row['Năm trước'].iloc[0]
    tong_tai_san_N = tong_tai_san_row['Năm sau'].iloc[0]

    divisor_N_1 = tong_tai_san_N_1 if tong_tai_san_N_1 != 0 else 1e-9
    divisor_N = tong_tai_san_N if tong_tai_san_N != 0 else 1e-9

    df['Tỷ trọng Năm trước (%)'] = (df['Năm trước'] / divisor_N_1) * 100
    df['Tỷ trọng Năm sau (%)'] = (df['Năm sau'] / divisor_N) * 100

    return df

def get_ai_analysis(data_for_ai, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Bạn là một chuyên gia phân tích tài chính cấp cao của Agribank, với kinh nghiệm sâu rộng về thị trường Việt Nam và nghiệp vụ tín dụng ngân hàng. Dựa trên các chỉ số tài chính của một doanh nghiệp được cung cấp bên dưới, hãy đưa ra một nhận xét khách quan, chuyên sâu, và có tính định hướng (khoảng 3-5 đoạn văn) về tình hình tài chính của doanh nghiệp. Phân tích cần tập trung vào:
        1.  **Đánh giá tổng quan về tăng trưởng:** Nhận định về động lực tăng trưởng hoặc các yếu tố gây suy giảm.
        2.  **Phân tích cơ cấu tài sản và nguồn vốn:** Đánh giá sự ổn định, hiệu quả sử dụng vốn và các rủi ro tiềm ẩn từ cơ cấu.
        3.  **Khả năng thanh toán và rủi ro thanh khoản:** Phân tích sâu chỉ số thanh toán hiện hành, xu hướng và ý nghĩa của nó đối với khả năng hoạt động liên tục.
        4.  **Đưa ra khuyến nghị chi tiết cho Agribank:** Dựa trên phân tích, đề xuất các bước hành động tiếp theo cho bộ phận tín dụng hoặc quản lý rủi ro của Agribank, ví dụ: cần xem xét thêm các chỉ tiêu nào, rủi ro cụ thể, tiềm năng hợp tác, hoặc các biện pháp bảo đảm.

        Dữ liệu thô và các chỉ số đã được tính toán:
        {data_for_ai}

        Hãy đảm bảo nhận xét của bạn sử dụng ngôn ngữ chuyên ngành tài chính ngân hàng, dễ hiểu, và mang tính ứng dụng cao cho việc ra quyết định cấp tín dụng.
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
        if len(df_raw.columns) >= 3:
            df_raw.columns = ['Chỉ tiêu', 'Năm trước', 'Năm sau']
        else:
            st.error("File Excel phải có ít nhất 3 cột: 'Chỉ tiêu', 'Năm trước', 'Năm sau'. Vui lòng kiểm tra lại định dạng file.")
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
            tsnh_row = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]
            no_ngan_han_row = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]

            if tsnh_row.empty or no_ngan_han_row.empty:
                raise IndexError("Thiếu chỉ tiêu 'TÀI SẢN NGẮN HẠN' hoặc 'NỢ NGẮN HẠN'.")

            tsnh_n = tsnh_row['Năm sau'].iloc[0]
            tsnh_n_1 = tsnh_row['Năm trước'].iloc[0]
            no_ngan_han_N = no_ngan_han_row['Năm sau'].iloc[0]
            no_ngan_han_N_1 = no_ngan_han_row['Năm trước'].iloc[0]

            thanh_toan_hien_hanh_N = tsnh_n / no_ngan_han_N if no_ngan_han_N != 0 else float('inf')
            thanh_toan_hien_hanh_N_1 = tsnh_n_1 / no_ngan_han_N_1 if no_ngan_han_N_1 != 0 else float('inf')

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chỉ số Thanh toán Hiện hành (Năm trước)", f"{thanh_toan_hien_hanh_N_1:.2f} lần")
            with col2:
                st.metric("Chỉ số Thanh toán Hiện hành (Năm sau)",
                          f"{thanh_toan_hien_hanh_N:.2f} lần",
                          delta=f"{(thanh_toan_hien_hanh_N - thanh_toan_hien_hanh_N_1):.2f}")
        except IndexError as ie:
            st.warning(f"Thiếu dữ liệu để tính Chỉ số Thanh toán Hiện hành: {ie}. Vui lòng đảm bảo các chỉ tiêu cần thiết có trong file.")
            thanh_toan_hien_hanh_N = "N/A"
            thanh_toan_hien_hanh_N_1 = "N/A"
        except ZeroDivisionError:
            st.error("Nợ ngắn hạn bằng 0, không thể tính chỉ số thanh toán hiện hành. Vui lòng kiểm tra dữ liệu hoặc liên hệ hỗ trợ.")
            thanh_toan_hien_hanh_N = "N/A"
            thanh_toan_hien_hanh_N_1 = "N/A"

        st.subheader("5. Nhận xét Chuyên sâu Tình hình Tài chính (AI)")
        data_for_ai_summary = df_processed[['Chỉ tiêu', 'Năm trước', 'Năm sau', 'Tốc độ tăng trưởng (%)', 'Tỷ trọng Năm trước (%)', 'Tỷ trọng Năm sau (%)']].copy()
        data_for_ai_summary.loc[len(data_for_ai_summary)] = ['Chỉ số Thanh toán Hiện hành (Năm trước)', thanh_toan_hien_hanh_N_1, None, None, None, None]
        data_for_ai_summary.loc[len(data_for_ai_summary)] = ['Chỉ số Thanh toán Hiện hành (Năm sau)', thanh_toan_hien_hanh_N, None, None, None, None]

        data_for_ai = data_for_ai_summary.to_markdown(index=False)

        if st.button("Yêu cầu AI Phân tích Chuyên sâu", help="Nhấn để Gemini AI phân tích báo cáo và đưa ra nhận xét chi tiết, có định hướng cho Agribank"):
            api_key = st.secrets.get("GEMINI_API_KEY")
            if api_key:
                with st.spinner("Gemini AI đang tổng hợp, phân tích chuyên sâu và đưa ra khuyến nghị... Vui lòng chờ giây lát."):
                    ai_result = get_ai_analysis(data_for_ai, api_key)
                    st.markdown("---")
                    st.markdown("<h3 style='color:#9E1B32;'>📝 Kết quả Phân tích từ Gemini AI:</h3>", unsafe_allow_html=True)
                    st.info(ai_result)
            else:
                st.error("Không tìm thấy Khóa API. Vui lòng cấu hình 'GEMINI_API_KEY' trong Streamlit Secrets để sử dụng tính năng AI phân tích chuyên sâu.")

    except ValueError as ve:
        st.error(f"Lỗi dữ liệu: {ve}. Vui lòng kiểm tra định dạng file Excel hoặc các chỉ tiêu tài chính cần thiết.")
    except Exception as e:
        st.error(f"Đã xảy ra lỗi không mong muốn khi xử lý file: {e}. Vui lòng đảm bảo file Excel của bạn đúng định dạng và có đầy đủ dữ liệu.")
else:
    st.info("Chào mừng bạn đến với Hệ thống Phân tích Báo cáo Tài chính của Agribank! Vui lòng tải lên file Excel Báo cáo Tài chính để bắt đầu phân tích chuyên sâu.")

st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)

# --- Draggable Chatbox (JavaScript) ---
import streamlit.components.v1 as components
components.html("""
<style>
  /* CSS cho chatbox đã được đưa vào phần Streamlit Markdown ở trên để dễ quản lý */
</style>

<div id="chatBubble" onclick="openChat()">💬</div>

<div id="chatWindow">
  <div id="chatHeader">
    Agribank AI Assistant
    <button id="closeBtn" onclick="closeChat()">✖</button>
  </div>
  <div id="chatBody">
    <p class="ai-message"><i>Xin chào! Tôi là trợ lý AI Agribank, sẵn sàng hỗ trợ bạn. Bạn muốn hỏi gì về báo cáo tài chính hoặc các dịch vụ ngân hàng khác?</i></p>
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
  const chatBody = document.
