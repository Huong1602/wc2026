# Machine Learning Pipeline - WC 2026 Prediction

Thư mục này chứa toàn bộ phần Data Science của dự án dự đoán kết quả bóng đá World Cup 2026.

## Luồng xử lý

```text
ingest_data.py -> eda.py -> train.py -> predict.py
```

## Cài đặt

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Chạy pipeline

```powershell
python -m src.ingest_data
python -m src.eda
python -m src.train
python -m src.validate_pipeline
python -m src.predict --home "France" --away "Japan"
```

## Output chính

- `data/raw/matches.csv`: dữ liệu trận quốc tế public.
- `data/raw/rankings.csv`: ranking Elo-derived theo thời gian.
- `data/processed/training_dataset.csv`: dataset đã feature engineering.
- `models/result_classifier.joblib`: model phân loại thắng/hòa/thua.
- `models/score_regressor.joblib`: model dự đoán tỷ số.
- `reports/training_metrics.json`: metrics model.
- `reports/eda_summary.json`: kết quả EDA.
- `reports/figures/`: biểu đồ EDA và confusion matrix.
- `reports/final_report.md`: báo cáo học thuật tóm tắt.

## Prediction contract

`python -m src.predict --home "France" --away "Japan"` trả JSON:

```json
{
  "homeTeam": "France",
  "awayTeam": "Japan",
  "probabilities": {
    "homeWin": 0.31,
    "draw": 0.37,
    "awayWin": 0.32
  },
  "predictedScore": {
    "home": 1,
    "away": 1
  },
  "modelName": "random_forest",
  "topFeatures": ["rank_diff", "home_rank", "away_rank"]
}
```

## Ghi chú

Ranking hiện tại là Elo-derived vì nguồn FIFA ranking lịch sử dạng CSV ổn định thường cần API hoặc tải thủ công. Cách này phù hợp cho bài tập lớn vì tái lập được, không cần API key, và vẫn đại diện cho sức mạnh tương đối của đội tuyển theo thời gian.

