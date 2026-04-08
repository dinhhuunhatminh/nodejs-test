import pymongo
import os

# Thay bằng Connection String của bạn nếu chạy local, 
# hoặc script sẽ tự lấy từ biến môi trường
MONGO_URI = "mongodb+srv://mikazuki241125111_db_user:15102005Huuminnh!@cluster0.ozb6qg2.mongodb.net/?appName=Cluster0" 

client = pymongo.MongoClient(MONGO_URI)
db = client['devsecops']
collection = db['tools']

# Bộ dữ liệu mở rộng
expanded_tools = {
    "SAST": [
        {"id": "sast_skip", "base_time": 0, "time_per_loc": 0, "v_score": 0},
        {"id": "njsscan_quick", "base_time": 10, "time_per_loc": 0.1, "v_score": 35},
        {"id": "semgrep_standard", "base_time": 25, "time_per_loc": 0.5, "v_score": 65},
        {"id": "sonar_deep", "base_time": 60, "time_per_loc": 2.0, "v_score": 85},
        {"id": "codeql_full", "base_time": 150, "time_per_loc": 3.5, "v_score": 98}
    ],
    "SCA": [
        {"id": "sca_skip", "base_time": 0, "time_per_loc": 0, "v_score": 0},
        {"id": "npm_audit", "base_time": 5, "time_per_loc": 0.05, "v_score": 25},
        {"id": "trivy_standard", "base_time": 15, "time_per_loc": 0.2, "v_score": 55},
        {"id": "trivy_deep", "base_time": 35, "time_per_loc": 0.8, "v_score": 80},
        {"id": "snyk_advanced", "base_time": 70, "time_per_loc": 1.5, "v_score": 95}
    ],
    "DAST": [
        {"id": "dast_skip", "base_time": 0, "time_per_loc": 0, "v_score": 0},
        {"id": "nuclei_fast", "base_time": 20, "time_per_loc": 0, "v_score": 45},
        {"id": "zap_quick", "base_time": 45, "time_per_loc": 0, "v_score": 60},
        {"id": "zap_full", "base_time": 180, "time_per_loc": 0, "v_score": 90},
        {"id": "zap_ajax_spider", "base_time": 300, "time_per_loc": 0, "v_score": 98}
    ]
}

# Thực hiện cập nhật
collection.delete_many({}) # Xóa dữ liệu cũ
collection.insert_one(expanded_tools)

print("✅ Đã cập nhật 15 cấu hình công cụ mới lên MongoDB thành công!")