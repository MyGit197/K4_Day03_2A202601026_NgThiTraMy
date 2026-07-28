# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Nguyễn Tuấn Hùng]
- **Student ID**: [2A202601194]
- **Date**: [28/07/2026]

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: [`docs/trace_eval.md` (Role 5 - Observability: Scoring Matrix & Trace Log) và phần hiển thị UI.]
- **Code Highlights**: 
  - Bảng chấm điểm Agentic Fit (Scoring Matrix 1-5 điểm cho 4 tiêu chí: Multi-step Reasoning, Tool Interaction, Dynamic Decision, Long Horizon) tại [trace_eval.md](docs/trace_eval.md#L7-L13), tổng điểm 18/20 → kết luận bài toán rất nên dùng ReAct Agent.
  - So sánh trực tiếp phản hồi Chatbot Baseline vs ReAct Agent trên Test Case #3 ("Tìm khóa Python cơ bản, học cuối tuần, học phí dưới 2 triệu") tại [trace_eval.md](docs/trace_eval.md#L20-L88), trích đầy đủ chuỗi `Thought -> Action -> Observation -> Final Answer`.
  - Về phần UI: Sử dụng streamlit, chuẩn hóa output console trong [app.py](src/app.py#L14-L18) bằng cách reconfigure `sys.stdout` sang `utf-8` và dùng emoji (🧠 Thought, 🛠️ Action, 👁️ Observation, 🏁 Final Answer) để log dễ đọc, dễ debug hơn khi trình chiếu demo.
- **Documentation**: [Trace log trong `docs/trace_eval.md` đóng vai trò "tấm gương" phản chiếu vòng lặp ReAct mà Role 4 lắp ráp trong `src/app.py`. Mỗi bước `Thought -> Action -> Observation` được Role 4 in ra console (qua các dòng `print()` có định dạng emoji tôi đề xuất) sẽ được tôi trích xuất, dán lại vào trace_eval.md kèm nhận xét (Nhận xét) để cả nhóm nhìn thấy rõ agent suy luận đúng/sai ở bước nào, từ đó phục vụ việc chấm điểm và cải tiến Guardrails.]


---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: [Khi demo trên terminal Windows, phần log UI (emoji + tiếng Việt có dấu) của `run_react_agent()` và `run_baseline_chatbot()` bị hiển thị lỗi ký tự (garbled text / dấu `?` thay cho chữ có dấu), khiến trace log trong lúc quan sát bị sai lệch, khó đối chiếu với nội dung đã dán vào `docs/trace_eval.md`.]
- **Log Source**: [Quan sát trực tiếp qua terminal khi chạy `python src/app.py`; log tham chiếu tại phần "🤖 [REACT AGENT]" và "💬 [CHATBOT BASELINE]" trong [app.py](src/app.py#L47-L82).]
- **Diagnosis**: [Không phải do prompt hay model, mà do encoding mặc định của console Windows (thường là `cp1252`/`cp437`) không hỗ trợ UTF-8, nên các ký tự tiếng Việt có dấu và emoji trong log bị in sai. Đây là lỗi tầng hiển thị (UI/console layer), không liên quan đến logic suy luận của ReAct Agent.]
- **Solution**: [Thêm đoạn kiểm tra và ép `sys.stdout.reconfigure(encoding='utf-8')` ngay đầu `app.py` (có bọc `try/except` để không crash trên môi trường không hỗ trợ), giúp toàn bộ log Thought/Action/Observation và Final Answer hiển thị đúng tiếng Việt có dấu và emoji, đảm bảo trace log ghi vào `docs/trace_eval.md` khớp 100% với những gì hiển thị trên console.]

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: [Khối `Thought` buộc Agent phải "nói ra" lý do trước khi hành động, nhờ đó khi kết quả tra cứu đầu tiên thất bại (Test Case #3, `Observation 1`: không tìm thấy khóa học khớp lịch cuối tuần), Agent có một `Thought 2` để tự nới lỏng điều kiện (bỏ `schedule`) và thử lại. Chatbot baseline không có cơ chế này nên chỉ đưa ra câu trả lời chung chung, mang tính "hướng dẫn tự tra cứu" thay vì tra cứu thật.]
2.  **Reliability**: [Trong trường hợp câu hỏi đơn giản, không cần dữ liệu thời gian thực (ví dụ hỏi khái niệm, định nghĩa), Agent có thể "worse" hơn Chatbot vì tốn thêm chi phí orchestration (nhiều vòng lặp Thought-Action) mà không mang lại giá trị, trong khi Chatbot trả lời ngay lập tức với 1 lệnh gọi LLM duy nhất.]
3.  **Observation**: [`Observation` chính là "bằng chứng thực tế" phản hồi lại cho Agent sau mỗi `Action`. Ở Test Case #3, `Observation 1` báo lỗi không có kết quả khớp buộc Agent phải điều chỉnh chiến lược ở `Thought 2` (nới lỏng tiêu chí lịch học) thay vì bịa ra một câu trả lời không có căn cứ — đây chính là điểm khác biệt cốt lõi so với Chatbot, vốn không có vòng phản hồi môi trường nào cả.]


---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: [Thay giao diện console hiện tại bằng UI web thực sự (Streamlit/Gradio hoặc React frontend + FastAPI backend) để nhiều người dùng có thể truy cập song song; dùng hàng đợi bất đồng bộ (async queue / Celery) cho các lệnh gọi tool để tránh nghẽn khi nhiều Agent chạy đồng thời.]
- **Safety**: [Tích hợp một 'Supervisor' LLM để kiểm duyệt (audit) từng `Action` trước khi Agent thực thi, kết hợp với `MAX_ITERATIONS` hiện có để chặn cả các hành vi bất thường lẫn vòng lặp vô hạn.]
- **Performance**: [Chuyển log dạng text thủ công (`docs/trace_eval.md`) sang hệ thống Observability chuẩn production (structured JSON log + dashboard như Grafana/Langfuse) để tự động tổng hợp Scoring Matrix thay vì ghi tay; dùng Vector DB để retrieval tool phù hợp khi hệ thống có hàng trăm tool thay vì if/else tuyến tính như hiện tại.]


---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.