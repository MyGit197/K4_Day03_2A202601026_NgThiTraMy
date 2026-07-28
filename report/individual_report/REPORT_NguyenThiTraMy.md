# Báo cáo cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Tên sinh viên**: Nguyễn Thị Trà My
- **Mã sinh viên**: 2A202601026
- **Ngày**: 2026-07-28

---

## I. Đóng góp kỹ thuật (15 điểm)

Trong vai trò Role 4, tôi chịu trách nhiệm chính về tích hợp lõi Agent và điều phối luồng ReAct cho ứng dụng.

- **Module thực hiện**:
  - `src/app.py`
  - `streamlit_app.py` (thêm giao diện demo Streamlit để tương tác và kiểm tra nhanh)

- **Những điểm nổi bật trong mã**:
  - Triển khai hàm `run_baseline_chatbot(user_query, provider)` để chạy luồng Chatbot Baseline với LLM chọn lọc, không gọi công cụ.
  - Triển khai hàm `run_react_agent(user_query, provider)` là luồng ReAct chính:
    - phân tích ý định người dùng và trích xuất `keyword`, `schedule`, `budget` từ câu hỏi
    - gọi tool `search_courses` để tìm khóa học phù hợp
    - thêm logic dự phòng (fallback) để nới lỏng điều kiện nếu không tìm thấy kết quả ban đầu
    - tích hợp `REACT_SYSTEM_PROMPT` để LLM tổng hợp kết quả sau khi có observation từ tool
    - đảm bảo đầu ra là trả lời thân thiện với người dùng, không lộ JSON tool thô.
  - Triển khai `run_react_agent_case5(user_query, provider)` xử lý riêng kịch bản Test Case 5:
    - nhận diện mã sinh viên trong câu hỏi
    - gọi `get_student_profile`
    - xử lý an toàn khi hồ sơ không tồn tại, tránh bịa thông tin hoặc tiếp tục sai
  - Thêm cơ chế guardrail `MAX_ITERATIONS` để chặn vòng lặp vô hạn và dừng an toàn khi không giải quyết được trong số bước tối đa.
  - Xây dựng `streamlit_app.py` để tạo UI demo: lựa chọn nhà cung cấp LLM, chọn câu mẫu, và chạy cả hai luồng Baseline và ReAct.

- **Tài liệu**:
  - Cập nhật `README.md` để hướng dẫn chạy demo Streamlit.
  - Ghi chú cách `src/app.py` tải bộ test từ `config/test_cases.json` và cách khởi tạo provider `get_llm_provider()`.
  - UI demo dùng lại hàm trong `src/app.py`, giúp kiểm chứng rõ ràng phần lõi agent của Role 4.

---

## II. Case study gỡ lỗi (10 điểm)

- **Mô tả vấn đề**:
  Khi thực hiện luồng ReAct cho Test Case 5, nếu tool `get_student_profile` trả về lỗi hồ sơ không tồn tại, agent cần dừng ngay và không tiếp tục lấy dữ liệu sai.

- **Nguồn log**:
  Console output trong `src/app.py` hiển thị:
  - `🧠 Thought: Đã tìm thấy mã sinh viên, tiến hành gọi tool kiểm tra hồ sơ.`
  - `👁️ Observation: LỖI: Không tìm thấy hồ sơ sinh viên 'SXXX'.`
  - `🏁 Final Answer: Tôi không thể xem được hồ sơ sinh viên này vì mã sinh viên không tồn tại...`

- **Chẩn đoán**:
  Vấn đề không phải do tool bị lỗi, mà do agent chưa xử lý đúng chuỗi trả về dạng lỗi. Khi observation bắt đầu bằng `LỖI:`, agent phải hiểu đó là trạng thái thất bại và trả về câu trả lời an toàn.

- **Giải pháp**:
  Tôi bổ sung phần xử lý trong `run_react_agent_case5()`:
  - dùng hàm trợ giúp `call_tool()` để kiểm soát lỗi và tránh crash
  - kiểm tra `observation.startswith("LỖI:")` và trả về kết luận an toàn
  - dừng luồng ReAct với một câu trả lời rõ ràng, giải thích rằng mã sinh viên không tồn tại hoặc chưa có hồ sơ

---

## III. Nhận định cá nhân: Chatbot vs ReAct (10 điểm)

1. **Khả năng suy luận**:
   Khối `Thought` giúp agent tách biệt bước suy nghĩ và bước hành động. ReAct buộc model phải quyết định trước khi gọi tool, ví dụ xác định người dùng muốn tìm khóa học rồi mới gọi `search_courses` với điều kiện đã phân tích.

2. **Độ tin cậy**:
   ReAct mạnh hơn khi cần dữ liệu cụ thể nhưng có thể kém hơn Chatbot trong trường hợp parser trích sai yêu cầu. Nếu agent hiểu sai điều kiện ngân sách hoặc lịch, nó có thể trả về "Không tìm thấy khóa phù hợp" thay vì đưa ra tư vấn chung, trong khi Chatbot vẫn trả lời được bằng kinh nghiệm tổng quát.

3. **Observation**:
   Phản hồi từ môi trường (tool observation) là bằng chứng thực tế. Khi `search_courses` trả kết quả, agent không được suy đoán thêm mà phải dựa vào dữ liệu đó. Trong hệ thống này, `REACT_SYSTEM_PROMPT` giúp LLM chuyển observation thành câu trả lời cụ thể cho người dùng.

---

## IV. Cải tiến tương lai (5 điểm)

- **Khả năng mở rộng**:
  - Áp dụng hàng đợi bất đồng bộ cho các cuộc gọi tool, để kiểm soát tốt hơn khi hệ thống có nhiều tool và nhiều yêu cầu cùng lúc.
  - Tách rõ các thành phần parsing, lựa chọn action và sinh phản hồi để dễ mở rộng và kiểm thử.

- **An toàn**:
  - Thêm lớp giám sát (supervisor) LLM để rà soát action trước khi thực thi.
  - Kiểm tra chặt chẽ schema tool và JSON đầu vào/ra để tránh lỗi do form sai hoặc tấn công injection.

- **Hiệu năng**:
  - Dùng vector DB hoặc lớp truy vấn để chọn công cụ và nội dung hồi đáp khi số lượng tool và dữ liệu lớn.
  - Cache các kết quả tool phổ biến để giảm số lần gọi LLM và tăng tốc phản hồi.

---
