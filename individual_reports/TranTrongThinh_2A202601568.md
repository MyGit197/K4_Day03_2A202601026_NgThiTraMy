# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trần Trọng Thịnh
- **Student ID**: 2A202601568
- **Date**: 28/07/2026
- **Role**: Role 2 - Tool Engineer
- **Topic**: Đề số 7 - Trợ lý tư vấn khóa học sinh viên

---

## I. Technical Contribution (15 Points)

- **Modules Implementated**: `src/tools.py`, `tool.txt`

- **Code Highlights**:
  - Thiết kế và triển khai bộ tool cho ReAct Agent gồm:
    `search_courses`, `get_course_detail`, `get_student_profile`,
    `check_prerequisite`, `check_schedule_conflict`, `register_course`,
    `create_learning_reminder`, `handoff_to_advisor`, `compare_courses`.
  - Bổ sung dữ liệu mẫu cho nhiều khóa học như Python, SQL/Power BI, Machine Learning, React, UI/UX, Cybersecurity, Data Storytelling và Research Skills.
  - Bổ sung hồ sơ sinh viên mẫu `S001` đến `S005` với ngành học, năm học, môn đã hoàn thành, mục tiêu nghề nghiệp, lịch học, ngân sách và phong cách học.
  - Chuẩn hóa lỗi bằng helper `_error()` để các tool luôn trả về chuỗi bắt đầu bằng `LỖI:` thay vì làm chương trình bị crash.
  - Bổ sung các helper xử lý dữ liệu như `_parse_budget`, `_matches_schedule`, `_schedule_conflicts`, `_missing_prerequisites`, `_course_summary`, `_course_detail_payload`.

- **Documentation**:
  - File `tool.txt` mô tả rõ mục đích, khi nào dùng, input/output, side effect và edge case production cho từng tool.
  - File `src/tools.py` có docstring chuẩn cho từng tool theo format: Name, Purpose, When to use, Input schema, Output schema, Error semantics, Side effects, Example, Safety.
  - Các tool được đăng ký trong `AVAILABLE_TOOLS` để `src/app.py` có thể gọi trong vòng lặp ReAct theo chuỗi `Thought -> Action -> Observation`.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  Trong quá trình chạy `python src/app.py`, Agent từng bị lỗi:
  `NameError: name 'AVAILABLE_TOOLS' is not defined`.
  Nguyên nhân là `src/app.py` sử dụng biến `AVAILABLE_TOOLS` trong `run_react_agent()` nhưng chưa import registry tool từ `src/tools.py`.

- **Log Source**:
  Terminal output:
  ```text
  NameError: name 'AVAILABLE_TOOLS' is not defined
  ```
  Sau đó, với câu hỏi `Xem hồ sơ SV999999 và đề xuất khóa học phù hợp`, Agent cũng từng gọi nhầm `search_courses` với keyword `"xuất"` thay vì gọi `get_student_profile`.

- **Diagnosis**:
  Lỗi đầu tiên là lỗi tích hợp giữa Role 2 và Role 4: tool registry đã có trong `src/tools.py`, nhưng app chưa import.
  Lỗi thứ hai là lỗi parser/intent routing trong `src/app.py`: câu hỏi có ý định xem hồ sơ sinh viên nhưng logic chỉ ưu tiên nhánh tìm khóa học.

- **Solution**:
  - Import `AVAILABLE_TOOLS` từ `tools`.
  - Thêm parser nhận dạng mã sinh viên như `SV002`, `S001`.
  - Ưu tiên gọi `get_student_profile(student_id)` trước khi đề xuất khóa học.
  - Nếu hồ sơ không tồn tại, Agent gọi `handoff_to_advisor` thay vì tự suy đoán.
  - Nếu hồ sơ tồn tại, Agent dùng ngành học, năm học, mục tiêu nghề nghiệp, ngân sách và lịch mong muốn để gọi `search_courses`.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: `Thought` giúp Agent chia bài toán thành từng bước rõ ràng. Ví dụ, với câu hỏi đề xuất khóa học cho sinh viên, Agent cần nghĩ rằng phải xem hồ sơ trước, sau đó mới tìm khóa phù hợp. Chatbot thông thường có thể trả lời chung chung mà không kiểm tra dữ liệu thật.

2. **Reliability**: Agent có thể kém hơn Chatbot nếu parser nhận sai intent hoặc gọi sai tool. Ví dụ, câu có cụm "đề xuất khóa học" từng bị parse nhầm keyword là `"xuất"`. Điều này cho thấy Agent mạnh hơn khi tool và routing đúng, nhưng dễ sai nếu thiết kế parser chưa chắc.

3. **Observation**: Observation từ tool giúp Agent không bịa dữ liệu. Nếu `get_student_profile("S999999")` trả `LỖI: Không tìm thấy hồ sơ`, Agent phải dừng tư vấn cá nhân hóa và chuyển cho tư vấn viên. Nếu Observation trả hồ sơ hợp lệ, Agent có bằng chứng để tiếp tục gọi `search_courses`.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Tách dữ liệu khóa học và sinh viên ra database hoặc API thay vì hard-code trong `src/tools.py`. Với nhiều tool hơn, nên có tool registry/schema tự động để Agent biết input/output chuẩn.

- **Safety**: Với các tool có side effect như `register_course` và `create_learning_reminder`, cần confirmation token hoặc bước xác nhận rõ ràng trước khi thực hiện. Các lỗi production nên dùng JSON envelope có `error_code`, `retryable`, `correlation_id`.

- **Performance**: Dùng cache cho `search_courses`, index tìm kiếm theo keyword/ngành/mục tiêu nghề nghiệp, và phân trang kết quả để tránh response quá dài. Nếu danh mục khóa học lớn, có thể dùng vector search hoặc ranking model để đề xuất khóa phù hợp hơn.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
