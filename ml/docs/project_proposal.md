# Đề cương project: Dự đoán kết quả các trận bóng đá WC 2026

## Bài toán

Xây dựng hệ thống dự đoán kết quả trận đấu tại FIFA World Cup 2026 dựa trên dữ liệu lịch sử, thống kê đội bóng và mô hình học máy.

Các nhánh dự đoán chính:

- Phân loại kết quả: thắng, hòa, thua.
- Hồi quy tỷ số: số bàn thắng của mỗi đội.

## Đặc trưng đầu vào

- Xếp hạng FIFA của hai đội.
- Chênh lệch xếp hạng FIFA.
- Phong độ gần đây theo điểm trung bình.
- Hiệu số bàn thắng bại gần đây.
- Lịch sử đối đầu.
- Trận đấu sân trung lập hay không.
- Lợi thế đồng chủ nhà cho Mỹ, Canada, Mexico.

## Mô hình dự kiến

- Logistic Regression làm baseline dễ giải thích.
- Random Forest để xử lý quan hệ phi tuyến.
- XGBoost để so sánh mô hình boosting nếu môi trường có thư viện.

## Chỉ số đánh giá

- Accuracy.
- Precision, Recall, F1-score.
- Confusion matrix.
- Sai số dự đoán tỷ số nếu mở rộng hồi quy.

## Prototype

Demo cho phép nhập hai đội tuyển, sau đó trả về:

- Xác suất đội 1 thắng.
- Xác suất hòa.
- Xác suất đội 2 thắng.
- Tỷ số dự đoán thử nghiệm.

