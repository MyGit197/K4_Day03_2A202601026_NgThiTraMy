"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)

Chủ đề: Đề số 7 - Trợ lý tư vấn khóa học sinh viên.

Nguyên tắc Role 2:
- Mỗi tool có mô tả rõ input/output/error.
- Mỗi tool luôn trả về chuỗi để ReAct Agent đưa vào Observation.
- Khi gặp lỗi, tool trả về chuỗi bắt đầu bằng "LỖI:" thay vì crash code.

Chuẩn docstring Mốc 2:
- Name: Tên tool/hàm.
- Purpose: Dùng để làm gì.
- When to use: Khi nào Agent nên gọi.
- Input schema: Kiểu và ý nghĩa tham số.
- Output schema: Dạng dữ liệu trả về khi thành công.
- Error semantics: Cách trả lỗi an toàn.
- Side effects: Có thay đổi dữ liệu hay không.
- Example: Ví dụ gọi hàm.
- Safety: Cam kết không crash khi gặp lỗi.
"""

from __future__ import annotations

import json
import re
from typing import Any


ERROR_PREFIX = "LỖI:"


def _error(message: str) -> str:
    """Tạo chuỗi lỗi thống nhất theo tool.txt: luôn bắt đầu bằng 'LỖI:'."""
    return f"{ERROR_PREFIX} {message}"


COURSES: dict[str, dict[str, Any]] = {
    "C101": {
        "title": "Python Cơ Bản Cho Sinh Viên",
        "description": "Nhập môn Python, tư duy thuật toán và bài tập thực hành.",
        "majors": ["all", "công nghệ thông tin", "khoa học dữ liệu", "kinh tế"],
        "level": "beginner",
        "year_fit": ["năm nhất", "năm hai"],
        "career_goals": ["ai engineer", "data analyst", "software engineer"],
        "fee": 1500000,
        "duration": "8 tuần",
        "instructor": "ThS. Nguyễn Minh Quân",
        "prerequisites": [],
        "certificate": "Chứng chỉ hoàn thành Python cơ bản",
        "schedule": "Tối thứ Ba và thứ Năm, 18:30-20:30",
        "schedule_type": "weekday_evening",
        "slots": [("Tue", "18:30", "20:30"), ("Thu", "18:30", "20:30")],
        "capacity_status": "Còn 12 chỗ",
        "tags": ["python", "lập trình", "coding", "năm nhất", "ai"],
    },
    "C102": {
        "title": "Phân Tích Dữ Liệu Với SQL và Power BI",
        "description": "Truy vấn SQL, làm sạch dữ liệu, dashboard Power BI và case study kinh doanh.",
        "majors": ["kinh tế", "quản trị kinh doanh", "khoa học dữ liệu", "all"],
        "level": "beginner",
        "year_fit": ["năm hai", "năm ba", "năm tư"],
        "career_goals": ["data analyst", "business analyst", "product analyst"],
        "fee": 1800000,
        "duration": "6 tuần",
        "instructor": "Ms. Trần Hải Anh",
        "prerequisites": ["Excel cơ bản"],
        "certificate": "Chứng chỉ Data Analysis Foundation",
        "schedule": "Sáng thứ Bảy, 08:00-11:00",
        "schedule_type": "weekend_morning",
        "slots": [("Sat", "08:00", "11:00")],
        "capacity_status": "Còn 8 chỗ",
        "tags": ["sql", "power bi", "data", "dashboard", "cuối tuần"],
    },
    "C201": {
        "title": "Machine Learning Cơ Bản",
        "description": "Supervised learning, đánh giá mô hình và mini project dự đoán dữ liệu.",
        "majors": ["công nghệ thông tin", "khoa học dữ liệu"],
        "level": "intermediate",
        "year_fit": ["năm hai", "năm ba", "năm tư"],
        "career_goals": ["ai engineer", "machine learning engineer", "data scientist"],
        "fee": 2500000,
        "duration": "10 tuần",
        "instructor": "Dr. Lê Phương Nam",
        "prerequisites": ["Python cơ bản", "Xác suất thống kê"],
        "certificate": "Chứng chỉ Machine Learning Foundation",
        "schedule": "Tối thứ Hai và thứ Tư, 18:30-20:30",
        "schedule_type": "weekday_evening",
        "slots": [("Mon", "18:30", "20:30"), ("Wed", "18:30", "20:30")],
        "capacity_status": "Còn 5 chỗ",
        "tags": ["machine learning", "ai", "ml", "python"],
    },
    "C202": {
        "title": "Web Development Với React",
        "description": "Xây dựng giao diện web hiện đại bằng React, component và state management.",
        "majors": ["công nghệ thông tin", "thiết kế tương tác"],
        "level": "intermediate",
        "year_fit": ["năm hai", "năm ba", "năm tư"],
        "career_goals": ["frontend developer", "software engineer", "web developer"],
        "fee": 2200000,
        "duration": "8 tuần",
        "instructor": "Mr. Phạm Tuấn Kiệt",
        "prerequisites": ["HTML/CSS cơ bản", "JavaScript cơ bản"],
        "certificate": "Chứng chỉ React Web Development",
        "schedule": "Chiều Chủ Nhật, 13:30-16:30",
        "schedule_type": "weekend_afternoon",
        "slots": [("Sun", "13:30", "16:30")],
        "capacity_status": "Còn 10 chỗ",
        "tags": ["react", "web", "frontend", "javascript", "cuối tuần"],
    },
    "C301": {
        "title": "AI Product Management",
        "description": "Thiết kế sản phẩm AI, đánh giá rủi ro, metric và phối hợp với team kỹ thuật.",
        "majors": ["quản trị kinh doanh", "công nghệ thông tin", "kinh tế", "all"],
        "level": "advanced",
        "year_fit": ["năm ba", "năm tư"],
        "career_goals": ["product manager", "ai product manager", "startup founder"],
        "fee": 1900000,
        "duration": "5 tuần",
        "instructor": "Ms. Đỗ Hoàng Linh",
        "prerequisites": [],
        "certificate": "Chứng chỉ AI Product Management",
        "schedule": "Tối thứ Sáu, 18:00-21:00",
        "schedule_type": "weekday_evening",
        "slots": [("Fri", "18:00", "21:00")],
        "capacity_status": "Còn 15 chỗ",
        "tags": ["ai", "product", "management", "startup"],
    },
    "C103": {
        "title": "Academic English For STEM",
        "description": "Đọc tài liệu kỹ thuật, viết email học thuật và thuyết trình dự án STEM.",
        "majors": ["all"],
        "level": "beginner",
        "year_fit": ["năm nhất", "năm hai", "năm ba", "năm tư"],
        "career_goals": ["research assistant", "software engineer", "data analyst", "all"],
        "fee": 1200000,
        "duration": "4 tuần",
        "instructor": "Ms. Rachel Nguyen",
        "prerequisites": [],
        "certificate": "Chứng chỉ Academic English for STEM",
        "schedule": "Sáng Chủ Nhật, 08:30-10:30",
        "schedule_type": "weekend_morning",
        "slots": [("Sun", "08:30", "10:30")],
        "capacity_status": "Còn 20 chỗ",
        "tags": ["english", "stem", "communication", "cuối tuần"],
    },
}


COURSES.update({
    "C104": {
        "title": "Kỹ Năng Học Đại Học và Quản Lý Thời Gian",
        "description": "Xây dựng phương pháp tự học, quản lý deadline, ghi chú hiệu quả và làm việc nhóm.",
        "majors": ["all"],
        "level": "beginner",
        "year_fit": ["năm nhất"],
        "career_goals": ["all", "academic success", "research assistant"],
        "fee": 900000,
        "duration": "3 tuần",
        "instructor": "Coach Vũ Hà My",
        "prerequisites": [],
        "certificate": "Chứng nhận Study Skills Foundation",
        "schedule": "Tối thứ Hai, 18:00-20:00",
        "schedule_type": "weekday_evening",
        "slots": [("Mon", "18:00", "20:00")],
        "capacity_status": "Còn 25 chỗ",
        "tags": ["study skills", "time management", "năm nhất", "kỹ năng mềm"],
        "mode": "offline",
        "language": "Tiếng Việt",
        "workload": "2-3 giờ/tuần",
        "project": "Lập kế hoạch học tập cá nhân 4 tuần",
        "outcomes": ["Quản lý deadline", "Ưu tiên công việc", "Tự đánh giá tiến độ"],
        "next_start": "2026-08-12",
        "rating": 4.6,
        "scholarship_available": True,
    },
    "C203": {
        "title": "Thiết Kế UI/UX Cho Sản Phẩm Số",
        "description": "Nghiên cứu người dùng, wireframe, prototype Figma và kiểm thử usability.",
        "majors": ["thiết kế tương tác", "công nghệ thông tin", "quản trị kinh doanh", "all"],
        "level": "intermediate",
        "year_fit": ["năm hai", "năm ba", "năm tư"],
        "career_goals": ["ux designer", "product designer", "product manager"],
        "fee": 2100000,
        "duration": "7 tuần",
        "instructor": "Ms. Phạm Ngọc Diệp",
        "prerequisites": [],
        "certificate": "Chứng chỉ UI/UX Product Design",
        "schedule": "Chiều thứ Bảy, 13:30-16:30",
        "schedule_type": "weekend_afternoon",
        "slots": [("Sat", "13:30", "16:30")],
        "capacity_status": "Còn 6 chỗ",
        "tags": ["ui", "ux", "figma", "product", "cuối tuần"],
        "mode": "hybrid",
        "language": "Tiếng Việt",
        "workload": "4-5 giờ/tuần",
        "project": "Prototype app đặt lịch cố vấn học tập",
        "outcomes": ["User research", "Wireframe", "Usability testing"],
        "next_start": "2026-08-24",
        "rating": 4.8,
        "scholarship_available": False,
    },
    "C204": {
        "title": "Cybersecurity Nhập Môn",
        "description": "Tư duy bảo mật, password hygiene, web security cơ bản và phòng chống phishing.",
        "majors": ["công nghệ thông tin", "khoa học dữ liệu", "all"],
        "level": "beginner",
        "year_fit": ["năm nhất", "năm hai", "năm ba"],
        "career_goals": ["security analyst", "software engineer", "it support"],
        "fee": 1700000,
        "duration": "6 tuần",
        "instructor": "Mr. Hoàng Việt Dũng",
        "prerequisites": ["Tin học đại cương"],
        "certificate": "Chứng chỉ Cybersecurity Awareness",
        "schedule": "Tối thứ Tư, 18:30-21:00",
        "schedule_type": "weekday_evening",
        "slots": [("Wed", "18:30", "21:00")],
        "capacity_status": "Còn 9 chỗ",
        "tags": ["security", "cybersecurity", "web", "phishing"],
        "mode": "online",
        "language": "Tiếng Việt",
        "workload": "3-4 giờ/tuần",
        "project": "Báo cáo audit bảo mật cá nhân",
        "outcomes": ["Nhận diện rủi ro", "Web security cơ bản", "An toàn tài khoản"],
        "next_start": "2026-09-02",
        "rating": 4.5,
        "scholarship_available": True,
    },
    "C302": {
        "title": "Data Storytelling và Thuyết Trình Dashboard",
        "description": "Biến insight dữ liệu thành câu chuyện, thiết kế slide và thuyết trình dashboard.",
        "majors": ["kinh tế", "quản trị kinh doanh", "khoa học dữ liệu", "all"],
        "level": "advanced",
        "year_fit": ["năm ba", "năm tư"],
        "career_goals": ["data analyst", "business analyst", "consultant"],
        "fee": 1600000,
        "duration": "4 tuần",
        "instructor": "Ms. Hà Thu Trang",
        "prerequisites": ["Excel cơ bản"],
        "certificate": "Chứng chỉ Data Storytelling",
        "schedule": "Tối thứ Năm, 18:30-20:30",
        "schedule_type": "weekday_evening",
        "slots": [("Thu", "18:30", "20:30")],
        "capacity_status": "Còn 14 chỗ",
        "tags": ["data", "storytelling", "presentation", "dashboard"],
        "mode": "offline",
        "language": "Tiếng Việt",
        "workload": "3 giờ/tuần",
        "project": "Thuyết trình dashboard phân tích hành vi sinh viên",
        "outcomes": ["Kể chuyện bằng dữ liệu", "Thiết kế slide", "Trình bày insight"],
        "next_start": "2026-08-29",
        "rating": 4.7,
        "scholarship_available": False,
    },
    "C303": {
        "title": "Nghiên Cứu Khoa Học Cho Sinh Viên",
        "description": "Đọc paper, đặt câu hỏi nghiên cứu, viết proposal và chuẩn bị poster học thuật.",
        "majors": ["all"],
        "level": "advanced",
        "year_fit": ["năm hai", "năm ba", "năm tư"],
        "career_goals": ["research assistant", "graduate study", "data scientist"],
        "fee": 2000000,
        "duration": "8 tuần",
        "instructor": "Dr. Mai Anh Khoa",
        "prerequisites": ["Academic English For STEM"],
        "certificate": "Chứng chỉ Undergraduate Research Skills",
        "schedule": "Sáng thứ Bảy, 09:00-11:30",
        "schedule_type": "weekend_morning",
        "slots": [("Sat", "09:00", "11:30")],
        "capacity_status": "Còn 4 chỗ",
        "tags": ["research", "paper", "proposal", "academic", "cuối tuần"],
        "mode": "hybrid",
        "language": "Song ngữ Việt-Anh",
        "workload": "5-6 giờ/tuần",
        "project": "Research proposal 2 trang và poster học thuật",
        "outcomes": ["Đọc paper", "Viết proposal", "Poster presentation"],
        "next_start": "2026-09-07",
        "rating": 4.9,
        "scholarship_available": True,
    },
})

COURSES["C101"].update({
    "mode": "offline",
    "language": "Tiếng Việt",
    "workload": "3-4 giờ/tuần",
    "project": "Ứng dụng quản lý todo bằng Python",
    "outcomes": ["Biến và kiểu dữ liệu", "Hàm", "Vòng lặp", "File I/O"],
    "next_start": "2026-08-15",
    "rating": 4.7,
    "scholarship_available": True,
})

COURSES["C102"].update({
    "mode": "hybrid",
    "language": "Tiếng Việt",
    "workload": "4 giờ/tuần",
    "project": "Dashboard phân tích doanh thu cửa hàng",
    "outcomes": ["SQL SELECT/JOIN", "Data cleaning", "Power BI dashboard"],
    "next_start": "2026-08-17",
    "rating": 4.6,
    "scholarship_available": True,
})

COURSES["C201"].update({
    "mode": "offline",
    "language": "Song ngữ Việt-Anh",
    "workload": "6-8 giờ/tuần",
    "project": "Mô hình dự đoán điểm rủi ro bỏ học",
    "outcomes": ["Train/test split", "Model evaluation", "Feature engineering"],
    "next_start": "2026-09-01",
    "rating": 4.8,
    "scholarship_available": False,
})

COURSES["C202"].update({
    "mode": "online",
    "language": "Tiếng Việt",
    "workload": "5 giờ/tuần",
    "project": "Portfolio cá nhân bằng React",
    "outcomes": ["Component", "State", "Props", "Deploy frontend"],
    "next_start": "2026-08-22",
    "rating": 4.5,
    "scholarship_available": False,
})

COURSES["C301"].update({
    "mode": "hybrid",
    "language": "Tiếng Anh",
    "workload": "3-5 giờ/tuần",
    "project": "AI product brief và risk checklist",
    "outcomes": ["Product discovery", "AI risk assessment", "Metric design"],
    "next_start": "2026-09-05",
    "rating": 4.4,
    "scholarship_available": True,
})

COURSES["C103"].update({
    "mode": "online",
    "language": "Tiếng Anh",
    "workload": "2-3 giờ/tuần",
    "project": "Slide thuyết trình mini research topic",
    "outcomes": ["Academic reading", "Technical email", "STEM presentation"],
    "next_start": "2026-08-10",
    "rating": 4.3,
    "scholarship_available": False,
})


STUDENTS: dict[str, dict[str, Any]] = {
    "S001": {
        "name": "Nguyễn Minh Anh",
        "major": "Công nghệ thông tin",
        "year": "năm nhất",
        "completed_courses": ["Tin học đại cương"],
        "strengths": ["logic", "tự học tốt", "toán"],
        "career_goal": "AI Engineer",
        "current_schedule": [("Tue", "18:30", "20:30"), ("Fri", "13:30", "15:30")],
    },
    "S002": {
        "name": "Trần Khánh Linh",
        "major": "Kinh tế",
        "year": "năm hai",
        "completed_courses": ["Excel cơ bản", "Thống kê ứng dụng"],
        "strengths": ["giao tiếp", "phân tích kinh doanh"],
        "career_goal": "Data Analyst",
        "current_schedule": [("Mon", "08:00", "10:00"), ("Thu", "13:30", "15:30")],
    },
    "S003": {
        "name": "Lê Hoàng Nam",
        "major": "Khoa học dữ liệu",
        "year": "năm ba",
        "completed_courses": ["Python cơ bản", "Xác suất thống kê", "SQL cơ bản"],
        "strengths": ["python", "thống kê", "làm project"],
        "career_goal": "Machine Learning Engineer",
        "current_schedule": [("Sat", "08:00", "11:00"), ("Wed", "13:30", "15:30")],
    },
}


STUDENTS.update({
    "S004": {
        "name": "Phạm Gia Hân",
        "major": "Thiết kế tương tác",
        "year": "năm hai",
        "completed_courses": ["Tin học đại cương", "Design Thinking"],
        "strengths": ["thẩm mỹ", "phỏng vấn người dùng", "thuyết trình"],
        "career_goal": "Product Designer",
        "current_schedule": [("Sat", "08:00", "10:00"), ("Tue", "13:30", "15:30")],
        "preferred_schedule": "cuối tuần",
        "budget_vnd": 2200000,
        "learning_style": "thực hành theo project",
    },
    "S005": {
        "name": "Đặng Minh Khang",
        "major": "Quản trị kinh doanh",
        "year": "năm ba",
        "completed_courses": ["Excel cơ bản", "Marketing căn bản", "Thống kê ứng dụng"],
        "strengths": ["giao tiếp", "kể chuyện", "phân tích thị trường"],
        "career_goal": "Product Manager",
        "current_schedule": [("Fri", "18:00", "21:00"), ("Sun", "13:30", "15:30")],
        "preferred_schedule": "tối trong tuần",
        "budget_vnd": 2000000,
        "learning_style": "case study và thảo luận",
    },
})

STUDENTS["S001"].update({
    "preferred_schedule": "tối trong tuần",
    "budget_vnd": 1800000,
    "learning_style": "học nền tảng chậm chắc và bài tập nhỏ",
})

STUDENTS["S002"].update({
    "preferred_schedule": "cuối tuần",
    "budget_vnd": 2000000,
    "learning_style": "case study kinh doanh và dashboard thực tế",
})

STUDENTS["S003"].update({
    "preferred_schedule": "tối trong tuần",
    "budget_vnd": 2600000,
    "learning_style": "project kỹ thuật và phản hồi code chi tiết",
})


def _to_json(data: Any) -> str:
    """
    Chuyển dữ liệu Python thành chuỗi JSON tiếng Việt dễ đọc.

    Args:
        data (Any): Dict/list/giá trị cần serialize.

    Returns:
        str: Chuỗi JSON dùng làm Observation cho Agent.
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as exc:
        return _error(f"Không thể chuyển dữ liệu sang JSON: {exc}")


def _normalize(value: Any) -> str:
    """
    Chuẩn hóa giá trị về chuỗi chữ thường để so khớp mềm.

    Args:
        value (Any): Giá trị bất kỳ cần chuẩn hóa.

    Returns:
        str: Chuỗi đã strip khoảng trắng và chuyển sang chữ thường.
    """
    try:
        return str(value).strip().lower()
    except Exception:
        return ""


def _get_course(course_id: Any) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """
    Lấy khóa học từ dữ liệu mẫu theo mã khóa học.

    Args:
        course_id (Any): Mã khóa học cần kiểm tra.

    Returns:
        tuple[str | None, dict[str, Any] | None, str | None]:
            Gồm mã đã chuẩn hóa, dữ liệu khóa học và thông báo lỗi nếu có.
    """
    if not isinstance(course_id, str):
        return None, None, _error("Thiếu mã khóa học hoặc mã khóa học không hợp lệ.")

    course_id_clean = course_id.strip().upper()
    if not course_id_clean:
        return None, None, _error("Thiếu mã khóa học hoặc mã khóa học không hợp lệ.")

    course = COURSES.get(course_id_clean)
    if course is None:
        return None, None, _error(f"Không tìm thấy khóa học có mã '{course_id_clean}'.")

    return course_id_clean, course, None


def _get_student(student_id: Any) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """
    Lấy hồ sơ sinh viên từ dữ liệu mẫu theo mã sinh viên.

    Args:
        student_id (Any): Mã sinh viên cần kiểm tra.

    Returns:
        tuple[str | None, dict[str, Any] | None, str | None]:
            Gồm mã đã chuẩn hóa, hồ sơ sinh viên và thông báo lỗi nếu có.
    """
    if not isinstance(student_id, str):
        return None, None, _error("Thiếu mã sinh viên hoặc mã sinh viên không hợp lệ.")

    student_id_clean = student_id.strip().upper()
    if not student_id_clean:
        return None, None, _error("Thiếu mã sinh viên hoặc mã sinh viên không hợp lệ.")

    student = STUDENTS.get(student_id_clean)
    if student is None:
        return None, None, _error(f"Không tìm thấy hồ sơ sinh viên '{student_id_clean}'.")

    return student_id_clean, student, None


def _parse_budget(budget: Any) -> tuple[int | None, str | None]:
    """
    Đọc ngân sách người dùng nhập thành số tiền VND.

    Args:
        budget (Any): Ngân sách dạng số hoặc chuỗi, ví dụ "2 triệu", "1500k".

    Returns:
        tuple[int | None, str | None]:
            Số tiền VND nếu đọc được và thông báo lỗi nếu input không hợp lệ.
    """
    if budget in ("", None):
        return None, None
    if isinstance(budget, (int, float)):
        if budget <= 0:
            return None, _error("Ngân sách không đọc được hoặc không hợp lệ.")
        if budget <= 100:
            return int(budget * 1_000_000), None
        return int(budget), None
    if not isinstance(budget, str):
        return None, _error("Ngân sách không đọc được hoặc không hợp lệ.")

    text = budget.strip().lower()
    if not text:
        return None, None

    match = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not match:
        return None, _error(f"Không đọc được ngân sách từ '{budget}'.")

    amount = float(match.group(1).replace(",", "."))
    if "triệu" in text or "trieu" in text or "tri" in text or text.endswith("m"):
        amount *= 1_000_000
    elif "k" in text or "nghìn" in text or "ngan" in text:
        amount *= 1_000
    elif 0 < amount <= 100:
        amount *= 1_000_000

    return int(amount), None


def _matches_keyword(course: dict[str, Any], keyword: str) -> bool:
    """
    Kiểm tra khóa học có khớp từ khóa tìm kiếm hay không.

    Args:
        course (dict[str, Any]): Dữ liệu một khóa học.
        keyword (str): Từ khóa đã chuẩn hóa.

    Returns:
        bool: True nếu khóa học khớp từ khóa hoặc người dùng không nhập từ khóa.
    """
    if not keyword:
        return True

    text = _normalize(
        " ".join([
            str(course.get("title", "")),
            str(course.get("description", "")),
            " ".join(course.get("tags", [])),
            " ".join(course.get("career_goals", [])),
        ])
    )

    if len(keyword) <= 2:
        tokens = set(re.findall(r"[\w]+", text, flags=re.UNICODE))
        return keyword in tokens

    return keyword in text


def _matches_schedule(course: dict[str, Any], schedule: str) -> bool:
    """
    Kiểm tra khóa học có khớp lịch học mong muốn hay không.

    Args:
        course (dict[str, Any]): Dữ liệu một khóa học.
        schedule (str): Lịch mong muốn, ví dụ "cuối tuần", "tối", "sáng".

    Returns:
        bool: True nếu lịch khóa học phù hợp với yêu cầu.
    """
    schedule_norm = _normalize(schedule)
    if not schedule_norm:
        return True

    schedule_type = course.get("schedule_type", "")
    schedule_text = _normalize(f"{course.get('schedule', '')} {schedule_type}")
    weekend_terms = ["cuối tuần", "cuoi tuan", "thứ bảy", "thu bay", "chủ nhật", "chu nhat", "weekend"]
    evening_terms = ["tối", "toi", "evening"]
    morning_terms = ["sáng", "sang", "morning"]

    if any(term in schedule_norm for term in weekend_terms):
        return "weekend" in schedule_type
    if any(term in schedule_norm for term in evening_terms):
        return "evening" in schedule_type
    if any(term in schedule_norm for term in morning_terms):
        return "morning" in schedule_type

    return schedule_norm in schedule_text


def _time_to_minutes(value: str) -> int:
    """
    Đổi thời gian dạng HH:MM sang tổng số phút trong ngày.

    Args:
        value (str): Thời gian dạng "18:30".

    Returns:
        int: Tổng số phút tính từ 00:00.
    """
    try:
        hour, minute = value.split(":")
        return int(hour) * 60 + int(minute)
    except Exception:
        return -1


def _slots_overlap(slot_a: tuple[str, str, str], slot_b: tuple[str, str, str]) -> bool:
    """
    Kiểm tra hai khung giờ có trùng nhau không.

    Args:
        slot_a (tuple[str, str, str]): Khung giờ thứ nhất dạng (day, start, end).
        slot_b (tuple[str, str, str]): Khung giờ thứ hai dạng (day, start, end).

    Returns:
        bool: True nếu cùng ngày và khoảng thời gian giao nhau.
    """
    try:
        day_a, start_a, end_a = slot_a
        day_b, start_b, end_b = slot_b
    except Exception:
        return False
    if day_a != day_b:
        return False
    start_a_minutes = _time_to_minutes(start_a)
    end_a_minutes = _time_to_minutes(end_a)
    start_b_minutes = _time_to_minutes(start_b)
    end_b_minutes = _time_to_minutes(end_b)
    if min(start_a_minutes, end_a_minutes, start_b_minutes, end_b_minutes) < 0:
        return False
    return start_a_minutes < end_b_minutes and start_b_minutes < end_a_minutes


def _missing_prerequisites(student: dict[str, Any], course: dict[str, Any]) -> list[str]:
    """
    Tìm các điều kiện đầu vào sinh viên còn thiếu.

    Args:
        student (dict[str, Any]): Hồ sơ sinh viên.
        course (dict[str, Any]): Dữ liệu khóa học.

    Returns:
        list[str]: Danh sách prerequisite chưa có trong hồ sơ sinh viên.
    """
    completed = {_normalize(item) for item in student.get("completed_courses", [])}
    return [item for item in course.get("prerequisites", []) if _normalize(item) not in completed]


def _schedule_conflicts(student: dict[str, Any], course: dict[str, Any]) -> list[dict[str, str]]:
    """
    Liệt kê các khung giờ khóa học bị trùng với lịch hiện tại của sinh viên.

    Args:
        student (dict[str, Any]): Hồ sơ sinh viên.
        course (dict[str, Any]): Dữ liệu khóa học.

    Returns:
        list[dict[str, str]]: Danh sách cặp khung giờ bị trùng.
    """
    conflicts = []
    for course_slot in course.get("slots", []):
        for student_slot in student.get("current_schedule", []):
            if _slots_overlap(course_slot, student_slot):
                conflicts.append({
                    "course_slot": f"{course_slot[0]} {course_slot[1]}-{course_slot[2]}",
                    "student_slot": f"{student_slot[0]} {student_slot[1]}-{student_slot[2]}",
                })
    return conflicts


def _fee_category(fee: Any) -> str:
    """
    Phân loại học phí để output dễ đọc hơn.

    Args:
        fee (Any): Học phí VND.

    Returns:
        str: Nhóm học phí thấp, trung bình hoặc cao.
    """
    try:
        fee_number = int(fee)
    except Exception:
        return "Chưa rõ"
    if fee_number <= 1_500_000:
        return "Thấp"
    if fee_number <= 2_200_000:
        return "Trung bình"
    return "Cao"


def _course_summary(course_id: str, course: dict[str, Any]) -> dict[str, Any]:
    """
    Tạo bản tóm tắt khóa học giàu thông tin cho search_courses.

    Args:
        course_id (str): Mã khóa học.
        course (dict[str, Any]): Dữ liệu khóa học.

    Returns:
        dict[str, Any]: Payload tóm tắt có nhiều trường để Agent tư vấn tốt hơn.
    """
    fee = course.get("fee", 0)
    return {
        "course_id": course_id,
        "title": course.get("title", "Chưa cập nhật tên khóa học"),
        "level": course.get("level", "Chưa cập nhật"),
        "fee_vnd": fee,
        "fee_category": _fee_category(fee),
        "duration": course.get("duration", "Chưa cập nhật"),
        "schedule": course.get("schedule", "Chưa cập nhật"),
        "schedule_type": course.get("schedule_type", "Chưa cập nhật"),
        "mode": course.get("mode", "offline"),
        "language": course.get("language", "Tiếng Việt"),
        "workload": course.get("workload", "Chưa cập nhật"),
        "project": course.get("project", "Bài tập thực hành cuối khóa"),
        "next_start": course.get("next_start", "Chưa cập nhật"),
        "rating": course.get("rating", "Chưa có đánh giá"),
        "scholarship_available": course.get("scholarship_available", False),
        "capacity_status": course.get("capacity_status", "Chưa cập nhật"),
        "skills": course.get("outcomes", course.get("tags", [])),
    }


def _course_detail_payload(course_id: str, course: dict[str, Any]) -> dict[str, Any]:
    """
    Tạo payload chi tiết khóa học với dữ liệu đa dạng.

    Args:
        course_id (str): Mã khóa học.
        course (dict[str, Any]): Dữ liệu khóa học.

    Returns:
        dict[str, Any]: Payload chi tiết dùng trong get_course_detail.
    """
    payload = _course_summary(course_id, course)
    payload.update({
        "status": "success",
        "description": course.get("description", "Chưa cập nhật mô tả."),
        "instructor": course.get("instructor", "Chưa cập nhật giảng viên"),
        "prerequisites": course.get("prerequisites", []),
        "certificate": course.get("certificate", "Chưa cập nhật chứng chỉ"),
        "majors": course.get("majors", []),
        "year_fit": course.get("year_fit", []),
        "career_goals": course.get("career_goals", []),
        "tags": course.get("tags", []),
    })
    return payload


def _student_profile_payload(student_id: str, student: dict[str, Any]) -> dict[str, Any]:
    """
    Tạo payload hồ sơ sinh viên giàu thông tin hơn.

    Args:
        student_id (str): Mã sinh viên.
        student (dict[str, Any]): Hồ sơ sinh viên.

    Returns:
        dict[str, Any]: Payload hồ sơ dùng trong get_student_profile.
    """
    return {
        "status": "success",
        "student_id": student_id,
        "name": student.get("name", "Chưa cập nhật"),
        "major": student.get("major", "Chưa cập nhật"),
        "year": student.get("year", "Chưa cập nhật"),
        "completed_courses": student.get("completed_courses", []),
        "strengths": student.get("strengths", []),
        "career_goal": student.get("career_goal", "Chưa cập nhật"),
        "current_schedule": [
            f"{day} {start}-{end}"
            for day, start, end in student.get("current_schedule", [])
        ],
        "preferred_schedule": student.get("preferred_schedule", "Chưa cập nhật"),
        "budget_vnd": student.get("budget_vnd", "Chưa cập nhật"),
        "learning_style": student.get("learning_style", "Chưa cập nhật"),
    }


def search_courses(
    keyword: str = "",
    major: str = "",
    level: str = "",
    career_goal: str = "",
    budget: str | int | float = "",
    schedule: str = "",
) -> str:
    """
    Tìm kiếm khóa học phù hợp với nhu cầu sinh viên.

    Name:
        search_courses

    Purpose:
        Lọc danh mục khóa học mẫu theo nhu cầu học tập, ngành học, trình độ,
        mục tiêu nghề nghiệp, ngân sách và lịch học mong muốn.

    When to use:
        Dùng khi sinh viên hỏi các câu như "Có khóa nào về AI không?",
        "Khóa nào phù hợp sinh viên năm nhất?", "Có khóa cuối tuần không?",
        hoặc "Có khóa nào dưới 2 triệu không?".

    Input schema:
        keyword (str): Từ khóa tìm kiếm, có thể rỗng.
        major (str): Ngành học của sinh viên, có thể rỗng.
        level (str): Trình độ/năm học, ví dụ "beginner", "năm nhất".
        career_goal (str): Mục tiêu nghề nghiệp, ví dụ "Data Analyst".
        budget (str | int | float): Ngân sách tối đa, ví dụ "2 triệu" hoặc 2000000.
        schedule (str): Lịch mong muốn, ví dụ "cuối tuần", "tối".

    Output schema:
        str: Chuỗi JSON có status="success", count và courses. Mỗi phần tử trong
        courses gồm course_id, title, level, fee_vnd, schedule, capacity_status.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu tham số sai kiểu, ngân sách không
        đọc được, ngân sách <= 0, hoặc không có khóa học phù hợp.

    Side effects:
        Không thay đổi dữ liệu, không đăng ký khóa học, không gọi API ngoài.

    Example:
        search_courses(keyword="AI", budget="2 triệu")

    Safety:
        Hàm được bọc try/except và luôn trả về str; lỗi runtime được chuyển thành
        thông báo "LỖI:" để Agent quan sát và xử lý tiếp.

    Args:
        keyword (str): Từ khóa, ví dụ "AI", "Python", "cuối tuần".
        major (str): Ngành học, ví dụ "Công nghệ thông tin".
        level (str): Trình độ/năm học, ví dụ "beginner", "năm nhất".
        career_goal (str): Mục tiêu nghề nghiệp.
        budget (str | int | float): Ngân sách tối đa, ví dụ "2 triệu" hoặc 2000000.
        schedule (str): Lịch mong muốn, ví dụ "cuối tuần", "tối".

    Returns:
        str: JSON danh sách khóa học phù hợp hoặc chuỗi "LỖI: ..." nếu không tìm thấy/sai tham số.
    """
    try:
        for name, value in {
            "keyword": keyword,
            "major": major,
            "level": level,
            "career_goal": career_goal,
            "schedule": schedule,
        }.items():
            if not isinstance(value, str):
                return _error(f"Sai kiểu dữ liệu cho tham số '{name}'.")

        max_budget, budget_error = _parse_budget(budget)
        if budget_error:
            return budget_error

        keyword_norm = _normalize(keyword)
        major_norm = _normalize(major)
        level_norm = _normalize(level)
        career_norm = _normalize(career_goal)
        results = []

        for course_id, course in COURSES.items():
            if not _matches_keyword(course, keyword_norm):
                continue
            course_majors = course.get("majors", [])
            course_level = course.get("level", "")
            course_year_fit = course.get("year_fit", [])
            course_goals = course.get("career_goals", [])
            course_fee = course.get("fee", 0)
            try:
                course_fee_number = int(course_fee)
            except Exception:
                course_fee_number = 0

            if major_norm and "all" not in course_majors and not any(major_norm in _normalize(item) for item in course_majors):
                continue
            if level_norm and level_norm not in _normalize(course_level) and not any(level_norm in _normalize(item) for item in course_year_fit):
                continue
            if career_norm and "all" not in course_goals and not any(career_norm in _normalize(item) for item in course_goals):
                continue
            if max_budget is not None and course_fee_number > max_budget:
                continue
            if not _matches_schedule(course, schedule):
                continue

            summary = _course_summary(course_id, course)
            summary["match_reason"] = "Khớp với các tiêu chí tìm kiếm đã cung cấp."
            results.append(summary)

        if not results:
            return _error("Không tìm thấy khóa học phù hợp với tiêu chí hiện tại.")

        return _to_json({"status": "success", "count": len(results), "courses": results})
    except Exception as exc:
        return _error(f"Tool search_courses gặp sự cố khi xử lý yêu cầu: {exc}")


def get_course_detail(course_id: str = "") -> str:
    """
    Lấy chi tiết khóa học: nội dung, học phí, thời lượng, giảng viên, điều kiện đầu vào, chứng chỉ và lịch học.

    Name:
        get_course_detail

    Purpose:
        Cung cấp thông tin đầy đủ của một khóa học cụ thể để Agent có căn cứ
        tư vấn thay vì tự suy đoán.

    When to use:
        Dùng sau search_courses khi người dùng muốn biết sâu hơn về một khóa,
        hoặc khi cần kiểm tra học phí, thời lượng, giảng viên, chứng chỉ,
        lịch học và prerequisite trước khi tư vấn/đăng ký.

    Input schema:
        course_id (str): Mã khóa học không rỗng, ví dụ "C101".

    Output schema:
        str: Chuỗi JSON có status="success", course_id, title, description,
        fee_vnd, duration, instructor, prerequisites, certificate, schedule,
        capacity_status.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu course_id thiếu, sai kiểu dữ liệu,
        hoặc không tồn tại trong danh mục khóa học mẫu.

    Side effects:
        Không thay đổi dữ liệu, chỉ đọc danh mục khóa học mẫu.

    Example:
        get_course_detail("C101")

    Safety:
        Hàm được bọc try/except và luôn trả về str; lỗi runtime không làm crash app.

    Args:
        course_id (str): Mã khóa học, ví dụ "C101".

    Returns:
        str: JSON chi tiết khóa học hoặc chuỗi "LỖI: ..." nếu mã không hợp lệ.
    """
    try:
        course_id_clean, course, error = _get_course(course_id)
        if error:
            return error

        return _to_json(_course_detail_payload(course_id_clean, course))
    except Exception as exc:
        return _error(f"Tool get_course_detail gặp sự cố khi xử lý yêu cầu: {exc}")


def get_student_profile(student_id: str = "") -> str:
    """
    Lấy hồ sơ sinh viên để tư vấn cá nhân hóa.

    Name:
        get_student_profile

    Purpose:
        Lấy ngành học, năm học, các môn đã hoàn thành, điểm mạnh, mục tiêu nghề
        nghiệp và lịch học hiện tại của sinh viên.

    When to use:
        Dùng khi cần cá nhân hóa gợi ý khóa học hoặc trước khi kiểm tra
        prerequisite, trùng lịch, đăng ký khóa học.

    Input schema:
        student_id (str): Mã sinh viên không rỗng, ví dụ "S001".

    Output schema:
        str: Chuỗi JSON có status="success", student_id, name, major, year,
        completed_courses, strengths, career_goal, current_schedule.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu student_id thiếu, sai kiểu dữ liệu,
        hoặc không tồn tại trong dữ liệu sinh viên mẫu.

    Side effects:
        Không thay đổi hồ sơ sinh viên, chỉ đọc dữ liệu mẫu.

    Example:
        get_student_profile("S001")

    Safety:
        Hàm được bọc try/except và luôn trả về str để Agent không bị crash khi
        thiếu hồ sơ.

    Args:
        student_id (str): Mã sinh viên, ví dụ "S001".

    Returns:
        str: JSON hồ sơ sinh viên hoặc chuỗi "LỖI: ..." nếu không tìm thấy hồ sơ.
    """
    try:
        student_id_clean, student, error = _get_student(student_id)
        if error:
            return error

        return _to_json(_student_profile_payload(student_id_clean, student))
    except Exception as exc:
        return _error(f"Tool get_student_profile gặp sự cố khi xử lý yêu cầu: {exc}")


def check_prerequisite(student_id: str = "", course_id: str = "") -> str:
    """
    Kiểm tra sinh viên có đủ điều kiện đầu vào của khóa học hay chưa.

    Name:
        check_prerequisite

    Purpose:
        Đối chiếu các môn/kỹ năng sinh viên đã hoàn thành với điều kiện đầu vào
        của khóa học để xác định sinh viên có thể học khóa đó hay không.

    When to use:
        Dùng khi người dùng hỏi "Em chưa học Python thì có đăng ký Machine
        Learning được không?", hoặc trước khi gọi register_course cho khóa có
        prerequisites.

    Input schema:
        student_id (str): Mã sinh viên không rỗng, ví dụ "S001".
        course_id (str): Mã khóa học không rỗng, ví dụ "C201".

    Output schema:
        str: Chuỗi JSON có status="success", student_id, course_id, eligible,
        missing_prerequisites và message.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu thiếu/sai kiểu student_id hoặc
        course_id, không tìm thấy sinh viên, hoặc không tìm thấy khóa học.

    Side effects:
        Không thay đổi dữ liệu, chỉ kiểm tra hồ sơ mẫu và danh mục khóa học.

    Example:
        check_prerequisite("S001", "C201")

    Safety:
        Hàm được bọc try/except và luôn trả về str; lỗi nghiệp vụ được xem là
        Observation để Agent tư vấn fallback.

    Args:
        student_id (str): Mã sinh viên.
        course_id (str): Mã khóa học.

    Returns:
        str: JSON kết quả kiểm tra hoặc chuỗi "LỖI: ..." nếu thiếu/sai dữ liệu.
    """
    try:
        student_id_clean, student, student_error = _get_student(student_id)
        if student_error:
            return student_error
        course_id_clean, course, course_error = _get_course(course_id)
        if course_error:
            return course_error

        missing = _missing_prerequisites(student, course)
        return _to_json({
            "status": "success",
            "student_id": student_id_clean,
            "course_id": course_id_clean,
            "eligible": not missing,
            "course_title": course.get("title", "Chưa cập nhật"),
            "student_completed_courses": student.get("completed_courses", []),
            "required_prerequisites": course.get("prerequisites", []),
            "missing_prerequisites": missing,
            "suggested_preparation": (
                []
                if not missing
                else [
                    "Học khóa nền tảng phù hợp trước khi đăng ký.",
                    "Trao đổi với cố vấn nếu đã có kinh nghiệm tương đương ngoài lớp học.",
                ]
            ),
            "message": (
                "Sinh viên đủ điều kiện đầu vào."
                if not missing
                else "Sinh viên chưa đủ điều kiện đầu vào, nên học bổ sung các mục còn thiếu trước."
            ),
        })
    except Exception as exc:
        return _error(f"Tool check_prerequisite gặp sự cố khi xử lý yêu cầu: {exc}")


def check_schedule_conflict(student_id: str = "", course_id: str = "") -> str:
    """
    Kiểm tra khóa học có trùng lịch học hiện tại của sinh viên không.

    Name:
        check_schedule_conflict

    Purpose:
        So sánh lịch khóa học với lịch học hiện tại của sinh viên để tránh tư vấn
        hoặc đăng ký khóa bị trùng giờ.

    When to use:
        Dùng khi người dùng hỏi "Khóa này có trùng lịch của em không?", hoặc
        trước khi gọi register_course.

    Input schema:
        student_id (str): Mã sinh viên không rỗng, ví dụ "S001".
        course_id (str): Mã khóa học không rỗng, ví dụ "C101".

    Output schema:
        str: Chuỗi JSON có status="success", student_id, course_id, has_conflict,
        conflicts và message.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu thiếu/sai kiểu student_id hoặc
        course_id, không tìm thấy sinh viên, hoặc không tìm thấy khóa học.

    Side effects:
        Không thay đổi lịch học, chỉ đọc dữ liệu mẫu.

    Example:
        check_schedule_conflict("S001", "C101")

    Safety:
        Hàm được bọc try/except và luôn trả về str; mọi lỗi đều chuyển thành
        thông báo an toàn cho Agent.

    Args:
        student_id (str): Mã sinh viên.
        course_id (str): Mã khóa học.

    Returns:
        str: JSON kết quả kiểm tra lịch hoặc chuỗi "LỖI: ..." nếu thiếu/sai dữ liệu.
    """
    try:
        student_id_clean, student, student_error = _get_student(student_id)
        if student_error:
            return student_error
        course_id_clean, course, course_error = _get_course(course_id)
        if course_error:
            return course_error

        conflicts = _schedule_conflicts(student, course)
        return _to_json({
            "status": "success",
            "student_id": student_id_clean,
            "course_id": course_id_clean,
            "course_title": course.get("title", "Chưa cập nhật"),
            "course_schedule": course.get("schedule", "Chưa cập nhật"),
            "student_current_schedule": [
                f"{day} {start}-{end}"
                for day, start, end in student.get("current_schedule", [])
            ],
            "has_conflict": bool(conflicts),
            "conflicts": conflicts,
            "suggested_action": (
                "Chọn khóa khác hoặc chuyển cho cố vấn học tập nếu sinh viên vẫn muốn học khóa này."
                if conflicts
                else "Có thể tiếp tục kiểm tra điều kiện đầu vào hoặc bước xác nhận đăng ký."
            ),
            "message": "Khóa học bị trùng lịch." if conflicts else "Không phát hiện trùng lịch.",
        })
    except Exception as exc:
        return _error(f"Tool check_schedule_conflict gặp sự cố khi xử lý yêu cầu: {exc}")


def register_course(student_id: str = "", course_id: str = "") -> str:
    """
    Mô phỏng đăng ký khóa học sau khi sinh viên xác nhận rõ ràng.

    Name:
        register_course

    Purpose:
        Ghi nhận đăng ký khóa học trong môi trường mô phỏng của lab sau khi
        sinh viên đã xác nhận rõ ràng.

    When to use:
        Chỉ dùng khi người dùng xác nhận dứt khoát như "Xác nhận đăng ký khóa
        C102 cho em". Không dùng khi người dùng chỉ hỏi khóa có phù hợp không,
        hỏi học phí, hỏi lịch, hoặc còn đang phân vân.

    Input schema:
        student_id (str): Mã sinh viên không rỗng.
        course_id (str): Mã khóa học không rỗng.

    Output schema:
        str: Chuỗi JSON có status="registered_mock", message, student_id,
        student_name, course_id, course_title, fee_vnd và schedule.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu thiếu/sai tham số, không tìm thấy
        sinh viên/khóa học, khóa hết chỗ, sinh viên thiếu prerequisite, hoặc
        khóa bị trùng lịch.

    Side effects:
        Chỉ mô phỏng đăng ký trong lab, không ghi database thật, không thu phí,
        không gửi email.

    Example:
        register_course("S002", "C102")

    Safety:
        Hàm được bọc try/except. Các lỗi nghiệp vụ như thiếu điều kiện hoặc
        trùng lịch được trả về thành chuỗi "LỖI:" để Agent giải thích cho sinh viên.

    Args:
        student_id (str): Mã sinh viên.
        course_id (str): Mã khóa học.

    Returns:
        str: JSON xác nhận đăng ký giả lập hoặc chuỗi "LỖI: ..." nếu chưa thể đăng ký.
    """
    try:
        student_id_clean, student, student_error = _get_student(student_id)
        if student_error:
            return student_error
        course_id_clean, course, course_error = _get_course(course_id)
        if course_error:
            return course_error

        if "hết" in _normalize(course.get("capacity_status", "")):
            return _error(f"Khóa học '{course_id_clean}' hiện đã hết chỗ.")

        missing = _missing_prerequisites(student, course)
        if missing:
            return _error("Chưa thể đăng ký vì sinh viên còn thiếu điều kiện đầu vào: " + ", ".join(missing) + ".")

        conflicts = _schedule_conflicts(student, course)
        if conflicts:
            return _error("Chưa thể đăng ký vì khóa học bị trùng lịch học hiện tại của sinh viên.")

        return _to_json({
            "status": "registered_mock",
            "registration_id": f"REG-{student_id_clean}-{course_id_clean}",
            "message": "Đăng ký khóa học thành công trong môi trường mô phỏng.",
            "student_id": student_id_clean,
            "student_name": student.get("name", "Chưa cập nhật"),
            "course_id": course_id_clean,
            "course_title": course.get("title", "Chưa cập nhật"),
            "fee_vnd": course.get("fee", "Chưa cập nhật"),
            "fee_category": _fee_category(course.get("fee", 0)),
            "schedule": course.get("schedule", "Chưa cập nhật"),
            "mode": course.get("mode", "offline"),
            "next_start": course.get("next_start", "Chưa cập nhật"),
            "certificate": course.get("certificate", "Chưa cập nhật"),
            "payment_note": "Học phí được ghi nhận ở trạng thái chờ thanh toán trong môi trường mô phỏng.",
            "recommended_next_action": "Có thể gọi create_learning_reminder nếu sinh viên muốn được nhắc học.",
        })
    except Exception as exc:
        return _error(f"Tool register_course gặp sự cố khi xử lý yêu cầu: {exc}")


def create_learning_reminder(student_id: str = "", course_id: str = "", reminder_time: str = "") -> str:
    """
    Mô phỏng tạo lịch nhắc học cho sinh viên.

    Name:
        create_learning_reminder

    Purpose:
        Tạo nhắc học giả lập theo thời gian sinh viên yêu cầu để hỗ trợ theo dõi
        lịch học sau khi đã chọn/đăng ký khóa.

    When to use:
        Dùng khi người dùng yêu cầu như "Nhắc em trước buổi học 30 phút" hoặc
        "Tạo reminder cho khóa C102".

    Input schema:
        student_id (str): Mã sinh viên không rỗng.
        course_id (str): Mã khóa học không rỗng.
        reminder_time (str): Thời điểm nhắc, ví dụ "trước buổi học 30 phút".

    Output schema:
        str: Chuỗi JSON có status="reminder_created_mock", message, student_id,
        student_name, course_id, course_title, course_schedule và reminder_time.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu thiếu/sai kiểu tham số, không tìm
        thấy sinh viên, không tìm thấy khóa học, hoặc reminder_time rỗng.

    Side effects:
        Chỉ mô phỏng tạo nhắc học, không ghi calendar thật, không gửi notification thật.

    Example:
        create_learning_reminder("S002", "C102", "trước buổi học 30 phút")

    Safety:
        Hàm được bọc try/except và luôn trả về str; không crash khi người dùng
        nhập thiếu thời gian nhắc.

    Args:
        student_id (str): Mã sinh viên.
        course_id (str): Mã khóa học.
        reminder_time (str): Thời gian nhắc, ví dụ "trước buổi học 30 phút".

    Returns:
        str: JSON xác nhận tạo nhắc học giả lập hoặc chuỗi "LỖI: ..." nếu thiếu/sai dữ liệu.
    """
    try:
        student_id_clean, student, student_error = _get_student(student_id)
        if student_error:
            return student_error
        course_id_clean, course, course_error = _get_course(course_id)
        if course_error:
            return course_error
        if not isinstance(reminder_time, str):
            return _error("Thiếu tham số hoặc sai dữ liệu cho 'reminder_time'.")
        reminder_time_clean = reminder_time.strip()
        if not reminder_time_clean:
            return _error("Thiếu tham số reminder_time.")

        return _to_json({
            "status": "reminder_created_mock",
            "reminder_id": f"REM-{student_id_clean}-{course_id_clean}",
            "message": "Đã tạo nhắc học trong môi trường mô phỏng.",
            "student_id": student_id_clean,
            "student_name": student.get("name", "Chưa cập nhật"),
            "course_id": course_id_clean,
            "course_title": course.get("title", "Chưa cập nhật"),
            "course_schedule": course.get("schedule", "Chưa cập nhật"),
            "reminder_time": reminder_time_clean,
            "channels": ["in_app", "email_mock"],
            "timezone": "Asia/Saigon",
        })
    except Exception as exc:
        return _error(f"Tool create_learning_reminder gặp sự cố khi xử lý yêu cầu: {exc}")


def handoff_to_advisor(student_id: str = "", reason: str = "", conversation_summary: str = "") -> str:
    """
    Mô phỏng chuyển trường hợp cần xử lý đặc biệt cho tư vấn viên/cố vấn học tập.

    Name:
        handoff_to_advisor

    Purpose:
        Tạo ticket chuyển tiếp giả lập cho tư vấn viên/cố vấn học tập khi Agent
        không nên tự quyết định.

    When to use:
        Dùng khi không tìm thấy thông tin, sinh viên có trường hợp đặc biệt,
        liên quan hoàn tiền/khiếu nại, cần cố vấn học tập quyết định, hoặc tool
        báo lỗi nhiều lần.

    Input schema:
        student_id (str): Mã sinh viên hoặc mã người dùng đang trao đổi.
        reason (str): Lý do chuyển tiếp không rỗng.
        conversation_summary (str): Tóm tắt ngắn bối cảnh hội thoại.

    Output schema:
        str: Chuỗi JSON có status="handoff_created_mock", ticket_id, student_id,
        student_name, reason, conversation_summary và next_step.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu bất kỳ tham số nào sai kiểu hoặc rỗng.

    Side effects:
        Chỉ mô phỏng tạo ticket, không gửi yêu cầu thật tới hệ thống hỗ trợ.

    Example:
        handoff_to_advisor("S001", "Trường hợp đặc biệt", "Sinh viên muốn học vượt.")

    Safety:
        Hàm được bọc try/except và luôn trả về str; có thể dùng làm fallback an toàn
        khi Agent không đủ bằng chứng để tư vấn tiếp.

    Args:
        student_id (str): Mã sinh viên.
        reason (str): Lý do chuyển tư vấn viên.
        conversation_summary (str): Tóm tắt hội thoại.

    Returns:
        str: JSON ticket chuyển tiếp giả lập hoặc chuỗi "LỖI: ..." nếu thiếu/sai tham số.
    """
    try:
        for name, value in {
            "student_id": student_id,
            "reason": reason,
            "conversation_summary": conversation_summary,
        }.items():
            if not isinstance(value, str):
                return _error(f"Thiếu tham số hoặc sai kiểu dữ liệu cho '{name}'.")
            if not value.strip():
                return _error(f"Thiếu tham số '{name}'.")

        student_id_clean = student_id.strip().upper()
        student_name = STUDENTS.get(student_id_clean, {}).get("name", "Sinh viên chưa xác thực hồ sơ")

        return _to_json({
            "status": "handoff_created_mock",
            "ticket_id": f"ADV-{student_id_clean}-001",
            "student_id": student_id_clean,
            "student_name": student_name,
            "student_profile_found": student_id_clean in STUDENTS,
            "priority": "high" if any(word in _normalize(reason) for word in ["khiếu nại", "hoàn tiền", "khẩn", "complaint", "refund"]) else "normal",
            "reason": reason.strip(),
            "conversation_summary": conversation_summary.strip(),
            "next_step": "Tư vấn viên sẽ xem xét và phản hồi trong vòng 1 ngày làm việc.",
            "recommended_channel": "academic_advisor_queue",
        })
    except Exception as exc:
        return _error(f"Tool handoff_to_advisor gặp sự cố khi xử lý yêu cầu: {exc}")


def compare_courses(course_ids: str | list[str] = "") -> str:
    """
    So sánh nhiều khóa học cạnh nhau.

    Name:
        compare_courses

    Purpose:
        So sánh nhanh nhiều khóa học theo học phí, thời lượng, lịch học,
        prerequisite, chứng chỉ và mục tiêu nghề nghiệp phù hợp.

    When to use:
        Dùng khi sinh viên hỏi "Nên chọn khóa C101 hay C201?", "Khóa nào rẻ hơn?",
        "So sánh Python và Machine Learning", hoặc khi Agent cần tóm tắt lựa chọn.

    Input schema:
        course_ids (str | list[str]): Ít nhất 2 mã khóa học. Có thể là chuỗi
        phân tách bởi dấu phẩy/khoảng trắng như "C101,C201" hoặc list ["C101", "C201"].

    Output schema:
        str: Chuỗi JSON có status="success", courses và quick_note. Mỗi course
        gồm course_id, title, level, fee_vnd, duration, schedule, prerequisites,
        certificate, career_goals.

    Error semantics:
        Trả về chuỗi bắt đầu bằng "LỖI:" nếu course_ids thiếu, sai kiểu, có ít
        hơn 2 mã, hoặc có mã khóa học không tồn tại.

    Side effects:
        Không thay đổi dữ liệu, chỉ đọc danh mục khóa học mẫu.

    Example:
        compare_courses("C101,C201")

    Safety:
        Hàm được bọc try/except và luôn trả về str; lỗi parse danh sách mã được
        chuyển thành thông báo "LỖI:".

    Args:
        course_ids (str | list[str]): Ít nhất 2 mã khóa học, ví dụ "C101,C201".

    Returns:
        str: JSON bảng so sánh hoặc chuỗi "LỖI: ..." nếu thiếu/sai mã khóa học.
    """
    try:
        if isinstance(course_ids, str):
            ids = [item.strip().upper() for item in re.split(r"[,;\s]+", course_ids) if item.strip()]
        elif isinstance(course_ids, (list, tuple, set)):
            ids = [str(item).strip().upper() for item in course_ids if str(item).strip()]
        else:
            return _error("Thiếu mã khóa học hoặc danh sách mã khóa học không hợp lệ.")

        if len(ids) < 2:
            return _error("Cần ít nhất 2 mã khóa học để so sánh.")

        unknown_ids = [course_id for course_id in ids if course_id not in COURSES]
        if unknown_ids:
            return _error(f"Không tìm thấy các khóa học: {', '.join(unknown_ids)}.")

        comparisons = []
        for course_id in ids:
            course = COURSES[course_id]
            comparisons.append(_course_detail_payload(course_id, course))

        cheapest = min(ids, key=lambda item: int(COURSES[item].get("fee", 0)))
        return _to_json({
            "status": "success",
            "courses": comparisons,
            "quick_note": f"Khóa có học phí thấp nhất là {cheapest} - {COURSES[cheapest].get('title', 'Chưa cập nhật')}.",
            "comparison_axes": [
                "học phí",
                "trình độ",
                "lịch học",
                "workload",
                "project cuối khóa",
                "prerequisite",
                "chứng chỉ",
                "học bổng",
            ],
        })
    except Exception as exc:
        return _error(f"Tool compare_courses gặp sự cố khi xử lý yêu cầu: {exc}")


AVAILABLE_TOOLS = {
    "search_courses": search_courses,
    "get_course_detail": get_course_detail,
    "check_prerequisite": check_prerequisite,
    "check_schedule_conflict": check_schedule_conflict,
    "get_student_profile": get_student_profile,
    "register_course": register_course,
    "create_learning_reminder": create_learning_reminder,
    "handoff_to_advisor": handoff_to_advisor,
    "compare_courses": compare_courses,
}
