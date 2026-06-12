# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcode API Key trực tiếp trong code (rủi ro bảo mật).
2. Hardcode Port 8000, không cho phép lấy qua biến môi trường.
3. Không có Health Check endpoints (`/health`, `/ready`).
4. Logging chỉ dùng `print()`, rất khó parse log khi đẩy lên các dịch vụ Cloud.
5. Thiếu cấu hình Graceful Shutdown, app tắt đột ngột làm mất các request đang xử lý.

### Exercise 1.3: Comparison table
| Feature | Basic | Advanced | Tại sao quan trọng? |
|---------|-------|----------|---------------------|
| Config | Hardcode | Env vars | Tránh lộ secrets (bảo mật), dễ dàng đổi port/cấu hình theo môi trường (linh hoạt) |
| Health check | Không có | Có endpoints | Giúp cloud platform tự động restart nếu app lỗi, hoặc biết khi nào app sẵn sàng nhận traffic |
| Logging | print() | JSON logging | Hệ thống quản lý log (Datadog, AWS CloudWatch) dễ dàng parse và truy vấn thông tin |
| Shutdown | Đột ngột | Graceful | Giúp các request đang được xử lý hoàn thành xong trước khi container thực sự tắt |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim`
2. Working directory: `/app`
3. Tại sao COPY requirements.txt trước? Để tận dụng Docker cache. Nếu file này không đổi, Docker không cần cài lại thư viện, giúp build cực nhanh.
4. CMD vs ENTRYPOINT: `CMD` cung cấp lệnh mặc định để chạy container nhưng rất dễ bị ghi đè lúc khởi chạy. `ENTRYPOINT` quy định file thực thi cứng, khó ghi đè hơn.

### Exercise 2.3: Image size comparison
- Develop: Ảnh hưởng bởi base image gốc (rất nặng).
- Production: Nhẹ hơn rất nhiều (~150 MB)
- Trọng tâm tối ưu nằm ở multi-stage build và bản `-slim`.

## Part 3: Cloud Deployment

### Exercise 3.1: Cloud deployment
- URL: Đã chuyển sang dùng nền tảng Render cho phần thực hành Final Project (Part 6).
- Xem cấu hình chi tiết và URL ở file `DEPLOYMENT.md`.

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Sử dụng thuật toán **Sliding Window** kết hợp với Redis (dùng `zadd`, `zremrangebyscore`) để đạt độ chuẩn xác cao nhất.
- Limit là 10 requests / minute.
- Không truyền Header `X-API-Key` lập tức Server chặn lại và trả về lỗi 401 Unauthorized.

### Exercise 4.4: Cost guard implementation
- Dùng Redis để theo dõi chi tiêu của từng user. Mỗi request gọi LLM cộng dồn 0.05$ (Mô phỏng).
- Nếu tổng chi phí trong tháng vượt ngân sách 10$, Server chặn đứng và báo lỗi HTTPException(402) Payment Required.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Health**: Liveness Probe (`/health`) hoạt động báo tình trạng uptime. Readiness Probe (`/ready`) luôn thử "ping" tới cục Redis trước khi thông báo "ready" cho Nginx.
- **Graceful Shutdown**: Bắt tín hiệu SIGTERM, chuyển trạng thái `_is_ready = False`, đồng thời đợi các in-flight requests (đang đếm) hoàn thành với vòng lặp timeout 30s mới thoát hẳn.
- Cấu hình Nginx đóng vai trò Load Balancer để phân tán tải qua 3 replicas của Agent, duy trì tính Stateless thông qua Redis (history chat được lưu thẳng xuống Redis).
