import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import CLASSIFIER_FILE
from src.predict import predict_match


st.set_page_config(page_title="WC 2026 Predictor", page_icon="⚽", layout="centered")

st.title("Dự đoán kết quả bóng đá WC 2026")
st.caption("Prototype baseline dùng dữ liệu lịch sử mẫu và Machine Learning.")

if not CLASSIFIER_FILE.exists():
    st.warning("Chưa có mô hình. Hãy chạy `python -m src.train` trước.")
    st.stop()

with st.form("prediction-form"):
    home_team = st.text_input("Đội 1", value="France")
    away_team = st.text_input("Đội 2", value="Japan")
    match_date = st.text_input("Ngày thi đấu", value="2026-06-15")
    country = st.text_input("Quốc gia đăng cai", value="United States")
    neutral = st.checkbox("Sân trung lập", value=True)
    submitted = st.form_submit_button("Dự đoán")

if submitted:
    result = predict_match(
        home_team=home_team.strip(),
        away_team=away_team.strip(),
        match_date=match_date.strip(),
        neutral=neutral,
        country=country.strip(),
    )
    probabilities = result["probabilities"]

    st.subheader(f"{home_team} vs {away_team}")
    st.write(f"Mô hình: `{result['model_name']}`")

    col1, col2, col3 = st.columns(3)
    col1.metric(f"{home_team} thắng", f"{probabilities.get('home_win', 0.0) * 100:.2f}%")
    col2.metric("Hòa", f"{probabilities.get('draw', 0.0) * 100:.2f}%")
    col3.metric(f"{away_team} thắng", f"{probabilities.get('away_win', 0.0) * 100:.2f}%")

    if result["score_prediction"]:
        score = result["score_prediction"]
        st.info(f"Tỷ số dự đoán: {home_team} {score['home_score']} - {score['away_score']} {away_team}")

