import pymongo
import os
import sys

def evaluate_combination(sast_tool, sca_tool, dast_tool, loc, time_limit, ram_limit):
    """
    Hàm tính toán Mục tiêu (Objective Function) và Ràng buộc (Constraints)
    """
    combo = [sast_tool, sca_tool, dast_tool]
    total_time = 0
    total_score = 0
    
    for tool in combo:
        if tool['id'] == 'skip': 
            continue
        
        # Ước lượng chi phí thời gian dựa trên LOC (Lines of Code)
        actual_time = tool['base_time'] + (tool['time_per_loc'] * loc)
        total_time += actual_time
        
        # Cộng dồn Điểm Giá trị Bảo mật (F1-Score)
        total_score += tool['f1_score'] * 100
        
        # RÀNG BUỘC PHẦN CỨNG (Hard Constraint):
        # Vì 3 job chạy song song trên 3 Runner độc lập, ta check giới hạn RAM của từng Tool.
        # Nếu bất kỳ tool nào vượt RAM máy chủ -> Tổ hợp này vô giá trị (Return -1)
        if tool['peak_ram_mb'] > ram_limit:
            return -1, 0
            
    # RÀNG BUỘC NGÂN SÁCH (Budget Constraint):
    # Tổng thời gian (Billable CI/CD minutes) không được vượt giới hạn quản trị viên cấp
    if total_time > time_limit:
        return -1, 0
        
    return total_score, total_time

def main():
    # 1. THU THẬP BIẾN SỐ MÔI TRƯỜNG (Context Parameters)
    TIME_BUDGET = int(os.environ.get('TIME_BUDGET', 300))
    LOC_CHANGED = int(os.environ.get('LOC_CHANGED', 100))
    RAM_LIMIT = int(os.environ.get('RAM_LIMIT', 4096))
    
    # Mô phỏng Auto-detect ngôn ngữ (Trong tương lai lấy từ GitHub API)
    repo_langs = ['javascript', 'python'] 

    # 2. TRUY VẤN CƠ SỞ DỮ LIỆU THỰC CHỨNG
    try:
        client = pymongo.MongoClient(os.environ.get('MONGO_URI'), tlsAllowInvalidCertificates=True)
        db = client['devsecops']
        all_tools = list(db['tools'].find({}))
    except Exception as e:
        print(f"❌ Lỗi kết nối CSDL: {e}")
        sys.exit(1)

    # 3. BỘ LỌC CỨNG (Language & Category Filtering)
    sast_pool, sca_pool, dast_pool = [], [], []
    
    for tool in all_tools:
        # CHÌA KHÓA MỞ RỘNG: Chấp nhận công cụ có tag "all" (Black-box DAST/Secrets)
        is_supported = ("all" in tool['languages']) or any(l in tool['languages'] for l in repo_langs)
        
        if is_supported:
            if tool['category'] == 'SAST': sast_pool.append(tool)
            elif tool['category'] == 'SCA': sca_pool.append(tool)
            elif tool['category'] == 'DAST': dast_pool.append(tool)

    # Khởi tạo Biến Quyết định "Không Chọn" (Skip)
    skip_tool = {'id': 'skip', 'name': 'Bỏ qua', 'base_time': 0, 'time_per_loc': 0, 'peak_ram_mb': 0, 'f1_score': 0}
    sast_pool.append(skip_tool)
    sca_pool.append(skip_tool)
    dast_pool.append(skip_tool)

    # 4. ĐỘNG CƠ QUY HOẠCH TOÀN CỤC (ILP State-Space Search)
    best_score = -1
    best_combo = None
    best_time = 0

    # Không gian tìm kiếm: (N_sast + 1) * (N_sca + 1) * (N_dast + 1)
    # Tốc độ thực thi: Vài phần ngàn giây (Microseconds)
    for sast in sast_pool:
        for sca in sca_pool:
            for dast in dast_pool:
                score, time = evaluate_combination(sast, sca, dast, LOC_CHANGED, TIME_BUDGET, RAM_LIMIT)
                
                if score > best_score:
                    best_score = score
                    best_combo = (sast, sca, dast)
                    best_time = time

    # 5. ĐIỀU PHỐI KẾT QUẢ RA PIPELINE
    sast_choice = best_combo[0]['id'] if best_combo[0]['id'] != 'skip' else 'sast_skip'
    sca_choice = best_combo[1]['id'] if best_combo[1]['id'] != 'skip' else 'sca_skip'
    dast_choice = best_combo[2]['id'] if best_combo[2]['id'] != 'skip' else 'dast_skip'

    # In Log Báo cáo để kỹ sư Audit trên GitHub Actions
    print("="*65)
    print("🚀 KẾT QUẢ QUY HOẠCH TOÀN CỤC (ILP ENGINE)")
    print(f"Ngân sách: {TIME_BUDGET}s | Quy mô: {LOC_CHANGED} LOC | Max RAM: {RAM_LIMIT}MB")
    print("-" * 65)
    print(f"SAST : {best_combo[0].get('name'):<25} (Điểm F1: {best_combo[0].get('f1_score')}) | RAM: {best_combo[0].get('peak_ram_mb')}MB")
    print(f"SCA  : {best_combo[1].get('name'):<25} (Điểm F1: {best_combo[1].get('f1_score')}) | RAM: {best_combo[1].get('peak_ram_mb')}MB")
    print(f"DAST : {best_combo[2].get('name'):<25} (Điểm F1: {best_combo[2].get('f1_score')}) | RAM: {best_combo[2].get('peak_ram_mb')}MB")
    print("-" * 65)
    print(f">> Tổng điểm tối ưu: {round(best_score, 2)} / 300")
    print(f">> Tổng thời gian dự tính: {round(best_time, 2)}s")
    print("="*65)

    # Đẩy biến ra cho hệ thống Runner của GitHub đọc
    out_file = os.environ.get('GITHUB_OUTPUT')
    if out_file:
        with open(out_file, 'a') as f:
            f.write(f"sast_choice={sast_choice}\n")
            f.write(f"sca_choice={sca_choice}\n")
            f.write(f"dast_choice={dast_choice}\n")

if __name__ == "__main__":
    main()