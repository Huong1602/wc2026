# WC 2026 Football Prediction Platform

Project dự đoán kết quả các trận bóng đá World Cup 2026 dựa trên dữ liệu lịch sử, ranking FIFA, phong độ gần đây, lịch sử đối đầu và mô hình Machine Learning.

## Mục tiêu

- Thu thập và chuẩn hóa dữ liệu trận đấu quốc tế.
- Tạo bộ đặc trưng đầu vào cho bài toán dự đoán bóng đá.
- Huấn luyện và so sánh các mô hình:
  - Logistic Regression
  - Random Forest
  - XGBoost
- Dự đoán kết quả `home_win`, `draw`, `away_win`.
- Dự đoán tỷ số baseline bằng regression.
- Cung cấp prototype web để nhập hai đội tuyển và xem kết quả dự báo.

## Cấu trúc project

```text
WC2026 Prediction Platform/
├── backend/              # Express API + PostgreSQL
│   ├── db/init.sql       # Schema và seed data
│   └── src/
│       ├── controllers/
│       ├── routes/
│       └── services/
├── frontend/             # React + Vite + TailwindCSS
│   └── src/
│       └── components/
├── ml/                   # Machine Learning pipeline
│   ├── data/raw/         # Dữ liệu mẫu
│   ├── data/processed/   # Dataset sau xử lý
│   ├── models/           # Model sau train
│   ├── reports/          # Metrics đánh giá
│   └── src/
│       ├── data_processing.py
│       ├── features.py
│       ├── train.py
│       └── predict.py
└── docker-compose.yml
```

## Chạy fullstack demo

```powershell
docker compose up --build
```

Sau khi chạy:

- Frontend: http://localhost:5173
- Backend: http://localhost:3000
- PostgreSQL: localhost:5432

## Chạy ML pipeline

```powershell
cd ml
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.train
python -m src.predict --home "France" --away "Japan"
```

Kết quả train được lưu tại:

- `ml/models/result_classifier.joblib`
- `ml/models/score_regressor.joblib`
- `ml/reports/training_metrics.json`
- `ml/data/processed/training_dataset.csv`

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

## Đánh giá đúng yêu cầu

Project hiện có hai phần rõ ràng:

- `ml/`: đúng trọng tâm đề tài Machine Learning, gồm dữ liệu mẫu, feature engineering, train model, predict CLI và báo cáo metrics.
- `backend/` + `frontend/`: prototype/demo để người dùng nhập hai đội tuyển và xem dự đoán.

Lưu ý: backend hiện dùng heuristic baseline để demo nhanh trên web. Phần model ML thật nằm trong `ml/`; bước nâng cấp tiếp theo là nạp model `.joblib` từ `ml/models/` vào backend hoặc tạo Python prediction service riêng.

