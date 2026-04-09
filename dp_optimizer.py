import pymongo
import os
import sys

def solve_knapsack(tools_list, time_limit, loc):
    # Tính toán thời gian thực tế dựa trên LOC cho từng công cụ
    for tool in tools_list:
        tool['actual_time'] = tool['base_time'] + (tool['time_per_loc'] * loc)
    
    n = len(tools_list)
    # Thuật toán Knapsack Dynamic Programming (hoặc Greedy nếu muốn nhanh)
    # Ở đây dùng Greedy để ưu tiên tỉ lệ v_score/time (phù hợp với bài toán chọn bộ công cụ)
    sorted_tools = sorted(tools_list, key=lambda x: x['v_score']/(x['actual_time'] if x['actual_time'] > 0 else 0.1), reverse=True)
    
    selected = []
    total_time = 0
    total_score = 0
    
    for tool in sorted_tools:
        if total_time + tool['actual_time'] <= time_limit:
            selected.append(tool)
            total_time += tool['actual_time']
            total_score += tool['v_score']
            
    return selected, total_time, total_score

def main():
    # Lấy tham số từ môi trường (GitHub Actions truyền vào) hoặc dùng mặc định để test
    try:
        TIME_BUDGET = int(os.environ.get('TIME_BUDGET', 300)) # Mặc định 5 phút
        LOC_CHANGED = int(os.environ.get('LOC_CHANGED', 100)) # Mặc định 100 dòng
    except:
        TIME_BUDGET, LOC_CHANGED = 300, 100

    # THÊM DÒNG NÀY ĐỂ ÉP SỐ LIỆU TEST:
    LOC_CHANGED = 5000  # Giả lập commit cực lớn để xem AI tính toán

    # Kết nối MongoDB (Nhớ thêm tham số SSL nếu chạy local bị lỗi)
    client = pymongo.MongoClient(os.environ.get('MONGO_URI'), tlsAllowInvalidCertificates=True)
    db = client['devsecops']
    data = db['tools'].find_one()

    results = {}
    summary_table = []

    # Chạy thuật toán cho từng tầng
    # Chia budget: Mỗi tầng 1/3 (Hoặc bạn có thể tối ưu chia tổng cho cả 3)
    layer_budget = TIME_BUDGET / 3

    for category in ['SAST', 'SCA', 'DAST']:
        selected, t, s = solve_knapsack(data[category], layer_budget, LOC_CHANGED)
        # Nếu không chọn được gì (do budget quá thấp), mặc định chọn skip
        if not selected:
            results[category] = f"{category.lower()}_skip"
            summary_table.append([category, "SKIP", 0, 0])
        else:
            # Chọn công cụ có v_score cao nhất trong danh sách thỏa mãn budget
            best_tool = max(selected, key=lambda x: x['v_score'])
            results[category] = best_tool['id']
            summary_table.append([category, best_tool['id'], round(best_tool['actual_time'], 2), best_tool['v_score']])

    # --- IN BÁO CÁO TRÌNH BÀY ---
    print("="*60)
    print(f"🚀 SMART PIPELINE DECISION REPORT")
    print("="*60)
    print(f"Input: LOC ={LOC_CHANGED} lines | Budget = {TIME_BUDGET}s")
    print("-"*60)
    print(f"{'LAYER':<10} | {'SELECTED TOOL':<20} | {'EST. TIME':<10} | {'SCORE'}")
    print("-"*60)
    total_est_time = 0
    total_est_score = 0
    for row in summary_table:
        print(f"{row[0]:<10} | {row[1]:<20} | {row[2]:<10} | {row[3]}")
        total_est_time += row[2]
        total_est_score += row[3]
    print("-"*60)
    print(f"TOTAL: Time = {round(total_est_time, 2)}s / {TIME_BUDGET}s | Score = {total_est_score}")
    print("="*60)

    # Xuất kết quả ra GitHub Output (Chuẩn mới)
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"sast_choice={results['SAST']}\n")
            f.write(f"sca_choice={results['SCA']}\n")
            f.write(f"dast_choice={results['DAST']}\n")
    else:
        # Fallback in ra màn hình nếu test trên máy tính cá nhân
        print(f"sast_choice={results['SAST']}")
        print(f"sca_choice={results['SCA']}")
        print(f"dast_choice={results['DAST']}")

if __name__ == "__main__":
    main()