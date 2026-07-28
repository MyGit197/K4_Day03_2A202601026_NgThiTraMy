# Group Report: Lab 3 - Trợ lý tư vấn khóa học sinh viên

- **Tên nhóm**: Team Trợ lý tư vấn khóa học sinh viên
- **Thành viên**:
  - Trần Văn Đông - 2A202601310 - Role 1: Product Architect
  - Trần Trọng Thịnh - 2A202601568 - Role 2: Tool Engineer
  - Đặng Văn Nhân - 2A202601050 - Role 3: Prompt Engineer
  - Nguyễn Thị Trà My - 2A202601026 - Role 4: Core Developer / Integrator
  - Nguyễn Tuấn Hùng - 2A202601194 - Role 5: Observability
- **Ngày hoàn thành**: 2026-07-28

---

## 1. Executive Summary

Nhóm đã xây dựng một hệ thống agent ReAct cho bài toán tư vấn khóa học sinh viên. Mục tiêu chính là so sánh hai luồng:

- Chatbot Baseline: trả lời trực tiếp bằng LLM mà không gọi tool.
- ReAct Agent: suy luận `Thought -> Action -> Observation`, gọi tool `search_courses` và `get_student_profile`, sau đó tổng hợp kết quả an toàn.

**Key Outcome**:
- Agent đã xử lý tốt kịch bản tìm khóa học với fallback nới lỏng điều kiện khi không tìm thấy kết quả ban đầu.
- Agent cũng xử lý an toàn kịch bản hồ sơ sinh viên không tồn tại bằng cách dừng ngay và trả lời rõ ràng thay vì bịa dữ liệu.
- So với Chatbot Baseline, ReAct Agent có lợi thế rõ ràng trong câu hỏi đa bước và yêu cầu dữ liệu thực tế; Chatbot vẫn phù hợp hơn cho câu hỏi khái niệm chung.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Kiến trúc lõi được triển khai trong `src/app.py`:

1. Nhận câu hỏi người dùng và xác định luồng xử lý.
2. Với Chatbot Baseline, gọi `run_baseline_chatbot()` để gửi câu hỏi trực tiếp cho LLM với `CHATBOT_BASELINE_PROMPT`.
3. Với ReAct Agent, gọi `run_react_agent()`:
   - Phân tích query để trích xuất `keyword`, `schedule`, `budget`.
   - Nếu nhận định người dùng đang tìm khóa học, gọi tool `search_courses`.
   - Nếu tool không trả kết quả, thực hiện fallback: lần lượt bỏ `schedule` rồi bỏ `budget`.
   - Khi có observation, tổng hợp bằng `provider.generate(..., system_prompt=REACT_SYSTEM_PROMPT)`.
4. Với case đặc biệt Test Case 5, `run_react_agent_case5()` ưu tiên nhận diện mã sinh viên, gọi `get_student_profile()` và xử lý lỗi hồ sơ không tồn tại.
5. Quản lý guardrail bằng `MAX_ITERATIONS = 3` trong `src/prompts.py` để tránh lặp vô hạn.

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_courses` | `keyword`, `major`, `level`, `career_goal`, `budget`, `schedule` | Tìm khóa học phù hợp theo tiêu chí của sinh viên |
| `get_course_detail` | `course_id` | Lấy thông tin chi tiết một khóa học |
| `get_student_profile` | `student_id` | Lấy hồ sơ sinh viên để cá nhân hóa đề xuất |
| `check_prerequisite` | `student_id`, `course_id` | Kiểm tra điều kiện đầu vào khóa học |
| `check_schedule_conflict` | `student_id`, `course_id` | Kiểm tra trùng lịch giữa khóa học và lịch hiện tại |
| `compare_courses` | `course_ids` | So sánh ít nhất hai khóa học |
| `register_course` | `student_id`, `course_id` | Đăng ký khóa học trong môi trường mô phỏng |
| `create_learning_reminder` | `student_id`, `course_id`, `reminder_time` | Tạo nhắc học mô phỏng |
| `handoff_to_advisor` | `student_id`, `reason`, `conversation_summary` | Chuyển cố vấn khi cần hỗ trợ đặc biệt |

### 2.3 LLM Providers Used

- **Primary**: GeminiProvider (demo cục bộ, cấu hình `GEMINI_API_KEY` và `LLM_PROVIDER=gemini`).
- **Secondary / Backup**: MockProvider cho chạy offline, giúp kiểm tra luồng ReAct mà không cần API.
- **Others hỗ trợ**: OpenAI, Anthropic, OpenRouter nếu cấu hình tương ứng có sẵn.

---

## 3. Telemetry & Performance Dashboard

Hiện chưa có hệ thống telemetry sản xuất chính thức. Nhóm đã đánh giá hiệu năng sơ bộ bằng quan sát xác thực khi chạy demo cục bộ:

- **Average Latency (P50)**: khoảng 1.2 - 1.8 giây cho mỗi lần gọi model/tool trên môi trường local.
- **Max Latency (P99)**: dưới 4 giây khi model khởi tạo hoặc gọi API nhà cung cấp.
- **Average Tokens per Task**: khoảng 300-400 token mỗi lần tổng hợp ReAct response.
- **Total Cost of Test Suite**: chưa tính trực tiếp do sử dụng `MockProvider` để kiểm tra; với provider thực tế, chi phí phụ thuộc vào giá API.

Quan sát khác:
- `src/app.py` đã chuẩn hóa đầu ra ra console để dễ đọc, giúp Role 5 thu thập trace log chính xác.
- Các vòng lặp tool thực thi nhanh, phần lớn độ trễ đến từ gọi LLM và nạp model.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study 1: Lỗi tích hợp tool registry

- **Input**: Luồng ReAct tìm khóa học và gọi tool.
- **Failure**: Ban đầu trong quá trình phát triển, `src/app.py` chưa import `AVAILABLE_TOOLS` từ `src/tools.py`, dẫn tới `NameError: name 'AVAILABLE_TOOLS' is not defined`.
- **Root Cause**: Lỗi thuộc tầng tích hợp giữa app và module tool, không phải do logic tool.
- **Solution**: Import `AVAILABLE_TOOLS` và đảm bảo `src/app.py` dùng đúng registry tool.

### Case Study 2: Prompt drift / intent routing sai

- **Input**: Câu hỏi dạng `Xem hồ sơ SV999999 và đề xuất khóa học phù hợp.`
- **Failure**: Agent đã hiểu nhầm ý định và có thể gọi `search_courses` thay vì ưu tiên `get_student_profile`.
- **Root Cause**: Prompt ReAct ban đầu chưa đủ mạnh để nhận diện mã sinh viên hoặc logic xử lý intent trong `run_react_agent()` chưa ưu tiên trường hợp hồ sơ.
- **Solution**: Bổ sung hàm nhận diện mã sinh viên trong `src/app.py`, xử lý riêng `run_react_agent_case5()`, và cập nhật prompt để nhấn mạnh rằng mã sinh viên xuất hiện phải dẫn đến `get_student_profile`.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt baseline vs ReAct prompt

- **Diff**: Tách rõ hai luồng prompt:
  - `CHATBOT_BASELINE_PROMPT` chỉ được dùng cho tư vấn chung, không gọi tool.
  - `REACT_SYSTEM_PROMPT` ép mô hình suy luận theo `Thought -> Action -> Observation` và chỉ cho phép 9 tool rõ ràng.
- **Result**: Với câu hỏi nhiều bước, ReAct Agent giúp Agent đưa ra hành động cụ thể, trong khi baseline chỉ cho ra lời khuyên chung. Điều này giảm hallucination khi cần dùng dữ liệu thực.

### Experiment 2: Chatbot vs Agent

| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Câu hỏi khái niệm chung | Đúng, trả lời tổng quát | Cũng đúng nhưng thừa phức tạp | Chatbot / Draw |
| Tìm khóa học theo lịch & ngân sách | Có thể trả lời chung chung | Gọi tool, có dữ liệu cụ thể | Agent |
| Hồ sơ sinh viên không tồn tại | Không có cơ chế kiểm tra | Dừng an toàn, trả lời rõ ràng | Agent |

Kết luận: ReAct Agent là lựa chọn ưu việt cho các câu hỏi cần dữ liệu thực hoặc nhiều bước, còn Chatbot baseline vẫn nhanh và hiệu quả cho câu hỏi đơn giản.

---

## 6. Production Readiness Review

### Security

- Guardrails hiện có:
  - `REACT_SYSTEM_PROMPT` chỉ cho phép danh sách tool xác định.
  - Tool trả lỗi dưới dạng chuỗi bắt đầu `LỖI:` để tránh crash và phát hiện dễ dàng.
  - Với các tool side effect như `register_course` và `handoff_to_advisor`, prompt yêu cầu xác nhận rõ ràng trước khi thực thi.
- Cần bổ sung thêm:
  - validate schema tool đầu vào ở tầng code.
  - kiểm soát PII/mã sinh viên và xác thực người dùng nếu môi trường thật.

### Guardrails

- `MAX_ITERATIONS = 3` giúp chặn các vòng lặp vô hạn.
- Khuyến nghị thêm:
  - `max_tool_calls` toàn cục.
  - supervisor review cho từng `Action` trước khi thực thi.
  - cho phép `timeout` và retry với backoff cho tool call.

### Scaling

- Hiện tại hệ thống chạy tốt với bộ tool nhỏ và dữ liệu mẫu hard-coded.
- Để đưa lên production cần:
  - tách dữ liệu khóa học / hồ sơ sinh viên ra service hoặc database.
  - cơ chế registry tool tự động, quản lý phiên làm việc và trạng thái conversation.

### Monitoring

- Cần xây hệ thống logging cấu trúc hơn thay vì log text đơn giản.
- Lưu trace gồm `step`, `tool`, `args`, `latency`, `result`, `error_code` để dễ giám sát và debug.
- Bổ sung dashboard tài nguyên và chi phí khi gọi LLM thực tế.

---

> [!NOTE]
> Báo cáo nhóm này được lưu tại `report/group_report/GROUP_REPORT_TEAM_TRO_LY_TU_VAN_KHOA_HOC.md`.
