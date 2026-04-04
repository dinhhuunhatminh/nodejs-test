import os
import argparse
from pymongo import MongoClient

def update_knowledge(category, tool_id, actual_time, actual_score, alpha=0.5):
    client = MongoClient(os.environ['MONGO_URI'])
    collection = client['devsecops']['tools']
    
    # Kéo dữ liệu hiện tại từ Cloud về
    data = collection.find_one()
    
    # Cập nhật thông số bằng thuật toán EMA
    for tool in data[category]:
        if tool['id'] == tool_id:
            old_time = tool.get('base_time', actual_time)
            old_score = tool.get('v_score', actual_score)
            tool['base_time'] = (alpha * actual_time) + ((1 - alpha) * old_time)
            tool['v_score'] = int((alpha * actual_score) + ((1 - alpha) * old_score))
            print(f"🔄 Đã ghi đè kết quả tự học của {tool_id} lên Cloud!")
            break

    # Đẩy toàn bộ dữ liệu mới lên lại MongoDB
    collection.replace_one({'_id': data['_id']}, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cat", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--time", type=float, required=True)
    parser.add_argument("--score", type=int, required=True)
    args = parser.parse_args()

    # Bỏ đi việc truyền đường dẫn file, gọi thẳng hàm
    update_knowledge(args.cat, args.id, args.time, args.score)