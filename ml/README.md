# Dự đoán kết quả các trận bóng đá World Cup 2026

Project này xây dựng baseline Machine Learning để dự đoán kết quả trận đấu bóng đá quốc tế, hướng tới FIFA World Cup 2026.

## Mục tiêu

- Chuẩn hóa dữ liệu lịch sử trận đấu và bảng xếp hạng FIFA.
- Tạo đặc trưng: phong độ gần đây, hiệu số bàn thắng bại, lịch sử đối đầu, ranking, lợi thế chủ nhà.
- Huấn luyện mô hình phân loại kết quả `home_win`, `draw`, `away_win`.
- Huấn luyện mô hình hồi quy thử nghiệm để dự đoán tỷ số.
- Cung cấp CLI và demo Streamlit để nhập hai đội tuyển và nhận dự báo.

## Cấu trúc thư mục

```text
wc2026-football-prediction/
├── app/
│   └── streamlit_app.py
├── data/
│   ├── raw/
│   │   ├── sample_fifa_rankings.csv
│   │   └── sample_matches.csv
│   └── processed/
├── docs/
│   └── project_proposal.md
├── models/
├── notebooks/
├── reports/
├── src/
│   ├── config.py
│   ├── data_processing.py
│   ├── features.py
│   ├── predict.py
│   └── train.py
└── requirements.txt
```

## Cài đặt

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Huấn luyện mô hình

```powershell
python -m src.train
```

Kết quả sẽ được lưu vào:

- `models/result_classifier.joblib`
- `models/score_regressor.joblib`
- `reports/training_metrics.json`
- `data/processed/training_dataset.csv`

## Dự đoán bằng CLI

```powershell
python -m src.predict --home "France" --away "Japan"
```

Ví dụ output:

```text
France vs Japan
France thắng: 52.00%
Hòa: 25.00%
Japan thắng: 23.00%
Tỷ số dự đoán: France 2 - 1 Japan
```

## Chạy demo

```powershell
streamlit run app/streamlit_app.py
```

## Ghi chú dữ liệu

Hai file trong `data/raw/` chỉ là dữ liệu mẫu để chạy thử pipeline. Khi làm báo cáo hoặc demo chính thức, nên thay bằng dữ liệu lịch sử đầy đủ từ các nguồn đáng tin cậy như FIFA, Kaggle football results dataset, football-data.co.uk hoặc các API thể thao.

