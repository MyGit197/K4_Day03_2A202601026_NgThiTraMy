"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS, get_weather, search_flights
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def run_react_agent(user_query: str, provider):
    """
    Vòng lặp ReAct Agent đơn giản sử dụng các tool có sẵn trong AVAILABLE_TOOLS.
    Cải tiến: phân tích user_query để trích keyword, schedule và budget
    rồi gọi search_courses với fallback (loại trừ điều kiện nếu không tìm thấy).
    """
    import re

    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0

    # Helpers
    tools = AVAILABLE_TOOLS

    def call_tool(name: str, *args):
        func = tools.get(name)
        if not func:
            return f"LỖI: Tool '{name}' không có trong AVAILABLE_TOOLS."
        try:
            return func(*args)
        except Exception as e:
            return f"LỖI: Khi gọi tool '{name}': {e}"

    # Basic parsers
    def parse_keyword(q: str) -> str:
        # ưu tiên các từ khóa kỹ thuật phổ biến
        for term in ["python", "react", "machine learning", "ml", "sql", "power bi"]:
            if term in q:
                return term
        # fallback: lấy từ trước 'khóa' nếu có
        m = re.search(r"(\b[\wáàảãạăắằẵặâầấạèéẻẽẹêềếểễệ]+)\s+khóa", q)
        if m:
            return m.group(1)
        return ""

    def parse_schedule(q: str) -> str:
        weekend_terms = ["cuối tuần", "cuoi tuan", "thứ bảy", "thu bay", "chủ nhật", "chu nhat", "weekend"]
        for t in weekend_terms:
            if t in q:
                return "cuối tuần"
        if "tối" in q or "toi" in q:
            return "tối"
        if "sáng" in q or "sang" in q:
            return "sáng"
        return ""

    def parse_budget(q: str) -> str:
        # tìm các mẫu như 'dưới 2 triệu', 'dưới 2000k', '<=2 triệu', '2 triệu'
        m = re.search(r"(dưới|duoi|<|<=)\s*(\d+[\d\.,]*)\s*(triệu|trieu|k|nghìn|ngan)?", q)
        if m:
            num = m.group(2).replace(',', '.')
            unit = (m.group(3) or '').lower()
            if 'tri' in unit:
                return f"{num} triệu"
            if unit in ('k','nghìn','ngan'):
                return f"{num}k"
            return f"{num}"
        # try explicit like '2 triệu' without 'dưới' — interpret as max budget
        m2 = re.search(r"(\d+[\d\.,]*)\s*(triệu|trieu|k|nghìn|ngan)", q)
        if m2:
            num = m2.group(1).replace(',', '.')
            unit = m2.group(2).lower()
            if 'tri' in unit:
                return f"{num} triệu"
            return f"{num}k"
        return ""

    q_lower = user_query.lower()
    keyword = parse_keyword(q_lower)
    schedule = parse_schedule(q_lower)
    budget = parse_budget(q_lower)

    # Run a single-step ReAct loop focused on search_courses for discovery
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        if keyword or any(k in q_lower for k in ["tìm", "tư vấn", "gợi ý", "khóa", "khóa học", "có khóa nào"]):
            print("🧠 Thought: Người dùng muốn tìm hoặc gợi ý khóa học.")
            print(f"🧾 Parsed intent -> keyword: '{keyword}', schedule: '{schedule}', budget: '{budget}'")

            # 1) Thử tìm với tất cả điều kiện
            print("🛠️ Action: search_courses(keyword, '', '', '', budget, schedule)")
            obs = call_tool("search_courses", keyword, "", "", "", budget, schedule)
            print(f"👁️ Observation: {obs}")

            # 2) Nếu không tìm thấy, lặp qua các fallback: bỏ schedule -> bỏ budget -> chỉ keyword
            if obs.startswith("LỖI:"):
                print("🧠 Thought: Không có kết quả chính xác, thử nới lỏng điều kiện (bỏ schedule).")
                obs2 = call_tool("search_courses", keyword, "", "", "", budget, "")
                print(f"👁️ Observation (fallback - no schedule): {obs2}")
                if not obs2.startswith("LỖI:"):
                    try:
                        summary = provider.generate(f"Tóm tắt kết quả tìm khóa (nới lỏng lịch):\n{obs2}", system_prompt=REACT_SYSTEM_PROMPT)
                        print(f"🏁 Final Answer:\n{summary}")
                        return
                    except Exception:
                        print(f"🏁 Final Answer (raw):\n{obs2}")
                        return

                print("🧠 Thought: Vẫn chưa có, thử nới lỏng thêm (bỏ budget).")
                obs3 = call_tool("search_courses", keyword, "", "", "", "", "")
                print(f"👁️ Observation (fallback - keyword only): {obs3}")
                if not obs3.startswith("LỖI:"):
                    try:
                        summary = provider.generate(f"Tóm tắt kết quả tìm khóa (nới lỏng):\n{obs3}", system_prompt=REACT_SYSTEM_PROMPT)
                        print(f"🏁 Final Answer:\n{summary}")
                        return
                    except Exception:
                        print(f"🏁 Final Answer (raw):\n{obs3}")
                        return

                # Không tìm được bất kỳ kết quả nào
                print("🏁 Final Answer: Không tìm thấy khóa phù hợp với các tiêu chí đã cho. Bạn có muốn nới lỏng tiêu chí (ví dụ bỏ điều kiện 'cuối tuần' hoặc tăng ngân sách)?")
                return

            # Nếu có kết quả ngay từ đầu
            try:
                summary = provider.generate(f"Tóm tắt kết quả tìm khóa cho người dùng:\n{obs}", system_prompt=REACT_SYSTEM_PROMPT)
                print(f"🏁 Final Answer:\n{summary}")
                return
            except Exception:
                print(f"🏁 Final Answer (raw):\n{obs}")
                return

        # Nếu không dự đoán intent tìm khoá, chuyển sang các luồng khác đã có
        print("🧠 Thought: Không xác định intent tìm khóa rõ ràng, dùng LLM để trả lời tổng quát.")
        try:
            final = provider.generate(user_query, system_prompt=REACT_SYSTEM_PROMPT)
            print(f"🏁 Final Answer:\n{final}")
            return
        except Exception as exc:
            print(f"🏁 Final Answer (fallback text): Xin lỗi, không xử lý được yêu cầu: {exc}")
            return

    # Guardrail
    if step >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử câu test số 3
    sample_query = tests[4]["question"]
    
    # print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    # run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)
