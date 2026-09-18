import json
import os
import google.generativeai as genai

SYSTEM_PROMPT = """
Bạn là trợ lý AI trên web "Thật Hay Giả?", hỗ trợ học sinh kiểm chứng tin tức.
NHIỆM VỤ QUAN TRỌNG NHẤT: BẠN PHẢI CHẤM ĐIỂM THEO ĐÚNG THANG ĐO SAU ĐÂY:
Đánh giá thông tin qua 5 tiêu chí, mỗi tiêu chí cho điểm từ 0 đến 2:
1. Nguồn đăng (0: Không rõ, 1: Có nhưng chưa chính thống, 2: Chính thống rõ ràng)
2. Người đăng (0: Ẩn danh, 1: Có thể xác minh nhưng chưa uy tín, 2: Cơ quan/cá nhân uy tín)
3. Dẫn chứng (0: Không có, 1: Khó kiểm chứng, 2: Rõ ràng, kiểm chứng được)
4. Xác nhận báo chí (0: Bị bác bỏ, 1: Chưa có báo xác nhận, 2: Báo chính thống xác nhận)
5. Cách trình bày (0: Giật gân/câu view, 1: Bình thường nhưng chủ quan, 2: Khách quan)

CÁCH TÍNH % TIN CẬY (reliability_score):
- Cộng tổng điểm 5 tiêu chí trên (Tối đa 10 điểm).
- Lấy (Tổng điểm / 10) * 100 để ra số %. (Ví dụ tổng 7 điểm -> 70%).

Luôn trả về định dạng JSON chính xác gồm: 
{
    "reliability_score": <số nguyên từ 0-100 dựa trên công thức trên>,
    "analysis": "<nhận xét ngắn gọn>",
    "criteria_breakdown": [
        {"name": "Nguồn đăng", "score": <0, 1 hoặc 2>, "comment": "<giải thích>"},
        {"name": "Người đăng", "score": <0, 1 hoặc 2>, "comment": "<giải thích>"},
        {"name": "Dẫn chứng", "score": <0, 1 hoặc 2>, "comment": "<giải thích>"},
        {"name": "Xác nhận báo chí", "score": <0, 1 hoặc 2>, "comment": "<giải thích>"},
        {"name": "Cách trình bày", "score": <0, 1 hoặc 2>, "comment": "<giải thích>"}
    ],
    "stop_advice": {"S": "...", "T": "...", "O": "...", "P": "..."},
    "google_search": {"queries": ["từ khóa 1", "từ khóa 2"], "tip": "..."},
    "ai_analyzed_links": [{"title":"...","url":"...","reliability":"Cao/Thấp","comment":"..."}]
}
"""

def show_error_on_web(error_message):
    return {
        "reliability_score": 0,
        "analysis": f"🚨 LỖI HỆ THỐNG: {error_message}",
        "criteria_breakdown": [{"name": "Lỗi", "score": 0, "comment": "Lỗi hệ thống"}] * 5,
        "stop_advice": {"S": "Lỗi", "T": "Lỗi", "O": "Lỗi", "P": "Lỗi"},
        "google_search": {"queries": ["Cách sửa lỗi mạng"], "tip": "Hãy thử lại sau."},
        "ai_analyzed_links": []
    }

def analyze_information(user_query):
    # Lấy API Key từ Vercel
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return show_error_on_web("CHƯA CẤU HÌNH GEMINI_API_KEY TRÊN VERCEL!")
    
    try:
        # Khởi tạo thư viện chính thức của Google
        genai.configure(api_key=api_key)
        
        # Gọi thẳng model gemini-1.5-flash (phiên bản ổn định và thông minh nhất hiện tại)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Gộp Prompt và Nội dung
        combined_text = f"{SYSTEM_PROMPT}\n\n--- THÔNG TIN NGƯỜI DÙNG CẦN KIỂM CHỨNG ---\n{user_query}"
        
        # Yêu cầu AI phân tích
        response = model.generate_content(combined_text)
        
        # Xử lý kết quả JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(clean_text)
        
        # Bổ sung dữ liệu mồi nếu AI bỏ sót
        if not result_json.get("google_search") or not result_json["google_search"].get("queries"):
            result_json["google_search"] = {
                "queries": [f"Sự thật về {user_query[:20]}...", f"Đính chính {user_query[:20]}..."],
                "tip": "MẸO: Khi tìm kiếm hãy thêm chữ 'Sự thật' hoặc 'Đính chính' vào trước!"
            }
            
        if not result_json.get("ai_analyzed_links"):
            result_json["ai_analyzed_links"] = [
                {"title": "Cổng thông tin Điện tử", "url": "https://chinhphu.vn", "reliability": "Cao", "comment": "Luôn tra cứu tại trang web chính thức."}
            ]
            
        return result_json
        
    except Exception as e:
        return show_error_on_web(str(e))
