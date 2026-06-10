# WC 2026 Football Prediction Platform

Dự án dự đoán kết quả các trận bóng đá World Cup 2026 dựa trên dữ liệu lịch sử, ranking đội tuyển, phong độ gần đây, lịch sử đối đầu và mô hình Machine Learning.

## Mục tiêu

- Thu thập và chuẩn hóa dữ liệu trận đấu quốc tế.
- Tạo bộ đặc trưng đầu vào cho bài toán dự đoán bóng đá.
- Huấn luyện và so sánh các mô hình:
  - Logistic Regression
  - Random Forest
  - XGBoost
- Dự đoán kết quả `home_win`, `draw`, `away_win`.
- Dự đoán tỷ số bằng regression baseline.
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
│   ├── data/raw/         # Dữ liệu raw public + ranking Elo-derived
│   ├── data/processed/   # Dataset sau xử lý
│   ├── models/           # Model sau train
│   ├── notebooks/        # Notebook EDA
│   ├── reports/          # Metrics, figures, báo cáo
│   └── src/
│       ├── ingest_data.py
│       ├── eda.py
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
python -m src.ingest_data
python -m src.eda
python -m src.train
python -m src.predict --home "France" --away "Japan"
python -m src.tournament_simulator --simulations 100
```

Kết quả train được lưu tại:

- `ml/models/result_classifier.joblib`
- `ml/models/score_regressor.joblib`
- `ml/reports/training_metrics.json`
- `ml/reports/eda_summary.json`
- `ml/reports/figures/`
- `ml/data/processed/training_dataset.csv`
- `ml/reports/champion_probabilities.json`
- `ml/reports/group_stage_simulation.json`
- `ml/reports/knockout_bracket_prediction.json`

`ml/data/raw/matches.csv` được tải từ dataset public International Football Results. `ml/data/raw/rankings.csv` là ranking Elo-derived để pipeline có thể tái lập mà không cần API key.

## API chính

```http
GET /api/health
GET /api/teams
GET /api/matches
GET /api/model/metrics
GET /api/predictions
POST /api/predictions
GET /api/tournament/simulation
POST /api/tournament/simulate
```

Body mẫu:

```json
{
  "homeTeam": "France",
  "awayTeam": "Japan",
  "matchDate": "2026-06-15",
  "country": "United States",
  "tournament": "FIFA World Cup",
  "neutral": true
}
```

## Đánh giá đúng yêu cầu

- `ml/`: trọng tâm Data Science, gồm ingest dữ liệu, EDA, feature engineering, train/evaluate model, predict CLI và báo cáo.
- `backend/`: Express API, lưu lịch sử dự đoán vào PostgreSQL, gọi trực tiếp `ml/src/predict.py` để dùng model `.joblib`.
- `frontend/`: demo web nhập hai đội, hiển thị xác suất, tỷ số, model tốt nhất, top features và metrics đánh giá.

## Ghi chú học thuật

Model tốt nhất không nhất thiết có accuracy rất cao vì bóng đá có độ nhiễu lớn. Điểm quan trọng của dự án là pipeline Data Science rõ ràng: dữ liệu thật, feature có lý do, evaluation theo thời gian, metrics minh bạch và demo sử dụng đúng model đã train.

Tính năng tournament simulation dùng model hiện tại để mô phỏng vòng bảng, chọn đội đi tiếp, sinh nhánh knockout và tính xác suất vô địch. Bracket Round of 32 hiện là deterministic approximation để phục vụ demo học thuật.
