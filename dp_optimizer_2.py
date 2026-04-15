import pymongo
import os
import sys

def solve_knapsack(tools_list, time_limit, loc):
    # 1. Tính toán thời gian thực tế (Weight) và làm tròn thành số nguyên
    for tool in tools_list:
        tool['actual_time'] = int(tool['base_time'] + (tool['time_per_loc'] * loc))

    n = len(tools_list)
    capacity = int(time_limit)
    
    # Bảng DP lưu điểm số tối đa
    dp = [[0 for x in range(capacity + 1)] for x in range(n + 1)]
    
    # 2. Xây dựng bảng quy hoạch động
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            tool = tools_list[i-1]
            if tool['actual_time'] <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - tool['actual_time']] + tool['v_score'])
            else:
                dp[i][w] = dp[i-1][w]

    # 3. Truy vết để lấy danh sách công cụ được chọn
    res = dp[n][capacity]
    w = capacity
    selected_tools = []
    
    for i in range(n, 0, -1):
        if res <= 0:
            break
        if res == dp[i - 1][w]:
            continue
        else:
            tool = tools_list[i - 1]
            selected_tools.append(tool)
            res = res - tool['v_score']
            w = w - tool['actual_time']
            
    return selected_tools, dp[n][capacity], sum(t['actual_time'] for t in selected_tools)

def main():
    # Lấy tham số từ môi trường
    try:
        TIME_BUDGET = int(os.environ.get('TIME_BUDGET', 300))
        LOC_CHANGED = int(os.environ.get('LOC_CHANGED', 100))
        # Đọc danh sách các lớp bảo mật người dùng muốn chạy
        selected_layers_str = os.environ.get('SELECTED_LAYERS', 'SAST,SCA,DAST') 
    except:
        TIME_BUDGET, LOC_CHANGED = 300, 100
        selected_layers_str = 'SAST,SCA,DAST'

    # Xử lý chuỗi đầu vào thành mảng (VD: "SAST, SCA" -> ['SAST', 'SCA'])
    target_layers = [layer.strip().upper() for layer in selected_layers_str.split(',') if layer.strip()]
    if not target_layers:
        target_layers = ['SAST', 'SCA', 'DAST']

    # Kết nối MongoDB 
    client = pymongo.MongoClient(os.environ.get('MONGO_URI'), tlsAllowInvalidCertificates=True)
    db = client['devsecops']
    data = db['tools'].find_one()

    results = {}
    summary_table = []

    # Phân bổ lại ngân sách động (Chỉ chia ngân sách cho những lớp được chọn)
    layer_budget = TIME_BUDGET / len(target_layers)

    # Chạy thuật toán kiểm tra cho từng tầng
    for category in ['SAST', 'SCA', 'DAST']:
        if category in target_layers:
            selected, t, s = solve_knapsack(data[category], layer_budget, LOC_CHANGED)
            if not selected:
                results[category] = f"{category.lower()}_skip"
                summary_table.append([category, "SKIP (LOW BUDGET)", 0, 0])
            else:
                best_tool = max(selected, key=lambda x: x['v_score'])
                results[category] = best_tool['id']
                summary_table.append([category, best_tool['id'], round(best_tool['actual_time'], 2), best_tool['v_score']])
        else:
            results[category] = f"{category.lower()}_skip"
            summary_table.append([category, "SKIPPED BY USER", 0, 0])

    # IN BÁO CÁO TRÌNH BÀY
    print("="*60)
    print(f"SMART PIPELINE DECISION REPORT (DYNAMIC MODE)")
    print("="*60)
    print(f"Input: LOC = {LOC_CHANGED} | Budget = {TIME_BUDGET}s | Target = {', '.join(target_layers)}")
    print("-" * 60)
    print(f"{'LAYER':<10} | {'SELECTED TOOL':<20} | {'EST. TIME':<10} | {'SCORE'}")
    print("-" * 60)
    total_est_time = 0
    total_est_score = 0
    for row in summary_table:
        print(f"{row[0]:<10} | {row[1]:<20} | {row[2]:<10} | {row[3]}")
        total_est_time += row[2]
        total_est_score += row[3]
    print("-" * 60)
    print(f"TOTAL: Time = {round(total_est_time, 2)}s / {TIME_BUDGET}s | Score = {total_est_score}")
    print("=" * 60)

    # Xuất kết quả ra GitHub Output
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"sast_choice={results['SAST']}\n")
            f.write(f"sca_choice={results['SCA']}\n")
            f.write(f"dast_choice={results['DAST']}\n")

if __name__ == "__main__":
    main()