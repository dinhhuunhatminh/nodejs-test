import os
import json
import argparse
import itertools
import certifi # <--- Thêm dòng này
from pymongo import MongoClient

def load_data():
    # zpip install pymongo dnspython 
    # print("Đang kết nối tới MongoDB...")
    # Lấy chìa khóa kết nối từ biến môi trường
    client = MongoClient(os.environ['MONGO_URI'], tlsCAFile=certifi.where())
    collection = client['devsecops']['tools']
    
    # Lấy document đầu tiên, bỏ qua cột _id tự sinh của MongoDB
    return collection.find_one({}, {'_id': 0})

def calculate_time(tool, loc):
    return tool['base_time'] + (tool['time_per_loc'] * loc)

def optimize_pipeline(data, loc, time_budget_sec):
    categories = list(data.keys())
    options_per_category = [data[cat] for cat in categories]
    
    best_combo = None
    max_v_score = -1
    best_time = 0

    for combo in itertools.product(*options_per_category):
        total_time = sum(calculate_time(tool, loc) for tool in combo)
        total_v_score = sum(tool['v_score'] for tool in combo)

        if total_time <= time_budget_sec and total_v_score > max_v_score:
            max_v_score = total_v_score
            best_combo = combo
            best_time = total_time

    if best_combo:
        result = {categories[i]: tool['id'] for i, tool in enumerate(best_combo)}
        return result, best_time, max_v_score
    else:
        return {"SAST": "sast_skip", "SCA": "sca_skip", "DAST": "dast_skip"}, 0, 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart CI/CD Optimizer")
    parser.add_argument("--loc", type=int, required=True, help="Số dòng code mới (Lines of Code)")
    parser.add_argument("--time_min", type=int, required=True, help="Ngân sách thời gian (Phút)")
    args = parser.parse_args()

    time_budget_sec = args.time_min * 60
    data = load_data()
    decision, estimated_time, total_score = optimize_pipeline(data, args.loc, time_budget_sec)

    print(json.dumps(decision))