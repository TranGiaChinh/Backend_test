# Task Management System - Backend API

## 1. Giới thiệu
Hệ thống Backend quản lý công việc (Task Management) được xây dựng với kiến trúc hiện đại, ứng dụng xử lý bất đồng bộ (Async) nhằm đảm bảo hiệu năng cao và tính nhất quán dữ liệu.
* **Framework:** FastAPI (Python 3.13)
* **Database:** MongoDB
* **Cache & Message Broker:** Redis
* **Deployment:** Docker & Docker Compose

## 2. Setup Guide (Hướng dẫn cài đặt)
Hệ thống đã được đóng gói hoàn chỉnh. Bạn không cần cài đặt Python hay Database trực tiếp lên máy chủ.

**Yêu cầu hệ thống:**
* Máy tính đã cài đặt sẵn **Docker** và **Docker Desktop / Compose**.

**Các bước khởi chạy:**
1. Mở Terminal (Command Prompt / PowerShell) tại thư mục gốc của dự án.
2. Gõ lệnh sau để hệ thống tự động tải môi trường, cài đặt thư viện và khởi chạy các dịch vụ:
   ```bash
   docker compose up -d --build
3. Hệ thống sẽ khởi động 4 container song song: mongodb, redis, api (server chính), và worker (chạy ngầm).
4. Khi terminal báo Started cho tất cả các container, hệ thống đã sẵn sàng hoạt động.

## 3. Database Design (MongoDB)

Hệ thống sử dụng MongoDB để lưu trữ dữ liệu. Dưới đây là cấu trúc các Collections cốt lõi:

### 3.1. Document Structure

* **`users` collection:**
    * `_id`: ObjectId (Tự động tạo)
    * `email`: String (ví dụ: "admin@gmail.com")
    * `hashed_password`: String (Mật khẩu đã mã hóa)
    * `full_name`: String

* **`projects` collection:**
    * `_id`: ObjectId
    * `name`: String
    * `description`: String
    * `owner_id`: ObjectId (Reference tới `users._id`)

* **`tasks` collection:**
    * `_id`: ObjectId
    * `title`: String
    * `status`: String (todo, doing, done)
    * `project_id`: ObjectId (Reference tới `projects._id`)
    * `assignee_id`: ObjectId (Reference tới `users._id`)
    * `tags`: Array of Strings (Embedded documents, VD: ["bug", "urgent"])
    * `created_at`: DateTime

* **`comments` collection:**
    * `_id`: ObjectId
    * `task_id`: ObjectId (Reference tới `tasks._id`)
    * `user_id`: ObjectId (Reference tới `users._id`)
    * `content`: String

* **`activity_logs` collection:**
    * `_id`: ObjectId
    * `action`: String (create, update, delete)
    * `entity_id`: ObjectId (ID của task vừa bị tác động)
    * `timestamp`: DateTime

### 3.2. Reference vs Embedded
* **Reference (Tham chiếu):** Mình sử dụng tham chiếu (lưu ObjectId) cho các mối quan hệ như `Task -> Project` hoặc `Comment -> Task`. Lý do là số lượng task trong một project có thể tăng lên vô hạn. Nếu dùng Embedded (nhúng toàn bộ data task vào trong data project), dung lượng của một document sẽ rất nhanh vượt quá giới hạn 16MB của MongoDB. Việc dùng Reference giúp dễ dàng phân trang dữ liệu khi query.
* **Embedded (Nhúng):** Mình sử dụng Embedded cho mảng `tags` bên trong collection `tasks`. Vì các thẻ tag (như "bug", "feature") là những dữ liệu cực nhỏ, số lượng ít và luôn đi kèm với task khi hiển thị lên giao diện. Nhúng trực tiếp giúp giảm bớt số lần gọi (query) vào Database.

### 3.3. Chiến lược Index
* **Unique Index:** Áp dụng cho trường `email` của collection `users`. Đảm bảo tính duy nhất, không có 2 tài khoản trùng email, đồng thời tăng tốc độ tìm kiếm khi user đăng nhập.
* **Compound Index (Chỉ mục kết hợp):** Áp dụng cho `{project_id: 1, status: 1}` trong collection `tasks`. Vì API thường xuyên phải lấy danh sách task theo dự án và lọc theo trạng thái (VD: lấy các task "done" của project A), Compound Index giúp Database tìm kiếm cực nhanh mà không phải quét toàn bộ collection.

## 4. API Documentation

Hệ thống tuân thủ nguyên tắc RESTful API. Dữ liệu trao đổi (Request/Response) được định dạng dưới chuẩn JSON.

### 4.1. User Management APIs

* **Tạo User mới**
  * **Endpoint:** `POST /users`
  * **Request Body:** 
  ```json
    {
      "email": "chinh@example.com",
      "password": "strongpassword123",
      "full_name": "Tran Gia Chinh"
    }
    ```
  * **Response (Thành công - 201 Created):** Trả về thông tin user (không chứa password).
  * **Response (Lỗi - 400 Bad Request):** Nếu email đã tồn tại hoặc thiếu trường dữ liệu.

* **Lấy thông tin User**
  * **Endpoint:** `GET /users/{id}`
  * **Response (Thành công - 200 OK):** Trả về JSON chứa `_id`, `email`, `full_name`.
  * **Response (Lỗi - 404 Not Found):** Nếu ID không tồn tại.

### 4.2. Project Management APIs

* **Tạo Dự án mới**
  * **Endpoint:** `POST /projects`
  * **Request Body:** 
  ```json
    {
      "name": "Backend Test Project",
      "description": "Dự án quản lý API cho bài test"
    }
    ```
  * **Response (201 Created):** Trả về thông tin Project vừa tạo kèm `_id` để sử dụng cho việc tạo Task.

### 4.3. Task Management APIs (Core Entity)

* **Lấy danh sách Công việc (Có Phân trang & Lọc)**
  * **Endpoint:** `GET /tasks`
  * **Query Parameters (Pagination):** `?page=1&limit=10&status=done` 
  * **Response (200 OK):**
    ```json
    {
      "data": [
        {
          "_id": "65abc123...",
          "title": "Fix login bug",
          "status": "done",
          "project_id": "65def456..."
        }
      ],
      "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "total_items": 45
      }
    }
    ```

* **Tạo Công việc mới**
  * **Endpoint:** `POST /tasks`
  * **Request Body:** Yêu cầu gửi lên `title`, `project_id`.
  * **Response (201 Created):** Trả về thông tin Task vừa tạo kèm `_id`.

* **Cập nhật Công việc**
  * **Endpoint:** `PUT /tasks/{id}` (hoặc `PATCH /tasks/{id}`)
  * **Request Body:** Gửi lên các trường cần sửa (ví dụ chỉ gửi `{"status": "done"}`).
  * **Response (200 OK):** Trả về thông tin Task sau khi đã cập nhật.

* **Xóa Công việc**
  * **Endpoint:** `DELETE /tasks/{id}`
  * **Response (200 OK hoặc 204 No Content):** Xóa thành công.
  * **Response (404 Not Found):** Nếu Task ID không tồn tại.

### 4.4. Comment APIs

* **Tạo Bình luận cho Task**
  * **Endpoint:** `POST /comments`
  * **Request Body:** Yêu cầu gửi lên `task_id`, `user_id` và `content` (nội dung bình luận).
  * **Response (201 Created):** Trả về thông tin bình luận kèm thời gian tạo.

* **Lấy danh sách Bình luận của 1 Task**
  * **Endpoint:** `GET /tasks/{task_id}/comments`
  * **Response (200 OK):** Trả về mảng các bình luận thuộc về Task đó, được sắp xếp từ mới nhất đến cũ nhất.

### 4.5. Activity Log API (Event-driven)

* **Xem lịch sử hoạt động của hệ thống**
  * **Endpoint:** `GET /logs`
  * **Query Parameters:** `?limit=50` (Giới hạn số lượng log hiển thị).
  * **Response (200 OK):** Trả về danh sách các sự kiện (ví dụ: `task.created`, `task.updated`) do hệ thống Background Worker tự động ghi nhận ngầm thông qua Redis Pub/Sub.