# Báo cáo dự án: Dự đoán kết quả các trận bóng đá WC 2026

## 1. Giới thiệu bài toán

Dự án xây dựng hệ thống dự đoán kết quả các trận đấu bóng đá quốc tế, hướng tới FIFA World Cup 2026. Bài toán chính là phân loại kết quả trận đấu thành ba lớp: đội 1 thắng, hòa, đội 2 thắng. Phần mở rộng dự đoán tỷ số bằng mô hình hồi quy.

## 2. Dữ liệu

Dữ liệu trận đấu được lấy từ bộ dữ liệu public International Football Results, gồm các trận quốc tế từ năm 1872 đến năm 2026. Các cột chính gồm ngày thi đấu, hai đội, tỷ số, giải đấu, quốc gia tổ chức và trạng thái sân trung lập.

Do không có file FIFA ranking lịch sử chính thức dạng CSV ổn định trong repo, dự án sinh `rankings.csv` bằng Elo rating từ chính dữ liệu trận đấu. Cách này giúp pipeline tái lập được và vẫn phản ánh sức mạnh đội bóng theo thời gian.

## 3. Tiền xử lý

Các bước tiền xử lý:

- Chuẩn hóa ngày thi đấu về kiểu datetime.
- Loại bỏ trận thiếu tỷ số.
- Chuẩn hóa tên đội, giải đấu và quốc gia.
- Loại bỏ duplicate theo `date + home_team + away_team`.
- Sinh nhãn `home_win`, `draw`, `away_win`.

## 4. EDA

Kết quả EDA chính:

- Lớp hòa là lớp thiểu số, nên accuracy không đủ để đánh giá toàn diện.
- Trận không trung lập có tỷ lệ đội chủ nhà thắng cao hơn trận trung lập.
- Số bàn thắng trung bình mỗi trận khoảng 3 bàn, nhưng thay đổi theo tournament.
- Ranking/strength cần kết hợp với phong độ gần đây vì sức mạnh đội thay đổi theo thời gian.

Biểu đồ được lưu trong `reports/figures/`.

## 5. Feature engineering

Các feature chính:

- Ranking: `home_rank`, `away_rank`, `rank_diff`.
- Phong độ gần đây: điểm trung bình, hiệu số bàn thắng bại, số bàn ghi được.
- Đối đầu: `h2h_home_points`.
- Bối cảnh trận đấu: `neutral`, `tournament_importance`.
- World Cup 2026: lợi thế đồng chủ nhà của United States, Canada, Mexico.
- Feature nâng cao: số ngày từ trận gần nhất, điểm World Cup gần đây.

## 6. Mô hình

Các mô hình classification:

- Logistic Regression.
- Random Forest.
- XGBoost nếu môi trường có thư viện.

Mô hình regression:

- Random Forest Regressor để dự đoán `home_score` và `away_score`.

Evaluation dùng split theo thời gian 80/20 để tránh leakage từ tương lai vào quá khứ.

## 7. Kết quả

Metrics chi tiết nằm trong `reports/training_metrics.json`. Web demo đọc trực tiếp file này thông qua backend và hiển thị best model, accuracy, macro F1, số dòng dữ liệu và top features.

## 8. Demo hệ thống

Người dùng nhập hai đội tuyển trên web, backend gọi `ml/src/predict.py`, model trả về:

- Xác suất đội 1 thắng.
- Xác suất hòa.
- Xác suất đội 2 thắng.
- Tỷ số dự đoán.
- Tên mô hình tốt nhất.
- Top features ảnh hưởng mạnh.

## 9. Hạn chế

- Chưa có dữ liệu đội hình, chấn thương, lịch thi đấu dày đặc hoặc chiến thuật.
- Ranking đang là Elo-derived, không phải FIFA ranking chính thức.
- World Cup 2026 chưa diễn ra, nên dự đoán chỉ mang tính thử nghiệm học thuật.

## 10. Hướng phát triển

- Bổ sung FIFA ranking chính thức nếu có nguồn CSV/API ổn định.
- Tối ưu hyperparameter bằng cross-validation theo thời gian.
- Thêm calibration cho xác suất.
- Thêm explainability bằng SHAP hoặc permutation importance.

