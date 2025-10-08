import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai # Thêm thư viện Gemini

# --- 1. Hàm Tải Dữ Liệu (Không đổi) ---
def load_financial_data(file_path="financial_data.xlsx"):
    try:
        bckt = pd.read_excel(file_path, sheet_name="Bảng Cân Đối Kế Toán").set_index('Chỉ tiêu')
        kqkd = pd.read_excel(file_path, sheet_name="Kết Quả Hoạt Động Kinh Doanh").set_index('Chỉ tiêu')
        lctt = pd.read_excel(file_path, sheet_name="Lưu Chuyển Tiền Tệ").set_index('Chỉ tiêu')
        return bckt, kqkd, lctt
    except FileNotFoundError:
        st.error(f"Không tìm thấy file {file_path}. Vui lòng đảm bảo file đã được đặt cùng thư mục với app.py hoặc kiểm tra lại đường dẫn.")
        st.stop()
    except KeyError as e:
        st.error(f"Lỗi đọc sheet: {e}. Vui lòng kiểm tra tên các sheet trong file Excel của bạn (phải là 'Bảng Cân Đối Kế Toán', 'Kết Quả Hoạt Động Kinh Doanh', 'Lưu Chuyển Tiền Tệ').")
        st.stop()
    except Exception as e:
        st.error(f"Có lỗi xảy ra khi đọc file Excel: {e}")
        st.stop()

# --- 2. Hàm Tính Toán Các Chỉ Số Tài Chính (Không đổi) ---
def calculate_financial_ratios(bckt, kqkd):
    ratios = {}
    periods = bckt.columns

    for period in periods:
        bckt_p = bckt[period]
        kqkd_p = kqkd[period]

        def get_value(df_series, item):
            return df_series.loc[item] if item in df_series.index else 0

        doanh_thu_bh = get_value(kqkd_p, 'Doanh thu bán hàng và cung cấp dịch vụ')
        loi_nhuan_gop = get_value(kqkd_p, 'Lợi nhuận gộp về bán hàng và cung cấp dịch vụ')
        loi_nhuan_sau_thue = get_value(kqkd_p, 'Lợi nhuận sau thuế TNDN')
        tong_tai_san = get_value(bckt_p, 'TỔNG CỘNG TÀI SẢN')
        tong_von_csh = get_value(bckt_p, 'TỔNG CỘNG VỐN CHỦ SỞ HỮU')
        tong_no = get_value(bckt_p, 'TỔNG CỘNG NỢ PHẢI TRẢ')
        tai_san_ngan_han = get_value(bckt_p, 'TỔNG CỘNG TÀI SẢN NGẮN HẠN')
        no_ngan_han = get_value(bckt_p, 'Nợ ngắn hạn')

        ratios[f'Biên lợi nhuận gộp ({period})'] = (loi_nhuan_gop / doanh_thu_bh) if doanh_thu_bh != 0 else 0
        ratios[f'Biên lợi nhuận ròng ({period})'] = (loi_nhuan_sau_thue / doanh_thu_bh) if doanh_thu_bh != 0 else 0
        ratios[f'ROA ({period})'] = (loi_nhuan_sau_thue / tong_tai_san) if tong_tai_san != 0 else 0
        ratios[f'ROE ({period})'] = (loi_nhuan_sau_thue / tong_von_csh) if tong_von_csh != 0 else 0

        ratios[f'Hệ số thanh toán hiện hành ({period})'] = (tai_san_ngan_han / no_ngan_han) if no_ngan_han != 0 else 0

        ratios[f'Hệ số Nợ/Tổng tài sản ({period})'] = (tong_no / tong_tai_san) if tong_tai_san != 0 else 0
        ratios[f'Hệ số Nợ/Vốn chủ sở hữu ({period})'] = (tong_no / tong_von_csh) if tong_von_csh != 0 else 0

        ratios[f'Vòng quay tổng tài sản ({period})'] = (doanh_thu_bh / tong_tai_san) if tong_tai_san != 0 else 0

    formatted_ratios = {}
    for ratio_name in set([k.split(' (')[0] for k in ratios.keys()]):
        formatted_ratios[ratio_name] = [ratios[f'{ratio_name} ({p})'] for p in periods]

    ratios_df_final = pd.DataFrame(formatted_ratios, index=periods).T
    return ratios_df_final

# --- 3. Hàm Trực Quan Hóa (Không đổi) ---
def plot_financial_data(df, title, y_axis_title):
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col))

    fig.update_layout(title_text=title,
                      xaxis_title="Chỉ tiêu",
                      yaxis_title=y_axis_title,
                      barmode='group',
                      hovermode="x unified",
                      legend_title_text="Kỳ báo cáo")
    return fig

def plot_ratio_trends(ratios_df):
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("Biên lợi nhuận ròng", "ROA", "ROE", "Hệ số Nợ/Tổng tài sản"))

    if 'Biên lợi nhuận ròng' in ratios_df.index:
        fig.add_trace(go.Scatter(x=ratios_df.columns, y=ratios_df.loc['Biên lợi nhuận ròng'], mode='lines+markers', name='Biên lợi nhuận ròng'),
                      row=1, col=1)

    if 'ROA' in ratios_df.index:
        fig.add_trace(go.Scatter(x=ratios_df.columns, y=ratios_df.loc['ROA'], mode='lines+markers', name='ROA'),
                      row=1, col=2)

    if 'ROE' in ratios_df.index:
        fig.add_trace(go.Scatter(x=ratios_df.columns, y=ratios_df.loc['ROE'], mode='lines+markers', name='ROE'),
                      row=2, col=1)

    if 'Hệ số Nợ/Tổng tài sản' in ratios_df.index:
        fig.add_trace(go.Scatter(x=ratios_df.columns, y=ratios_df.loc['Hệ số Nợ/Tổng tài sản'], mode='lines+markers', name='Hệ số Nợ/Tổng tài sản'),
                      row=2, col=2)

    fig.update_layout(height=700, showlegend=False, title_text="Xu hướng các chỉ số tài chính chính")
    fig.update_yaxes(tickformat=".2%", title_text="Tỷ lệ")
    return fig

# --- 4. Hàm Phân Tích Chuyên Sâu của AI (Sử dụng Gemini) ---
def get_ai_financial_analysis(bckt_df, kqkd_df, ratios_df):
    # Cấu hình Gemini với API Key từ Streamlit secrets
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except KeyError:
        st.error("GOOGLE_API_KEY chưa được cấu hình trong .streamlit/secrets.toml")
        return None
    except Exception as e:
        st.error(f"Lỗi cấu hình Gemini API: {e}")
        return None

    # Chọn mô hình Gemini
    # Có thể dùng "gemini-pro" cho văn bản hoặc các biến thể mới hơn nếu có
    model = genai.GenerativeModel('gemini-pro')

    # Chuyển đổi DataFrames thành chuỗi để đưa vào prompt
    bckt_str = bckt_df.to_markdown()
    kqkd_str = kqkd_df.to_markdown()
    ratios_str = ratios_df.to_markdown(floatfmt=".2%")

    # Xây dựng prompt
    prompt = f"""
    Bạn là một chuyên gia phân tích tài chính cấp cao của Agribank, với kinh nghiệm sâu rộng về thị trường Việt Nam và nghiệp vụ tín dụng ngân hàng. Dựa trên các chỉ số tài chính của một doanh nghiệp được cung cấp bên dưới, hãy đưa ra một nhận xét khách quan, chuyên sâu, và có tính định hướng (khoảng 3-5 đoạn văn) về tình hình tài chính của doanh nghiệp. Phân tích cần tập trung vào:
    1.  **Đánh giá tổng quan về tăng trưởng:** Nhận định về động lực tăng trưởng hoặc các yếu tố gây suy giảm.
    2.  **Phân tích cơ cấu tài sản và nguồn vốn:** Đánh giá sự ổn định, hiệu quả sử dụng vốn và các rủi ro tiềm ẩn từ cơ cấu.
    3.  **Khả năng thanh toán và rủi ro thanh khoản:** Phân tích sâu chỉ số thanh toán hiện hành, xu hướng và ý nghĩa của nó đối với khả năng hoạt động liên tục.
    4.  **Đưa ra khuyến nghị chi tiết cho Agribank:** Dựa trên phân tích, đề xuất các bước hành động tiếp theo cho bộ phận tín dụng hoặc quản lý rủi ro của Agribank, ví dụ: cần xem xét thêm các chỉ tiêu nào, rủi ro cụ thể, tiềm năng hợp tác, hoặc các biện pháp bảo đảm.

    Dữ liệu thô và các chỉ số đã được tính toán:

    ---
    ### Bảng Cân Đối Kế Toán:
    {bckt_str}

    ### Kết Quả Hoạt Động Kinh Doanh:
    {kqkd_str}

    ### Các Chỉ Số Tài Chính:
    {ratios_str}
    ---

    Hãy đảm bảo nhận xét của bạn sử dụng ngôn ngữ chuyên ngành tài chính ngân hàng, dễ hiểu, và mang tính ứng dụng cao cho việc ra quyết định cấp tín dụng.
    """

    try:
        with st.spinner("AI (Gemini) đang phân tích dữ liệu tài chính..."):
            # Gọi API của Gemini
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7, # Điều chỉnh để có câu trả lời sáng tạo hơn (cao hơn) hoặc tập trung hơn (thấp hơn)
                    max_output_tokens=1000 # Giới hạn độ dài phản hồi
                )
            )
            return response.text # Lấy nội dung văn bản từ phản hồi
    except Exception as e:
        st.error(f"Lỗi khi gọi API Gemini: {e}. Vui lòng kiểm tra API Key và giới hạn sử dụng.")
        return None

# --- 5. Giao Diện Ứng Dụng Streamlit (Giữ nguyên) ---
st.set_page_config(layout="wide", page_title="Phân Tích Báo Cáo Tài Chính")

st.title("Ứng Dụng Phân Tích Báo Cáo Tài Chính Doanh Nghiệp")
st.write("Phân tích các báo cáo tài chính cơ bản, tính toán các chỉ số quan trọng và nhận định chuyên sâu từ AI.")

uploaded_file = st.file_uploader("Tải lên file Excel báo cáo tài chính của doanh nghiệp (phải có các sheet: 'Bảng Cân Đối Kế Toán', 'Kết Quả Hoạt Động Kinh Doanh', 'Lưu Chuyển Tiền Tệ')", type=["xlsx"])

bckt = pd.DataFrame()
kqkd = pd.DataFrame()
lctt = pd.DataFrame()

if uploaded_file is not None:
    with open("temp_financial_data.xlsx", "wb") as f:
        f.write(uploaded_file.getbuffer())
    bckt, kqkd, lctt = load_financial_data("temp_financial_data.xlsx")
else:
    st.info("Vui lòng tải lên file Excel để bắt đầu phân tích.")
    st.stop()

if not bckt.empty and not kqkd.empty:
    st.header("1. Dữ liệu Báo cáo Tài chính")

    tab1, tab2, tab3 = st.tabs(["Bảng Cân Đối Kế Toán", "Kết Quả Hoạt Động Kinh Doanh", "Lưu Chuyển Tiền Tệ"])

    with tab1:
        st.subheader("Bảng Cân Đối Kế Toán (Balance Sheet)")
        st.dataframe(bckt.style.format("{:,.0f}"))
    with tab2:
        st.subheader("Kết Quả Hoạt Động Kinh Doanh (Income Statement)")
        st.dataframe(kqkd.style.format("{:,.0f}"))
    with tab3:
        st.subheader("Lưu Chuyển Tiền Tệ (Cash Flow Statement)")
        st.dataframe(lctt.style.format("{:,.0f}"))

    st.header("2. Các Chỉ Số Tài Chính Quan Trọng")
    ratios_df = calculate_financial_ratios(bckt, kqkd)
    st.dataframe(ratios_df.style.format("{:.2%}"))

    st.markdown("""
    Các chỉ số được tính toán:
    *   **Biên lợi nhuận gộp**: Lợi nhuận gộp / Doanh thu
    *   **Biên lợi nhuận ròng**: Lợi nhuận sau thuế / Doanh thu
    *   **ROA (Return on Assets)**: Lợi nhuận sau thuế / Tổng tài sản
    *   **ROE (Return on Equity)**: Lợi nhuận sau thuế / Vốn chủ sở hữu
    *   **Hệ số thanh toán hiện hành**: Tài sản ngắn hạn / Nợ ngắn hạn
    *   **Hệ số Nợ/Tổng tài sản**: Tổng nợ phải trả / Tổng tài sản
    *   **Hệ số Nợ/Vốn chủ sở hữu**: Tổng nợ phải trả / Vốn chủ sở hữu
    *   **Vòng quay tổng tài sản**: Doanh thu / Tổng tài sản
    """)

    st.header("3. Trực Quan Hóa")

    st.subheader("Xu hướng các chỉ số tài chính chính")
    st.plotly_chart(plot_ratio_trends(ratios_df), use_container_width=True)

    st.subheader("Phân tích Tài sản và Nguồn vốn")
    selected_bckt_category = st.selectbox(
        "Chọn danh mục để xem chi tiết từ Bảng Cân Đối Kế Toán:",
        ['TỔNG CỘNG TÀI SẢN NGẮN HẠN', 'TỔNG CỘNG TÀI SẢN DÀI HẠN',
         'TỔNG CỘNG TÀI SẢN', 'TỔNG CỘNG NỢ PHẢI TRẢ', 'TỔNG CỘNG VỐN CHỦ SỞ HỮU']
    )
    if selected_bckt_category in bckt.index:
        bckt_plot_df = pd.DataFrame(bckt.loc[selected_bckt_category]).T
        st.plotly_chart(plot_financial_data(bckt_plot_df, f'Giá trị {selected_bckt_category} qua các kỳ', 'Giá trị'), use_container_width=True)
    else:
        st.warning(f"Chỉ tiêu '{selected_bckt_category}' không tồn tại trong Bảng Cân Đối Kế Toán.")

    st.subheader("Phân tích Doanh thu và Lợi nhuận")
    kqkd_plot_items = ['Doanh thu bán hàng và cung cấp dịch vụ', 'Giá vốn hàng bán', 'Lợi nhuận gộp về bán hàng và cung cấp dịch vụ',
                                 'Lợi nhuận thuần từ hoạt động kinh doanh', 'Lợi nhuận sau thuế TNDN']
    existing_kqkd_items = [item for item in kqkd_plot_items if item in kqkd.index]

    if existing_kqkd_items:
        kqkd_plot_df = kqkd.loc[existing_kqkd_items]
        st.plotly_chart(plot_financial_data(kqkd_plot_df.T, 'Xu hướng Doanh thu và Lợi nhuận', 'Giá trị'), use_container_width=True)
    else:
        st.warning("Không đủ dữ liệu trong Kết Quả Hoạt Động Kinh Doanh để vẽ biểu đồ doanh thu và lợi nhuận.")

    st.subheader("Phân tích Lưu Chuyển Tiền Tệ")
    st.plotly_chart(plot_financial_data(lctt.T, 'Lưu Chuyển Tiền Thuần qua các kỳ', 'Giá trị'), use_container_width=True)

    st.header("4. Nhận Định Chuyên Sâu từ Chuyên Gia Agribank")
    if st.button("Tạo phân tích AI"):
        ai_analysis = get_ai_financial_analysis(bckt, kqkd, ratios_df)
        if ai_analysis:
            st.markdown(ai_analysis)

st.sidebar.markdown("---")
st.sidebar.markdown("### Về ứng dụng")
st.sidebar.info(
    "Ứng dụng này cung cấp cái nhìn tổng quan về tình hình tài chính của công ty "
    "dựa trên các báo cáo tài chính cơ bản. "
    "Dữ liệu được sử dụng là ví dụ và cần được thay thế bằng dữ liệu thực tế."
)
