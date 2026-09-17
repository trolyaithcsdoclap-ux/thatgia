from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import os

# Import hàm xử lý AI từ thư mục utils
from utils.ai_helper import analyze_information

# Load các biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)

CORS(app)

@app.route('/')
def home():
    # Render file index.html nằm trong thư mục templates/
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify_information():
    # Lấy dữ liệu JSON từ Frontend gửi lên
    data = request.get_json()
    
    if not data:
         return jsonify({"error": "Định dạng dữ liệu không hợp lệ"}), 400
         
    user_query = data.get('query', '')

    # Validate dữ liệu đầu vào
    if not user_query.strip():
        return jsonify({"error": "Vui lòng nhập thông tin cần kiểm chứng"}), 400

    try:
        # Gọi module AI helper để phân tích
        result = analyze_information(user_query)
        # Trả kết quả về cho Frontend dưới dạng JSON
        return jsonify(result)
        
    except Exception as e:
        # Xử lý lỗi hệ thống
        return jsonify({"error": "Đã xảy ra lỗi trên máy chủ: " + str(e)}), 500

if __name__ == '__main__':
    # Chạy server ở chế độ debug, cổng mặc định 5000
    app.run(debug=True, port=5000)