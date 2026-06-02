# WC 2026 Football Prediction Platform

Fullstack project dự đoán kết quả các trận bóng đá World Cup 2026.

## Công nghệ

- Frontend: React + Vite + TailwindCSS
- Backend: Node.js + Express
- Database: PostgreSQL
- Runtime: Docker + Docker Compose

## Chức năng

- Xem danh sách đội tuyển và ranking mẫu.
- Xem dữ liệu trận đấu lịch sử mẫu.
- Nhập hai đội tuyển để dự đoán:
  - Xác suất đội 1 thắng
  - Xác suất hòa
  - Xác suất đội 2 thắng
  - Tỷ số dự đoán baseline
- Lưu lịch sử dự đoán vào PostgreSQL.

## Chạy project

```powershell
docker compose up --build
```

Sau khi chạy:

- Frontend: http://localhost:5173
- Backend: http://localhost:3000
- PostgreSQL: localhost:5432

## API chính

```http
GET /api/health
GET /api/teams
GET /api/matches
GET /api/predictions
POST /api/predictions
```

Body mẫu:

```json
{
  "homeTeam": "France",
  "awayTeam": "Japan",
  "matchDate": "2026-06-15",
  "country": "United States",
  "neutral": true
}
```

## Ghi chú

Đây là baseline demo cho đề tài. Mô hình hiện tại dùng scoring heuristic dựa trên ranking, phong độ gần đây, đối đầu và lợi thế chủ nhà 2026. Khi làm bản nâng cao, có thể thay `backend/src/services/predictionService.js` bằng mô hình ML thật như Logistic Regression, Random Forest hoặc XGBoost.

