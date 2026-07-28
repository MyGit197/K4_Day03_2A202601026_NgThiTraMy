# Báo cáo cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Tên sinh viên**: Trần Văn Đông
- **Mã sinh viên**: 2A202601310
- **Ngày**: 28/07/2026
- **Vai trò**: Role 1 - Product Architect
- **Chủ đề**: Đề số 7 - Trợ lý tư vấn khóa học sinh viên

---

## I. Đóng góp kỹ thuật (10 điểm)

### 1. Phạm vi phụ trách

- **Module thực hiện**: `config/test_cases.json`
- **Nhiệm vụ**: định hướng bài toán và xây dựng bộ câu hỏi kiểm thử dùng chung cho
  Chatbot Baseline và ReAct Agent.

Tôi chỉ phụ trách phần thiết kế test case. Phần tool, system prompt, ReAct loop và
trace report do các Role 2, 3, 4 và 5 thực hiện.

### 2. Bộ 5 test case đã xây dựng

| ID | Loại test | Mục đích |
|---:|---|---|
| 1 | Đơn giản - chỉ cần LLM | Kiểm tra khả năng giải thích khái niệm khóa học tiên quyết mà không gọi tool |
| 2 | Đơn giản - chỉ cần LLM | Kiểm tra khả năng phân biệt khóa bắt buộc và khóa tự chọn |
| 3 | Multi-step - cần 1 tool | Kiểm tra Agent tìm khóa Python theo trình độ, lịch học và ngân sách |
| 4 | Multi-step - cần 2 tools | Kiểm tra Agent lấy hồ sơ sinh viên rồi tìm khóa học phù hợp |
| 5 | Edge Case | Kiểm tra cách Agent xử lý mã sinh viên không tồn tại |

Hai câu đầu được thiết kế để chứng minh Chatbot vẫn phù hợp với câu hỏi kiến thức
chung. Hai câu tiếp theo yêu cầu dữ liệu từ hệ thống nên Agent phải gọi tool và sử
dụng Observation. Câu cuối cùng là đầu vào lỗi để kiểm tra khả năng dừng an toàn.

### 3. Expected behavior

Tôi bổ sung `expected_behavior` cho từng test case để nhóm có căn cứ so sánh output
thực tế:

- Test 1 và 2: trả lời trực tiếp, số lần gọi tool bằng 0.
- Test 3: gọi `search_courses` rồi trả lời từ dữ liệu tool.
- Test 4: gọi `get_student_profile`, sau đó gọi `search_courses`.
- Test 5: `get_student_profile` báo lỗi; Agent không được bịa hồ sơ hoặc tiếp tục
  tư vấn như thể dữ liệu tồn tại.

Ví dụ câu bẫy:

```json
{
  "id": 5,
  "category": "🔴 Edge Case (Bẫy Guardrail)",
  "question": "Xem hồ sơ SV999999 và đề xuất khóa học phù hợp.",
  "expected_behavior": "get_student_profile báo lỗi; Agent không bịa, không lặp và fallback an toàn."
}
```

---

## II. Phân tích một tình huống debugging (10 điểm)

### 1. Mô tả vấn đề

Khi chạy Test Case 5, kết quả thực tế không đi theo `expected_behavior`. Agent gọi
`search_courses` thay vì `get_student_profile`.

### 2. Failed trace

```text
Question: Xem hồ sơ SV999999 và đề xuất khóa học phù hợp.

Thought: Người dùng muốn tìm hoặc gợi ý khóa học.
Parsed intent -> keyword: 'xuất'
Action: search_courses(...)
Observation: LỖI: Không tìm thấy khóa học phù hợp với tiêu chí hiện tại.
Final Answer: Không tìm thấy khóa phù hợp với các tiêu chí đã cho.
```

### 3. Nhận xét từ góc độ thiết kế test

- **Expected**: Agent nhận diện yêu cầu xem hồ sơ và gọi
  `get_student_profile("SV999999")`.
- **Actual**: Agent hiểu nhầm từ `"đề xuất"` thành keyword `"xuất"` và gọi
  `search_courses`.
- Kết quả không crash và có fallback, nhưng vẫn FAIL vì chọn sai tool path.
- Qua đối chiếu dữ liệu, test dùng dạng mã `SV...` trong khi dữ liệu mẫu của tool
  dùng dạng `S...`. Đây là điểm cần được cả nhóm thống nhất trước khi nghiệm thu.

Vai trò của tôi trong tình huống này là dùng `expected_behavior` để phát hiện sai
lệch, ghi lại câu hỏi gây lỗi và chuyển failed trace cho Role 4/Role 5 phân tích,
không trực tiếp sửa parser hoặc tool.

---

## III. Nhận xét cá nhân: Chatbot vs ReAct (10 điểm)

1. **Reasoning**: Với câu hỏi đơn giản, Chatbot có thể trả lời trực tiếp và không
   cần chi phí điều phối tool. Với câu hỏi cá nhân hóa, Agent phải chia bài toán
   thành các bước lấy hồ sơ, tìm khóa học và tổng hợp kết quả.

2. **Reliability**: Agent không tự động tốt hơn Chatbot. Nếu chọn sai tool hoặc
   parser hiểu sai câu hỏi, Agent có thể trả lời sai hướng dù câu trả lời cuối vẫn
   lịch sự. Vì vậy test phải kiểm tra cả Action và Observation, không chỉ Final
   Answer.

3. **Observation**: Observation là bằng chứng để xác định Agent có grounding hay
   không. Các thông tin như tên khóa, học phí, lịch học và hồ sơ sinh viên chỉ được
   khẳng định khi tool đã trả về dữ liệu tương ứng.

---

## IV. Hướng cải tiến trong tương lai (5 điểm)

- Bổ sung trường `expected_tools` để chỉ rõ tên và thứ tự tool cần gọi.
- Bổ sung `max_tool_calls` để kiểm tra Agent có gọi thừa hoặc lặp tool hay không.
- Chuẩn hóa mã sinh viên giữa test case và dữ liệu mẫu trước khi chạy regression.
- Tự động lưu `actual_behavior` và trạng thái PASS/FAIL sau mỗi lần chạy.
- Chuẩn bị thêm câu hỏi cross-audit về input thiếu thông tin, mã không tồn tại và
  yêu cầu gọi tool ngoài danh sách.