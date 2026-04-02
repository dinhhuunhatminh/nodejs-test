import json
import argparse

def update_knowledge(filepath, category, tool_id, actual_time, actual_score, alpha=0.5):
    # Đọc dữ liệu cũ
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Cập nhật dữ liệu bằng công thức Tự học (Exponential Moving Average)
    for tool in data[category]:
        if tool['id'] == tool_id:
            old_time = tool['base_time']
            old_score = tool['v_score']
            
            tool['base_time'] = (alpha * actual_time) + ((1 - alpha) * old_time)
            tool['v_score'] = int((alpha * actual_score) + ((1 - alpha) * old_score))
            
            print(f"🔄 Đã học xong cho {tool_id}!")
            print(f"   Thời gian: {old_time}s -> {tool['base_time']}s")
            print(f"   Điểm lỗi: {old_score} -> {tool['v_score']}")
            break

    # Ghi đè lại file JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cat", required=True, help="Danh mục (SAST, SCA, DAST)")
    parser.add_argument("--id", required=True, help="ID công cụ (vd: sonar_quick)")
    parser.add_argument("--time", type=float, required=True, help="Thời gian chạy thực tế (giây)")
    parser.add_argument("--score", type=int, required=True, help="Số lỗi thực tế tìm được")
    args = parser.parse_args()

    update_knowledge("data/security_tools.json", args.cat, args.id, args.time, args.score)