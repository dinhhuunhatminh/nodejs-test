# Tối ưu hóa các công cụ bảo mật trong DevOps Pinelines bằng thuật toán Quy hoạch động (nodejs-test)

Dự án này là một nguyên mẫu (prototype) mô phỏng một đường ống CI/CD bảo mật thông minh. Thay vì chạy tất cả các công cụ quét mã nguồn một cách cứng nhắc, hệ thống tích hợp **Thuật toán Quy hoạch động (Knapsack)** để tối ưu hóa thời gian chạy và sử dụng **Trí tuệ nhân tạo (LLM)** để tương tác trực tiếp với lập trình viên trên nền tảng GitHub.

Ứng dụng mẫu được sử dụng để kiểm thử là một Web Server Node.js (dựa trên `nodejs-getting-started` của Heroku).

## Tính năng cốt lõi

*  Smart Orchestration (Điều phối thông minh):** Sử dụng thuật toán Knapsack (Python) để tự động chọn lọc các công cụ SAST, SCA, DAST phù hợp với ngân sách thời gian (Time Budget).
*  AI Security Reviewer:** Tích hợp Google Gemini API. AI tự động đọc các báo cáo JSON/SARIF khô khan, dịch thành ngôn ngữ tự nhiên và comment hướng dẫn sửa lỗi ngay trên Pull Request.
*  Self-Learning Mechanism (Cơ chế tự học):** Sử dụng thuật toán EMA (Exponential Moving Average) để tự động cập nhật thời gian chạy và điểm số hiệu năng (v_score) của các tool lên MongoDB sau mỗi lần chạy.
*  Continuous Deployment (Triển khai liên tục):** Đóng gói bằng Docker (multi-layer) và tự động cập nhật image trên server thông qua Watchtower.

## 🗂 Cấu trúc dự án
Các file được tạo thêm hoặc có chỉnh sửa quan trọng 
\`\`\`text
nodejs-test
 ┣  .github/workflows
 ┃ ┗  ai-devsecops-pipeline.yml  # Kịch bản CI/CD cốt lõi - workflow dùng chính
 ┣  data
 ┣  public
 ┣  view
 ┣  index.js                       
 ┣  Dockerfile                     # Đóng gói ứng dụng (node:18-alpine)
 ┣  dp_optimizer_2.py              # Thuật toán Knapsack
 ┣  dp_optimizer.py                # Thuật toán Tham lam để so sánh với Knapsack
 ┣  feedback_updater.py            # Thuật toán EMA cập nhật DB
 ┣  migrate_db.py                  # Script nạp dữ liệu lên MongoDB
 ┗  package.json                   # Quản lý dependencies Node.js
\`\`\`

##  Thiết lập và Cấu hình (Dành cho Fork/Clone)

Để pipeline này có thể hoạt động trên repo của riêng bạn, hãy vào **Settings > Secrets and variables > Actions** và cấu hình các biến bảo mật (Repository Secrets) sau:

* `MONGO_URI`: Chuỗi kết nối đến MongoDB Atlas của bạn (dùng cho thuật toán đọc/ghi chỉ số).
* `GEMINI_API_KEY`: API Key của Google Gemini (dùng cho AI Code Reviewer).
* `GITHUB_TOKEN`: (Đã có sẵn mặc định) Cấp quyền cho workflow có thể comment vào Pull Request.

##  Hướng dẫn vận hành Pipeline

Hệ thống CI/CD được thiết kế tự động hoàn toàn. Để kích hoạt và kiểm thử các tính năng:

1. **Kiểm thử Thuật toán (Push to Main):** Thực hiện commit và push một thay đổi bất kỳ lên nhánh `main`. Truy cập tab **Actions**, bạn sẽ thấy luồng chạy thực thi, Job `brain_optimizer` sẽ phân bổ thời gian và kích hoạt các Job quét tương ứng.
2. **Kiểm thử AI Reviewer (Tạo Pull Request):**
   * Tạo một nhánh mới (vd: `test-loi-ai`).
   * Cố tình thêm một lỗ hổng bảo mật vào `index.js` (Ví dụ: Hardcode mật khẩu hoặc dùng hàm `eval()`).
   * Mở một **Pull Request** yêu cầu gộp vào `main`.
   * Đợi khoảng 2-3 phút, bot AI sẽ tự động comment chi tiết lỗi và cách khắc phục bằng tiếng Việt ngay trong luồng thảo luận của PR.

## 🛠 Công nghệ sử dụng

* **App:** Node.js, Express.
* **DevSecOps Tools:** Semgrep, Trivy, ZAP.
* **Pipeline:** GitHub Actions, Python 3.10.
* **Database & AI:** MongoDB, Google Gemini 1.5.