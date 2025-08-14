import streamlit as st
import pandas as pd
import random
import requests
import io

# Cấu hình trang
st.set_page_config(page_title="Quiz Trắc Nghiệm", layout="wide")

# CSS tùy chỉnh
st.markdown("""
<style>
.main-contai                    # Xử lý đáp án đúng - lấy từ phần cuối cùng
                    correct = parts[-1].strip() if len(parts) > 0 and parts[-1].strip() else ""
                    
                    # Nếu không có đáp án đúng ở cuối, kiểm tra vị trí 6 (cho trường hợp 7 phần)
                    if not correct and len(parts) >= 7:
                        correct = parts[6].strip()
                    
                    # Debug: Kiểm tra điều kiện - chỉ cần có câu hỏi + ít nhất A và B
                    if question and a and b:
                        data.append([question, a, b, c, d, e, correct])
                    else:
                        missing_parts = []
                        if not question: missing_parts.append("câu hỏi")
                        if not a: missing_parts.append("đáp án A")
                        if not b: missing_parts.append("đáp án B")
                        st.warning(f"Dòng bị bỏ qua - thiếu {', '.join(missing_parts)}: {line[:100]}...")ont-size: 20px;
}
.quiz-layout {
    display: flex;
    gap: 30px;
    height: 80vh;
}
.answers-section {
    flex: 1;
    padding: 25px;
    background-color: #f8f9fa;
    border-radius: 15px;
    border-right: 4px solid #007bff;
    margin-right: 15px;
}
.question-section {
    flex: 1;
    padding: 25px;
    background-color: #fff;
    border-radius: 15px;
    border: 2px solid #dee2e6;
    margin-left: 15px;
}
.question-text {
    font-size: 25px;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 25px;
    line-height: 1.6;
    padding: 20px;
    background-color: #e3f2fd;
    border-radius: 10px;
    border-left: 6px solid #1976d2;
}
.answer-option {
    margin: 12px 0;
    padding: 18px;
    background-color: white;
    border-radius: 10px;
    border: 2px solid #e9ecef;
    font-size: 24px;
    line-height: 1.6;
    cursor: pointer;
    transition: all 0.3s ease;
}
.answer-option:hover {
    border-color: #007bff;
    background-color: #f8f9fa;
}
/* Tùy chỉnh checkbox */
.stCheckbox > label {
    font-size: 24px !important;
    padding: 18px !important;
    margin: 10px 0 !important;
    background-color: white !important;
    border-radius: 10px !important;
    border: 2px solid #e9ecef !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}
.stCheckbox > label:hover {
    border-color: #007bff !important;
    background-color: #f8f9fa !important;
}
.stCheckbox > label > div {
    font-size: 24px !important;
}
.correct-feedback {
    background-color: #d4edda;
    border-color: #28a745;
    color: #155724;
}
.incorrect-feedback {
    background-color: #f8d7da;
    border-color: #dc3545;
    color: #721c24;
}
.section-title {
    font-size: 24px;
    font-weight: bold;
    color: #495057;
    margin-bottom: 20px;
    text-align: center;
    padding: 15px;
    background-color: #e9ecef;
    border-radius: 10px;
}
.progress-info {
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
    color: #007bff;
}
.btn-custom {
    background-color: #007bff;
    color: white;
    padding: 15px 30px;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    width: 100%;
    margin: 10px 0;
}
.feedback-box {
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
}
.feedback-correct {
    background-color: #d4edda;
    color: #155724;
    border: 2px solid #28a745;
}
.feedback-incorrect {
    background-color: #f8d7da;
    color: #721c24;
    border: 2px solid #dc3545;
}
.preview-question {
    background-color: #f8f9fa;
    padding: 20px;
    margin: 15px 0;
    border-radius: 10px;
    border-left: 4px solid #007bff;
    font-size: 16px;
}
.preview-answer {
    margin: 8px 0;
    padding: 8px;
    background-color: white;
    border-radius: 5px;
    border: 1px solid #e9ecef;
}
.preview-correct {
    background-color: #e8f5e8;
    border-left: 4px solid #28a745;
    padding: 10px;
    border-radius: 5px;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

def convert_gdrive_link(gdrive_link):
    """Chuyển đổi Google Drive link thành direct download link"""
    try:
        if "drive.google.com" in gdrive_link:
            # Lấy file ID từ link Google Drive
            if "/file/d/" in gdrive_link:
                file_id = gdrive_link.split("/file/d/")[1].split("/")[0]
            elif "id=" in gdrive_link:
                file_id = gdrive_link.split("id=")[1].split("&")[0]
            else:
                return None
            
            # Tạo direct download link
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return None
    except Exception as e:
        st.error(f"Lỗi xử lý link Google Drive: {e}")
        return None

def download_from_gdrive(gdrive_link):
    """Tải file từ Google Drive và trả về file object"""
    try:
        download_link = convert_gdrive_link(gdrive_link)
        if not download_link:
            st.error("Link Google Drive không hợp lệ")
            return None
        
        # Tải file
        response = requests.get(download_link)
        if response.status_code == 200:
            # Tạo file object từ content
            file_content = io.BytesIO(response.content)
            return file_content
        else:
            st.error(f"Không thể tải file từ Google Drive. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Lỗi tải file từ Google Drive: {e}")
        return None

def load_excel_file(uploaded_file):
    """Đọc file Excel và trả về DataFrame"""
    try:
        df = pd.read_excel(uploaded_file)
        if df.shape[1] < 6:
            st.error("File Excel phải có ít nhất 6 cột (Câu hỏi, A, B, C, D, Đáp án đúng)")
            return None
        elif df.shape[1] == 6:
            st.info("File có 6 cột - Sẽ chỉ hiển thị đáp án A, B, C, D")
        else:
            st.info("File có 7+ cột - Đáp án E sẽ hiển thị khi có dữ liệu")
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {str(e)}")
        return None

def load_txt_file(uploaded_file):
    """Đọc file TXT và chuyển đổi thành DataFrame"""
    try:
        # Đọc nội dung file - xử lý cả file upload và file từ Google Drive
        if hasattr(uploaded_file, 'read'):
            if hasattr(uploaded_file, 'decode'):
                content = uploaded_file.decode('utf-8')
            else:
                content = uploaded_file.read().decode('utf-8')
        else:
            content = str(uploaded_file)
        
        lines = content.strip().split('\n')
        
        data = []
        for line in lines:
            line = line.strip()
            if line:  # Bỏ qua dòng trống
                # Tách theo dấu //
                parts = line.split('//')
                if len(parts) >= 4:  # Ít nhất có câu hỏi + A + B + đáp án đúng
                    # Xử lý câu hỏi - loại bỏ số thứ tự đầu nếu có
                    question = parts[0].strip()
                    # Loại bỏ pattern như "3.Which..." thành "Which..."
                    import re
                    question = re.sub(r'^\d+\.\s*', '', question)
                    
                    # Xử lý các đáp án
                    a = parts[1].strip() if len(parts) > 1 else ""
                    b = parts[2].strip() if len(parts) > 2 else ""
                    c = parts[3].strip() if len(parts) > 3 else ""
                    d = parts[4].strip() if len(parts) > 4 else ""
                    e = parts[5].strip() if len(parts) > 5 and parts[5].strip() else ""
                    
                    # Xử lý đáp án đúng - lấy từ phần cuối cùng
                    correct = parts[-1].strip() if parts[-1].strip() else ""
                    
                    # Kiểm tra nếu đáp án đúng nằm trong phần đáp án E (trường hợp đặc biệt)
                    if not correct and len(parts) > 6:
                        correct = parts[6].strip()
                    
                    # Debug: In ra để kiểm tra
                    if question and a and b:  # Chỉ cần có câu hỏi, A và B là đủ
                        data.append([question, a, b, c, d, e, correct])
                    else:
                        st.warning(f"Câu hỏi không đầy đủ thông tin: {question[:50]}...")
        
        if not data:
            st.error("Không tìm thấy câu hỏi hợp lệ trong file TXT")
            return None
            
        # Tạo DataFrame - sử dụng pandas đã import ở đầu file
        df = pd.DataFrame(data, columns=['Câu hỏi', 'A', 'B', 'C', 'D', 'E', 'Đáp án đúng'])
        st.success(f"Đã đọc thành công {len(data)} câu hỏi từ file TXT")
        return df
        
    except Exception as e:
        st.error(f"Lỗi khi đọc file TXT: {str(e)}")
        return None

def validate_questions_data(df):
    """Kiểm tra và báo cáo lỗi trong dữ liệu câu hỏi"""
    errors = []
    warnings = []
    question_numbers = []
    
    for i, (_, row) in enumerate(df.iterrows()):
        row_num = i + 1
        question_text = str(row.iloc[0]).strip()
        
        # Trích xuất số thứ tự từ câu hỏi
        import re
        number_match = re.match(r'^(\d+)\.?\s*', question_text)
        if number_match:
            question_numbers.append((row_num, int(number_match.group(1)), question_text[:50] + "..."))
        
        # Kiểm tra câu hỏi trống
        if not question_text or question_text == "":
            errors.append(f"Câu {row_num}: Câu hỏi trống")
        
        # Kiểm tra thiếu đáp án A, B (bắt buộc), C, D (tùy chọn)
        # Chỉ yêu cầu ít nhất A và B, C và D có thể trống
        required_answers = ['A', 'B']
        for j, label in enumerate(required_answers):
            if j + 1 < len(row):
                answer_value = row.iloc[j + 1]
                # Kiểm tra nếu là NaN hoặc chuỗi rỗng
                if (isinstance(answer_value, float) and pd.isna(answer_value)) or not str(answer_value).strip():
                    errors.append(f"Câu {row_num}: Thiếu đáp án {label} (bắt buộc)")
        
        # Cảnh báo nếu thiếu C hoặc D (không phải lỗi)
        optional_answers = ['C', 'D']
        missing_optional = []
        for j, label in enumerate(optional_answers, start=2):  # C=index 2, D=index 3
            if j + 1 < len(row):
                answer_value = row.iloc[j + 1]
                if (isinstance(answer_value, float) and pd.isna(answer_value)) or not str(answer_value).strip():
                    missing_optional.append(label)
        
        if missing_optional:
            warnings.append(f"Câu {row_num}: Không có đáp án {', '.join(missing_optional)} (câu chỉ có {4-len(missing_optional)} đáp án)")
        
        # Kiểm tra đáp án đúng
        correct_answer = row.iloc[-1]
        if (isinstance(correct_answer, float) and pd.isna(correct_answer)) or not str(correct_answer).strip():
            errors.append(f"Câu {row_num}: Thiếu đáp án đúng")
        else:
            correct_answers = parse_correct_answers(correct_answer)
            if not correct_answers:
                errors.append(f"Câu {row_num}: Đáp án đúng không hợp lệ - '{correct_answer}'")
            else:
                # Kiểm tra đáp án đúng có tồn tại không
                valid_options = ['A', 'B', 'C', 'D']
                if len(row) > 5:
                    e_value = row.iloc[5]
                    if not (isinstance(e_value, float) and pd.isna(e_value)) and str(e_value).strip():
                        valid_options.append('E')
                
                for ans in correct_answers:
                    if ans not in valid_options:
                        errors.append(f"Câu {row_num}: Đáp án đúng '{ans}' không tồn tại")
        
        # Cảnh báo câu hỏi quá ngắn
        if len(question_text) < 10:
            warnings.append(f"Câu {row_num}: Câu hỏi có vẻ quá ngắn")
    
    # Kiểm tra số thứ tự câu hỏi
    if question_numbers:
        # Sắp xếp theo số thứ tự trong câu hỏi
        sorted_questions = sorted(question_numbers, key=lambda x: x[1])
        
        missing_numbers = []
        duplicate_numbers = []
        large_jumps = []
        
        # Kiểm tra số trùng lặp
        seen_numbers = set()
        for row_num, q_num, q_text in question_numbers:
            if q_num in seen_numbers:
                duplicate_numbers.append(f"Số {q_num} (dòng {row_num}): {q_text}")
            else:
                seen_numbers.add(q_num)
        
        # Kiểm tra số thiếu và nhảy số bất thường
        if len(sorted_questions) > 1:
            for i in range(len(sorted_questions) - 1):
                current_num = sorted_questions[i][1]
                next_num = sorted_questions[i + 1][1]
                diff = next_num - current_num
                
                if diff > 1:
                    # Có số bị thiếu
                    missing_range = list(range(current_num + 1, next_num))
                    if diff > 5:  # Nhảy số quá lớn (hơn 5)
                        large_jumps.append(f"Nhảy từ câu {current_num} đến câu {next_num} (thiếu {len(missing_range)} câu: {missing_range})")
                    else:
                        missing_numbers.extend(missing_range)
        
        # Báo cáo lỗi về số thứ tự
        if duplicate_numbers:
            errors.append("📋 Phát hiện số câu trùng lặp:")
            for dup in duplicate_numbers:
                errors.append(f"  • {dup}")
        
        if missing_numbers:
            # Sắp xếp và nhóm số thiếu liên tiếp
            missing_sorted = sorted(set(missing_numbers))
            missing_ranges = []
            start = missing_sorted[0]
            end = missing_sorted[0]
            
            for i in range(1, len(missing_sorted)):
                if missing_sorted[i] == end + 1:
                    end = missing_sorted[i]
                else:
                    if start == end:
                        missing_ranges.append(str(start))
                    else:
                        missing_ranges.append(f"{start}-{end}")
                    start = end = missing_sorted[i]
            
            if start == end:
                missing_ranges.append(str(start))
            else:
                missing_ranges.append(f"{start}-{end}")
            
            warnings.append(f"📝 Thiếu câu số: {', '.join(missing_ranges)} (tổng cộng {len(missing_numbers)} câu)")
        
        if large_jumps:
            warnings.append("� Phát hiện nhảy số bất thường:")
            for jump in large_jumps:
                warnings.append(f"  • {jump}")
        
        # Tìm và báo cáo các khoảng trống lớn
        if len(sorted_questions) > 1:
            all_gaps = []
            for i in range(len(sorted_questions) - 1):
                current_num = sorted_questions[i][1]
                next_num = sorted_questions[i + 1][1]
                current_row = sorted_questions[i][0]
                next_row = sorted_questions[i + 1][0]
                
                if next_num - current_num > 1:
                    gap_size = next_num - current_num - 1
                    missing_range = list(range(current_num + 1, next_num))
                    all_gaps.append(f"Giữa dòng {current_row} (câu {current_num}) và dòng {next_row} (câu {next_num}): thiếu {gap_size} câu {missing_range}")
            
            if all_gaps:
                warnings.append("🔍 Chi tiết vị trí thiếu câu:")
                for gap in all_gaps:
                    warnings.append(f"  • {gap}")
        
        # Thông tin tổng quan về số thứ tự
        if question_numbers:
            min_num = min(q_num for _, q_num, _ in question_numbers)
            max_num = max(q_num for _, q_num, _ in question_numbers)
            total_range = max_num - min_num + 1
            actual_count = len(question_numbers)
            
            if total_range != actual_count:
                warnings.append(f"📋 Khoảng số: {min_num}-{max_num} ({total_range} câu) nhưng chỉ có {actual_count} câu trong file")
    
    return errors, warnings

def get_answer_content(question_row, answer_letter):
    """Lấy nội dung đầy đủ của đáp án từ chữ cái (A, B, C, D, E)"""
    if answer_letter == 'A':
        return question_row.iloc[1]
    elif answer_letter == 'B':
        return question_row.iloc[2]
    elif answer_letter == 'C':
        return question_row.iloc[3]
    elif answer_letter == 'D':
        return question_row.iloc[4]
    elif answer_letter == 'E':
        return question_row.iloc[5] if len(question_row) > 5 else ""
    return answer_letter

def parse_correct_answers(answer_str):
    """Phân tích đáp án đúng từ chuỗi"""
    if pd.isna(answer_str):
        return []
    
    answer_str = str(answer_str).upper().strip()
    import re
    answers = re.split(r'[,;\s]+', answer_str)
    valid_answers = [ans for ans in answers if ans in ['A', 'B', 'C', 'D', 'E']]
    return valid_answers

def select_questions_custom_range(df, start_row, end_row):
    """Chọn câu hỏi theo khoảng tùy chỉnh (từ dòng start_row đến end_row)"""
    # Chuyển đổi từ 1-indexed sang 0-indexed
    start_idx = start_row - 1
    end_idx = end_row
    
    if start_idx < 0:
        start_idx = 0
    if end_idx > len(df):
        end_idx = len(df)
    
    if start_idx >= end_idx:
        st.error("Dòng bắt đầu phải nhỏ hơn dòng kết thúc")
        return None
    
    return df.iloc[start_idx:end_idx].reset_index(drop=True)

def select_questions_random(df, num_questions):
    """Chọn câu hỏi ngẫu nhiên"""
    if num_questions > len(df):
        num_questions = len(df)
    
    selected_indices = random.sample(range(len(df)), num_questions)
    return df.iloc[selected_indices].reset_index(drop=True)

def main():
    st.title("📚 Ứng dụng luyện tập trắc nghiệm")
    st.markdown("---")
    
    # Khởi tạo session state
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = None
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'show_review' not in st.session_state:
        st.session_state.show_review = False
    if 'df_data' not in st.session_state:
        st.session_state.df_data = None
    if 'file_loaded' not in st.session_state:
        st.session_state.file_loaded = False
    
    # Sidebar cho cấu hình
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        
        # Hiển thị trạng thái file đã load
        if st.session_state.file_loaded:
            st.info(f"📄 Đã tải file với {len(st.session_state.df_data)} câu hỏi")
            if st.button("🗑️ Xóa file và tải file mới", type="secondary"):
                st.session_state.file_loaded = False
                st.session_state.df_data = None
                st.session_state.quiz_started = False
                st.session_state.quiz_completed = False
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.session_state.selected_questions = None
                st.rerun()
        
        # Tabs cho các phương thức tải file (chỉ hiển thị khi chưa load file)
        uploaded_file = None
        if not st.session_state.file_loaded:
            tab1, tab2 = st.tabs(["📁 Upload File", "🔗 Google Drive"])
            
            with tab1:
                # Upload file Excel hoặc TXT
                uploaded_file = st.file_uploader(
                    "Chọn file chứa câu hỏi",
                    type=['xlsx', 'xls', 'txt'],
                    help="Hỗ trợ:\n• File Excel (7 cột): Câu hỏi, A, B, C, D, E, Đáp án đúng\n• File TXT: Mỗi câu một dòng, các phần cách nhau bằng //"
                )
            
            with tab2:
                # Nhập link Google Drive
                gdrive_link = st.text_input(
                    "Nhập link Google Drive",
                    placeholder="https://drive.google.com/file/d/...",
                    help="Dán link chia sẻ Google Drive của file Excel hoặc TXT\nLưu ý: File phải được chia sẻ công khai hoặc cho phép mọi người xem"
                )
                
                # Button để tải file từ Google Drive
                load_gdrive = st.button("📥 Tải file từ Google Drive", type="primary")
                
                if load_gdrive and gdrive_link:
                    with st.spinner("Đang tải file từ Google Drive..."):
                        gdrive_file = download_from_gdrive(gdrive_link)
                        if gdrive_file:
                            # Xác định loại file từ link
                            if gdrive_link.lower().find('.xlsx') != -1 or gdrive_link.lower().find('.xls') != -1:
                                file_extension = 'xlsx'
                            elif gdrive_link.lower().find('.txt') != -1:
                                file_extension = 'txt'
                            else:
                                # Thử đoán dựa trên content
                                try:
                                    # Thử đọc như Excel trước
                                    pd.read_excel(gdrive_file)
                                    file_extension = 'xlsx'
                                except:
                                    file_extension = 'txt'
                            
                            # Xử lý file ngay và lưu vào session_state
                            if file_extension in ['xlsx', 'xls']:
                                df = load_excel_file(gdrive_file)
                            elif file_extension == 'txt':
                                df = load_txt_file(gdrive_file)
                            else:
                                st.error("Định dạng file không được hỗ trợ")
                                df = None
                            
                            if df is not None:
                                st.session_state.df_data = df
                                st.session_state.file_loaded = True
                                st.success("✅ Tải file thành công từ Google Drive!")
            
            # Xử lý file upload thông thường (từ tab 1)  
            if uploaded_file is not None:
                # Xác định loại file và đọc tương ứng
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension in ['xlsx', 'xls']:
                    df = load_excel_file(uploaded_file)
                elif file_extension == 'txt':
                    df = load_txt_file(uploaded_file)
                else:
                    st.error("Định dạng file không được hỗ trợ")
                    df = None
                
                if df is not None:
                    st.session_state.df_data = df
                    st.session_state.file_loaded = True        # Sử dụng dữ liệu từ session_state
        if st.session_state.file_loaded and st.session_state.df_data is not None:
            df = st.session_state.df_data
            
            st.success(f"✅ File hợp lệ: {len(df)} câu hỏi")
            
            # Kiểm tra lỗi dữ liệu
            errors, warnings = validate_questions_data(df)
            
            if errors:
                st.error("❌ Phát hiện lỗi trong dữ liệu:")
                with st.expander("🔍 Chi tiết lỗi", expanded=True):
                    for error in errors:
                        st.markdown(f"• {error}")
                st.markdown("**⚠️ Vui lòng sửa lỗi trước khi tiếp tục.**")
                return  # Dừng xử lý nếu có lỗi
            
            if warnings:
                st.warning("⚠️ Cảnh báo và gợi ý:")
                with st.expander("📋 Chi tiết cảnh báo", expanded=True):
                    for warning in warnings:
                            if "nhảy số bất thường" in warning.lower():
                                st.markdown(f"🚨 **{warning}**")
                            elif "thiếu câu số" in warning.lower():
                                st.markdown(f"📝 **{warning}**")
                            elif "khoảng số" in warning.lower():
                                st.markdown(f"📊 **{warning}**")
                            else:
                                st.markdown(f"• {warning}")
                    
                    # Hiển thị thêm bảng tóm tắt các vấn đề về số thứ tự
                    number_issues = [w for w in warnings if any(keyword in w.lower() for keyword in ["thiếu câu", "nhảy số", "khoảng số"])]
                    if number_issues:
                        st.info("💡 **Phân tích số thứ tự câu hỏi:**")
                        with st.expander("🔍 Chi tiết phân tích", expanded=False):
                            for issue in number_issues:
                                st.write(f"• {issue}")
                            st.markdown("""
                            **Gợi ý khắc phục:**
                            - ✅ Kiểm tra lại file gốc xem có câu nào bị thiếu
                            - ✅ Đảm bảo đánh số liên tục (1, 2, 3, 4...)
                            - ✅ Tìm và bổ sung câu bị thiếu
                            """)
                    
                    st.info("💡 Các cảnh báo trên chỉ mang tính thông tin, bạn vẫn có thể tiếp tục làm bài.")
                
                st.session_state.questions_df = df
                
                # Hiển thị preview toàn bộ đề thi
                with st.expander("🔍 Preview toàn bộ đề thi", expanded=False):
                    st.markdown("### 📋 Danh sách câu hỏi và đáp án")
                    for i, (_, row) in enumerate(df.iterrows()):
                        # Tạo HTML cho mỗi câu hỏi
                        question_html = f"""
                        <div style="background-color: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 4px solid #007bff;">
                            <div style="font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 12px;">
                                📝 Câu {i+1}: {row.iloc[0]}
                            </div>
                            <div style="margin-left: 20px; font-size: 16px;">
                                <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 5px;">
                                    <strong>A.</strong> {row.iloc[1] if row.iloc[1] and str(row.iloc[1]).strip() else ""}
                                </div>
                                <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 5px;">
                                    <strong>B.</strong> {row.iloc[2] if row.iloc[2] and str(row.iloc[2]).strip() else ""}
                                </div>
                                <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 5px;">
                                    <strong>C.</strong> {row.iloc[3] if row.iloc[3] and str(row.iloc[3]).strip() else ""}
                                </div>
                                <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 5px;">
                                    <strong>D.</strong> {row.iloc[4] if row.iloc[4] and str(row.iloc[4]).strip() else ""}
                                </div>
                        """
                        
                        # Thêm đáp án E nếu có
                        if len(row) > 5 and row.iloc[5] and str(row.iloc[5]).strip():
                            question_html += f"""
                                <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 5px;">
                                    <strong>E.</strong> {row.iloc[5]}
                                </div>
                            """
                        
                        # Thêm đáp án đúng
                        correct_answers = parse_correct_answers(row.iloc[-1])
                        correct_content = []
                        for ans in correct_answers:
                            content = get_answer_content(row, ans)
                            if content and str(content).strip():
                                correct_content.append(f"{ans}. {content}")
                            else:
                                correct_content.append(ans)
                        
                        question_html += f"""
                            </div>
                            <div style="margin-top: 15px; padding: 10px; background-color: #e8f5e8; border-radius: 5px; border-left: 4px solid #28a745;">
                                <strong style="color: #155724;">✅ Đáp án đúng:</strong><br>
                                <span style="color: #155724;">{' | '.join(correct_content)}</span>
                            </div>
                        </div>
                        """
                        
                        st.markdown(question_html, unsafe_allow_html=True)
                    
                    # Thống kê tổng quan
                    st.markdown("---")
                    st.markdown("### 📊 Thống kê")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Tổng số câu", len(df))
                    with col2:
                        # Đếm số câu có đáp án E
                        has_e = 0
                        for _, row in df.iterrows():
                            if len(row) > 5 and row.iloc[5] and str(row.iloc[5]).strip():
                                has_e += 1
                        st.metric("Câu có đáp án E", has_e)
                    with col3:
                        # Đếm số câu có nhiều đáp án đúng
                        multi_answer = sum(1 for _, row in df.iterrows() if len(parse_correct_answers(row.iloc[-1])) > 1)
                        st.metric("Câu nhiều đáp án", multi_answer)
                    with col4:
                        # Đếm số câu có đánh số
                        import re
                        numbered_questions = sum(1 for _, row in df.iterrows() if re.match(r'^\d+\.?\s*', str(row.iloc[0]).strip()))
                        st.metric("Câu có đánh số", numbered_questions)
                    
                    # Hiển thị bảng số thứ tự nếu có câu được đánh số
                    question_numbers = []
                    for i, (_, row) in enumerate(df.iterrows()):
                        question_text = str(row.iloc[0]).strip()
                        number_match = re.match(r'^(\d+)\.?\s*', question_text)
                        if number_match:
                            question_numbers.append({
                                'Dòng trong file': i + 1,
                                'Số câu': int(number_match.group(1)),
                                'Câu hỏi': question_text[:80] + "..." if len(question_text) > 80 else question_text
                            })
                    
                    if question_numbers:
                        st.markdown("### 🔢 Bảng số thứ tự câu hỏi")
                        with st.expander("📋 Chi tiết đánh số", expanded=False):
                            df_numbers = pd.DataFrame(question_numbers)
                            st.dataframe(df_numbers, use_container_width=True)
                            
                            # Tìm khoảng trống
                            sorted_nums = sorted([item['Số câu'] for item in question_numbers])
                            if len(sorted_nums) > 1:
                                gaps = []
                                for i in range(len(sorted_nums) - 1):
                                    if sorted_nums[i + 1] - sorted_nums[i] > 1:
                                        missing = list(range(sorted_nums[i] + 1, sorted_nums[i + 1]))
                                        gaps.append(f"Từ câu {sorted_nums[i]} đến {sorted_nums[i + 1]}: thiếu {missing}")
                                
                                if gaps:
                                    st.markdown("**🔍 Khoảng trống phát hiện:**")
                                    for gap in gaps:
                                        st.write(f"• {gap}")
                
                # Cấu hình bài thi
                st.subheader("🎯 Cấu hình bài thi")
                
                # Chọn kiểu chọn câu
                selection_mode = st.radio(
                    "Cách chọn câu hỏi:",
                    ["Ngẫu nhiên", "Tùy chỉnh khoảng dòng"]
                )
                
                if selection_mode == "Ngẫu nhiên":
                    num_questions = st.selectbox(
                        "Số câu muốn luyện:",
                        options=[10, 20, 30, 40, 50],
                        index=0
                    )
                    
                    if st.button("🚀 Bắt đầu làm bài (Ngẫu nhiên)", type="primary"):
                        selected_df = select_questions_random(df, num_questions)
                        st.session_state.selected_questions = selected_df
                        st.session_state.show_review = True
                        st.session_state.quiz_started = False
                        st.session_state.current_question = 0
                        st.session_state.user_answers = {}
                        st.session_state.quiz_completed = False
                        st.session_state.show_answer = False
                        st.rerun()
                
                else:  # Tùy chỉnh khoảng dòng
                    st.write("**Chọn khoảng dòng trong Excel:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        start_row = st.number_input("Từ dòng:", min_value=1, max_value=len(df), value=1)
                    with col2:
                        end_row = st.number_input("Đến dòng:", min_value=1, max_value=len(df), value=min(20, len(df)))
                    
                    if st.button("🚀 Bắt đầu làm bài (Tùy chỉnh)", type="primary"):
                        selected_df = select_questions_custom_range(df, start_row, end_row)
                        if selected_df is not None:
                            st.session_state.selected_questions = selected_df
                            st.session_state.show_review = True
                            st.session_state.quiz_started = False
                            st.session_state.current_question = 0
                            st.session_state.user_answers = {}
                            st.session_state.quiz_completed = False
                            st.session_state.show_answer = False
                            st.rerun()
    
    # Phần chính
    if st.session_state.show_review and st.session_state.selected_questions is not None:
        # Hiển thị review đề
        st.markdown("## 📋 Review đề thi")
        st.markdown(f"**Tổng số câu hỏi:** {len(st.session_state.selected_questions)} câu")
        
        # Hiển thị danh sách câu hỏi
        with st.expander("📝 Danh sách câu hỏi", expanded=True):
            for i, (_, row) in enumerate(st.session_state.selected_questions.iterrows()):
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 4px solid #007bff;">
                    <strong>Câu {i+1}:</strong> {row.iloc[0]}
                </div>
                """, unsafe_allow_html=True)
        
        # Nút bắt đầu làm bài
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Xác nhận và bắt đầu làm bài", type="primary", key="start_quiz"):
                st.session_state.quiz_started = True
                st.session_state.show_review = False
                st.rerun()
            
            if st.button("🔙 Quay lại chọn đề", key="back_to_selection"):
                st.session_state.show_review = False
                st.session_state.selected_questions = None
                st.rerun()
    
    elif not st.session_state.quiz_started:
        st.info("👆 Vui lòng upload file Excel và cấu hình bài thi ở sidebar để bắt đầu.")
        
        # Hiển thị hướng dẫn
        st.markdown("## 📖 Hướng dẫn sử dụng")
        st.markdown("""
        ### 📋 Cấu trúc file được hỗ trợ:
        
        **� File Excel (.xlsx, .xls) - Cấu trúc 7 cột:**
        - **Cột 1**: Câu hỏi
        - **Cột 2**: Đáp án A
        - **Cột 3**: Đáp án B  
        - **Cột 4**: Đáp án C
        - **Cột 5**: Đáp án D
        - **Cột 6**: Đáp án E (để trống nếu không có)
        - **Cột 7**: Đáp án đúng (A, B, C, D, E hoặc nhiều đáp án)
        
        **� File TXT (.txt) - Format mới:**
        - Mỗi câu hỏi một dòng
        - Các phần cách nhau bằng `//`
        - Cấu trúc: `Câu hỏi//A//B//C//D//E//Đáp án đúng`
        - Đáp án E trống: `Câu hỏi//A//B//C//D// //Đáp án đúng`
        
        **📝 Ví dụ file TXT:**
        ```
        2 + 2 = ?//3//4//5//6// //B
        Chọn ngôn ngữ lập trình://Python//HTML//JavaScript//CSS//Java//A,C,E
        ```
        
        ### ✨ Tính năng thông minh:
        - **Đáp án E tự động ẩn/hiện**: Chỉ hiển thị khi có dữ liệu
        - **Hỗ trợ nhiều đáp án đúng**: A,B hoặc B,C,D...
        - **Tự động phát hiện định dạng**: Excel hoặc TXT
        
        ### Cách sử dụng:
        1. Upload file Excel hoặc TXT
        2. Chọn **Ngẫu nhiên** (10-50 câu) hoặc **Tùy chỉnh khoảng dòng**
        3. Làm bài với checkbox (có thể chọn nhiều đáp án)
        4. Xem kết quả ngay lập tức và tổng kết cuối bài
        
        💡 **Mẹo**: File TXT dễ tạo và chỉnh sửa bằng notepad!
        """)
        
    else:
        if not st.session_state.quiz_completed:
            # Progress bar
            progress = st.session_state.current_question / len(st.session_state.selected_questions)
            st.progress(progress)
            
            # Layout 2 cột
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            # Cột trái - Đáp án
            with col1:
                st.markdown('<div class="section-title">📝 Các đáp án</div>', unsafe_allow_html=True)
                
                if not st.session_state.show_answer:
                    st.markdown("💡 **Có thể chọn nhiều đáp án**")
                
                current_q = st.session_state.selected_questions.iloc[st.session_state.current_question]
                
                # Lấy các đáp án
                options = []
                columns = st.session_state.selected_questions.columns.tolist()
                num_cols = len(columns)
                
                # Kiểm tra A, B (luôn hiển thị nếu có dữ liệu)
                for i, label in enumerate(['A', 'B']):
                    col_index = i + 1  # Cột 2, 3
                    if col_index < num_cols and not pd.isna(current_q.iloc[col_index]):
                        options.append(f"{label}. {current_q.iloc[col_index]}")
                
                # Kiểm tra C, D - chỉ hiển thị nếu có dữ liệu và không trống
                for i, label in enumerate(['C', 'D']):
                    col_index = i + 3  # Cột 4, 5
                    if col_index < num_cols and not pd.isna(current_q.iloc[col_index]) and str(current_q.iloc[col_index]).strip():
                        options.append(f"{label}. {current_q.iloc[col_index]}")
                
                # Kiểm tra E (cột 6) - chỉ hiển thị nếu có dữ liệu
                if num_cols >= 6:
                    e_col_index = 5  # Cột 6 (index 5)
                    if e_col_index < num_cols and not pd.isna(current_q.iloc[e_col_index]) and str(current_q.iloc[e_col_index]).strip():
                        # Kiểm tra xem cột 6 có phải là đáp án đúng không (file 6 cột)
                        if num_cols == 6:
                            # File 6 cột: cột 6 là đáp án đúng, không phải đáp án E
                            pass
                        else:
                            # File 7+ cột: cột 6 là đáp án E
                            options.append(f"E. {current_q.iloc[e_col_index]}")
                
                # Hiển thị checkboxes cho đáp án (có thể chọn nhiều)
                selected_answers = []
                
                # Tạo key duy nhất cho từng câu hỏi để tránh conflict
                question_key = f"q_{st.session_state.current_question}"
                
                # Reset checkbox state khi chuyển câu
                if f"{question_key}_reset" not in st.session_state:
                    st.session_state[f"{question_key}_reset"] = False
                
                for i, option in enumerate(options):
                    checkbox_key = f"{question_key}_{option[0]}_{i}"
                    
                    # Nếu đã trả lời, disable checkbox và hiển thị trạng thái đã chọn
                    if st.session_state.show_answer:
                        user_answer = st.session_state.user_answers.get(st.session_state.current_question, [])
                        is_checked = option[0] in user_answer
                        st.checkbox(
                            option, 
                            value=is_checked,
                            disabled=True,
                            key=f"{checkbox_key}_disabled"
                        )
                        if is_checked:
                            selected_answers.append(option[0])
                    else:
                        # Checkbox có thể chọn
                        if st.checkbox(option, key=checkbox_key):
                            selected_answers.append(option[0])
                
                # Nút xác nhận (chỉ hiển thị nếu chưa trả lời)
                if not st.session_state.show_answer:
                    if st.button("✅ Xác nhận đáp án", type="primary", key="confirm"):
                        if selected_answers:
                            st.session_state.user_answers[st.session_state.current_question] = selected_answers
                            st.session_state.show_answer = True
                            st.rerun()
                        else:
                            st.warning("Vui lòng chọn ít nhất một đáp án!")
                
                # Hiển thị feedback nếu đã trả lời
                if st.session_state.show_answer:
                    # Đáp án đúng ở cột cuối cùng
                    # - File 6 cột: đáp án đúng ở cột 6 (index 5)
                    # - File 7 cột: đáp án đúng ở cột 7 (index 6)
                    correct_answers = parse_correct_answers(current_q.iloc[-1])
                    user_answer = st.session_state.user_answers.get(st.session_state.current_question, [])
                    
                    if set(user_answer) == set(correct_answers):
                        st.markdown(f'''
                        <div class="feedback-box feedback-correct">
                            🎉 Chính xác! Đáp án đúng: {", ".join(correct_answers)}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="feedback-box feedback-incorrect">
                            ❌ Sai rồi!<br>
                            Bạn chọn: {", ".join(user_answer)}<br>
                            Đáp án đúng: {", ".join(correct_answers)}
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    # Nút tiếp theo
                    if st.session_state.current_question < len(st.session_state.selected_questions) - 1:
                        if st.button("➡️ Câu tiếp theo", type="primary", key="next"):
                            st.session_state.current_question += 1
                            st.session_state.show_answer = False
                            st.rerun()
                    else:
                        if st.button("🏁 Hoàn thành bài thi", type="primary", key="finish"):
                            st.session_state.quiz_completed = True
                            st.rerun()
            
            # Cột phải - Câu hỏi
            with col2:
                st.markdown('<div class="section-title">❓ Câu hỏi</div>', unsafe_allow_html=True)
                
                st.markdown(f'''
                <div class="progress-info">
                    Câu {st.session_state.current_question + 1} / {len(st.session_state.selected_questions)}
                </div>
                ''', unsafe_allow_html=True)
                
                st.markdown(f'''
                <div class="question-text">
                    {current_q.iloc[0]}
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Hiển thị kết quả cuối cùng
            st.markdown("## 📊 Kết quả bài làm")
            
            total_questions = len(st.session_state.selected_questions)
            correct_count = 0
            
            # Tính điểm
            for i in range(total_questions):
                current_q = st.session_state.selected_questions.iloc[i]
                # Đáp án đúng ở cột cuối cùng
                correct_answers = parse_correct_answers(current_q.iloc[-1])
                user_answer = st.session_state.user_answers.get(i, [])
                
                if set(user_answer) == set(correct_answers):
                    correct_count += 1
            
            score_percentage = (correct_count / total_questions) * 100
            
            # Hiển thị điểm
            if score_percentage >= 80:
                color = "#28a745"
                message = "Xuất sắc! 🎉"
            elif score_percentage >= 60:
                color = "#ffc107"
                message = "Khá tốt! 👍"
            else:
                color = "#dc3545"
                message = "Cần cố gắng thêm! 💪"
            
            st.markdown(f'''
            <div style="background-color: {color}20; border: 3px solid {color}; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
                <h2 style="color: {color}; margin-bottom: 15px;">{message}</h2>
                <h1 style="color: {color};">Điểm số: {correct_count}/{total_questions} ({score_percentage:.1f}%)</h1>
            </div>
            ''', unsafe_allow_html=True)
            
            # Chi tiết từng câu
            st.markdown("### 📝 Chi tiết bài làm")
            
            for i in range(total_questions):
                current_q = st.session_state.selected_questions.iloc[i]
                correct_answers = parse_correct_answers(current_q.iloc[-1])
                user_answer = st.session_state.user_answers.get(i, [])
                is_correct = set(user_answer) == set(correct_answers)
                
                icon = "✅" if is_correct else "❌"
                bg_color = "#d4edda" if is_correct else "#f8d7da"
                
                # Lấy nội dung đầy đủ của đáp án đúng
                correct_answer_contents = []
                for ans in correct_answers:
                    content = get_answer_content(current_q, ans)
                    if content and str(content).strip():
                        correct_answer_contents.append(f"{ans}. {content}")
                    else:
                        correct_answer_contents.append(ans)
                
                # Hiển thị với font size lớn hơn
                st.markdown(f'''
                <div style="background-color: {bg_color}; padding: 25px; border-radius: 15px; margin: 15px 0; border-left: 6px solid {'#28a745' if is_correct else '#dc3545'}; font-size: 18px;">
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 15px;">
                        {icon} Câu {i+1}: {current_q.iloc[0]}
                    </div>
                    <div style="margin-bottom: 10px; font-size: 18px;">
                        <strong>Đáp án của bạn:</strong> {", ".join(user_answer) if user_answer else "Không chọn"}
                    </div>
                    <div style="font-size: 18px; line-height: 1.5;">
                        <strong>Đáp án đúng:</strong><br>
                        {"<br>".join(correct_answer_contents)}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Nút làm lại
            if st.button("🔄 Làm bài mới", type="primary"):
                st.session_state.quiz_started = False
                st.session_state.show_review = False
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.session_state.quiz_completed = False
                st.session_state.show_answer = False
                st.session_state.selected_questions = None
                st.rerun()

if __name__ == "__main__":
    main()
