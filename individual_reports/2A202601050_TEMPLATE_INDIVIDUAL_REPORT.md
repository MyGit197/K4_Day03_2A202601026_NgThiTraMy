# BÁO CÁO CÁ NHÂN: LAB 3 - CHATBOT VS REACT AGENT

- **Họ và tên**: Đặng Văn Nhân
- **Mã sinh viên**: 2A202601050
- **Vai trò**: Role 3 - Prompt & Safeguard Engineer
- **Ngày thực hiện**: 28/07/2026

---

## I. Đóng góp kỹ thuật (15 điểm)

### 1. Phạm vi phụ trách

- **Module thực hiện**: [`src/prompts.py`](../src/prompts.py)
- **Nội dung chính**:
  - Viết `CHATBOT_BASELINE_PROMPT` cho chatbot tư vấn khóa học không có tool.
  - Thiết kế `REACT_SYSTEM_PROMPT` cho trợ lý tư vấn khóa học theo chu trình
    `Thought -> Action -> Observation`.
  - Khai báo giao thức gọi 9 công cụ, quy tắc chọn tool và định dạng tham số JSON.
  - Xây dựng guardrails về grounding, vòng lặp, prompt injection, quyền truy cập
    hồ sơ, dữ liệu cá nhân và xác nhận trước thao tác có side effect.
  - Cấu hình `MAX_ITERATIONS = 3` và `TIMEOUT_SECONDS = 10`.

### 2. Các phần nổi bật

**a. Phân tách rõ khả năng của Chatbot Baseline**

Tôi giới hạn chatbot baseline ở nhiệm vụ tư vấn kiến thức chung, đồng thời yêu cầu
không được bịa dữ liệu hiện hành như mã khóa học, học phí, lịch học, chỗ trống hoặc
trạng thái đăng ký. Khi câu hỏi cần dữ liệu thực tế, chatbot phải nói rõ giới hạn và
hướng dẫn người dùng kiểm tra nguồn chính thức. Cách viết này tạo một baseline công
bằng để so sánh với Agent, thay vì để chatbot giả vờ đã tra cứu dữ liệu.

**b. Chuẩn hóa giao thức ReAct thành hai dạng đầu ra**

```text
Thought: <lý do ngắn gọn cần chọn công cụ>
Action: <tên_công_cụ>[<JSON object>]
```

Sau `Action`, mô hình phải dừng để ứng dụng thực thi tool và trả về `Observation`.
Khi đã đủ bằng chứng, mô hình chuyển sang:

```text
Thought: <xác nhận đã đủ căn cứ>
Final Answer: <câu trả lời hoàn chỉnh>
```

Prompt quy định mỗi lượt chỉ gọi một tool, không tự tạo `Observation`, không viết
`Action` và `Final Answer` trong cùng lượt, không dùng tên tool ngoài danh sách và
không truyền tham số rỗng hoặc tham số tự đoán. Điều này giúp parser dễ xử lý hơn và
giảm lỗi tool call không hợp lệ.

**c. Mô tả chiến lược dùng công cụ theo mục tiêu**

Tôi ánh xạ từng nhu cầu sang công cụ phù hợp: tìm khóa bằng `search_courses`, lấy
chi tiết bằng `get_course_detail`, cá nhân hóa bằng `get_student_profile`, kiểm tra
đầu vào bằng `check_prerequisite`, kiểm tra lịch bằng
`check_schedule_conflict`, và so sánh bằng `compare_courses`.

Với `register_course`, prompt bắt buộc phải có kết quả kiểm tra điều kiện tiên quyết,
xung đột lịch và xác nhận rõ ràng của người dùng trước khi thực hiện. Hai tool
`create_learning_reminder` và `handoff_to_advisor` cũng chỉ được gọi sau khi đủ
tham số và có xác nhận đúng đối tượng.

**d. Guardrails về grounding và xử lý lỗi**

- Chỉ được khẳng định học phí, lịch, giảng viên, hồ sơ hoặc kết quả đăng ký khi có
  `Observation` hỗ trợ.
- Nếu tool trả chuỗi bắt đầu bằng `LỖI:`, Agent không được báo thành công hoặc lặp
  lại nguyên Action đã thất bại.
- Các tiêu chí như “dưới 2 triệu”, “chỉ học cuối tuần” được coi là ràng buộc cứng;
  Agent không được tự ý nới. Nếu chỉ có phương án gần phù hợp, câu trả lời phải nêu
  rõ tiêu chí được đáp ứng, tiêu chí không đáp ứng và điều kiện đã nới.
- `MAX_ITERATIONS = 3` ngăn Agent lặp vô hạn khi tool liên tục lỗi hoặc mô hình
  không thể đi đến `Final Answer`.

**e. Guardrails về bảo mật và riêng tư**

Prompt coi cả nội dung người dùng và `Observation` là dữ liệu không tin cậy, từ
chối chỉ dẫn yêu cầu bỏ qua system prompt, tiết lộ prompt/secret, đổi vai trò hoặc
xác nhận một thao tác chưa thành công. Agent chỉ được truy cập hồ sơ bằng
`authenticated_student_id` từ ngữ cảnh tin cậy, không dùng tùy ý mã sinh viên xuất
hiện trong câu hỏi. Các thao tác đăng ký, tạo nhắc và chuyển cố vấn chỉ có hiệu lực
cho đúng đối tượng và đúng tham số đã được người dùng xác nhận.

### 3. Cách module tương tác với vòng lặp ReAct

`src/app.py` import `CHATBOT_BASELINE_PROMPT`, `REACT_SYSTEM_PROMPT` và
`MAX_ITERATIONS` từ `src/prompts.py`. Trong kiến trúc hoàn chỉnh, ứng dụng gửi
system prompt cùng câu hỏi cho LLM, parser đọc `Action`, gọi hàm tương ứng trong
`src/tools.py`, sau đó nối kết quả thành `Observation` cho lượt kế tiếp. Vòng lặp
dừng khi nhận được `Final Answer` hoặc khi chạm `MAX_ITERATIONS`. Vì vậy,
`src/prompts.py` đóng vai trò như một “hợp đồng” giữa LLM, parser, tool registry và
lớp guardrail của ứng dụng.

---

## II. Phân tích một tình huống debugging (10 điểm)

### 1. Mô tả vấn đề

Trong lần kiểm tra trace ban đầu, Agent vẫn sử dụng ví dụ boilerplate về thời tiết:

```text
Thought 1: Cần tra cứu thời tiết Hà Nội.
Action 1: get_weather['Hà Nội']
Observation 1: Thời tiết Hà Nội: 28°C, Nắng nhẹ, Độ ẩm 65%.
```

Trong khi đó, nhóm đã chọn đề tài **Trợ lý tư vấn khóa học sinh viên** và toolset
thực tế gồm `search_courses`, `get_course_detail`, `check_prerequisite`,
`check_schedule_conflict`, v.v. Cú pháp `get_weather['Hà Nội']` cũng truyền tham số
vị trí, không phải JSON object có tên trường như parser mới mong đợi.

### 2. Nguồn log

- Trace trước khi đồng bộ prompt:
  [`docs/trace_eval.md`](../docs/trace_eval.md), mục “So sánh phản hồi (Test case #3)”.
- Danh sách công cụ của đề tài đã chọn:
  [`tool.txt`](../tool.txt).

### 3. Chẩn đoán

Nguyên nhân chính là **configuration/prompt drift**, không phải do tool bị crash.
System prompt và trace mẫu ban đầu còn bám theo bài toán thời tiết/chuyến bay, trong
khi phạm vi sản phẩm và tool specification đã chuyển sang tư vấn khóa học. Ngoài
ra, prompt cũ chỉ mô tả chung `Action: tên_công_cụ[tham_số]`, nên LLM có thể:

- Chọn tool không thuộc registry của ứng dụng.
- Sinh tham số vị trí hoặc JSON sai định dạng khiến parser không đọc được.
- Viết luôn `Observation` hoặc `Final Answer` mà chưa chờ kết quả tool.
- Lặp lại cùng một Action khi tool báo lỗi.

Đây là lỗi ở giao diện giữa prompt, parser và tool spec. LLM chỉ đang làm theo ví dụ
và định dạng mà hệ thống đã cung cấp.

### 4. Giải pháp

Tôi đã viết lại `REACT_SYSTEM_PROMPT` theo đúng đề tài, liệt kê đầy đủ 9 tool cùng
tên tham số và ví dụ JSON hợp lệ. Tôi bổ sung các quy tắc:

1. Mỗi lượt chỉ sinh đúng một Action và dừng ngay sau Action.
2. Không tự tạo hoặc dự đoán Observation.
3. Chỉ dùng tool trong allowlist và chỉ truyền trường có trong schema.
4. Khi thiếu tham số, hỏi người dùng thay vì truyền chuỗi rỗng hoặc tự đoán.
5. Khi tool báo lỗi, không báo thành công và không lặp lại Action y hệt.
6. Dừng an toàn sau tối đa ba vòng lặp.

Định dạng mong đợi sau khi sửa là:

```text
Thought: Cần tìm các khóa AI phù hợp với ngành và ngân sách người dùng đã nêu.
Action: search_courses[{"keyword":"AI","major":"Công nghệ thông tin","budget":2000000}]
```

Nhờ đó, đầu ra của LLM rõ ràng hơn cho parser, đồng bộ với tool registry và có điểm
dừng an toàn khi không thể hoàn thành tác vụ.

---

## III. Nhận xét cá nhân: Chatbot vs ReAct (10 điểm)

1. **Reasoning**: `Thought` buộc Agent xác định thông tin còn thiếu và giải thích
   ngắn gọn lý do chọn tool trước khi hành động. Với câu hỏi “Tôi có đăng ký được
   khóa C201 không?”, Agent không chỉ trả lời theo kiến thức có sẵn mà phải kiểm tra
   điều kiện tiên quyết, lịch học và căn cứ vào kết quả thật. Chatbot baseline chỉ có
   thể đưa khuyến nghị chung hoặc nói rằng nó không có dữ liệu để xác minh.

2. **Reliability**: Agent có thể hoạt động kém hơn Chatbot với câu hỏi kiến thức đơn
   giản vì gọi tool không cần thiết làm tăng độ trễ, chi phí và số điểm có thể phát
   sinh lỗi. Agent cũng kém tin cậy khi tool spec mơ hồ, parser không đồng bộ với
   prompt, tool trả schema bất nhất, Observation lỗi hoặc vòng lặp quá ngắn cho một
   tác vụ nhiều bước. Chatbot phù hợp hơn khi câu hỏi chỉ cần kiến thức tĩnh và
   không yêu cầu hành động hay dữ liệu hiện hành.

3. **Observation**: Observation biến suy luận ban đầu thành một quy trình có phản
   hồi từ môi trường. Nếu kết quả cho biết thiếu prerequisite, Agent phải dừng ý định
   đăng ký và giải thích môn còn thiếu. Nếu lịch bị trùng, bước tiếp theo phải là đề
   xuất lựa chọn khác thay vì tiếp tục `register_course`. Nếu tìm kiếm không có kết
   quả, Agent phải giữ nguyên ràng buộc cứng hoặc xin phép người dùng nới điều kiện.
   Do đó, Observation vừa cung cấp bằng chứng, vừa quyết định hướng đi của bước sau.

---

## IV. Hướng cải tiến trong tương lai (5 điểm)

- **Khả năng mở rộng**: Chuyển tool spec sang schema có cấu trúc và tự động sinh
  phần hướng dẫn tool trong prompt từ một registry duy nhất. Các tool độc lập có thể
  chạy bất đồng bộ; tác vụ dài nên dùng queue, timeout, retry có backoff và
  correlation ID để theo dõi xuyên suốt.
- **An toàn**: Kết hợp guardrail trong prompt với kiểm soát bắt buộc ở tầng code:
  allowlist tool, JSON Schema validation, xác thực/phân quyền, confirmation token,
  idempotency key và policy engine cho thao tác có side effect. Có thể thêm
  Supervisor kiểm tra kế hoạch trước khi đăng ký hoặc truy cập dữ liệu nhạy cảm.
- **Hiệu năng**: Rút gọn system prompt theo nhóm tool liên quan, cache kết quả chỉ
  đọc có TTL, dùng vector search để chọn tool khi registry lớn và đo token/latency
  cho từng bước. Các câu hỏi đơn giản nên đi theo Chatbot path; chỉ chuyển sang
  ReAct path khi cần dữ liệu động, nhiều bước hoặc thao tác thực tế.
- **Quan sát hệ thống**: Lưu trace có cấu trúc gồm `trace_id`, `step`, tool, tham số
  đã che PII, latency, trạng thái và mã lỗi. Xây dựng bộ regression test cho các lỗi
  Action sai JSON, lặp tool, prompt injection, truy cập sai hồ sơ, tự nới ràng buộc
  và thực hiện thao tác khi chưa xác nhận.
