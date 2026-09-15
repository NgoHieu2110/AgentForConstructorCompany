"""
ml_risk_model.py
=================
Đây là phần "ML model" thật sự (không phải LLM) trong hệ thống.

Bài toán: dự đoán xác suất một NCC sẽ GIAO TRỄ hoặc CÓ LỖI CHẤT LƯỢNG ở dự án tiếp theo,
dựa trên lịch sử hợp tác trước đây (bảng supplier_performance_history).

Vì sao dùng ML thay vì LLM ở đây: đây là bài toán học từ dữ liệu số có cấu trúc
(số ngày trễ, số lỗi, tỷ lệ đúng hạn...) - đúng sở trường của mô hình học máy cổ điển,
và cho kết quả nhất quán, dễ kiểm định hơn nhiều so với việc hỏi LLM "NCC này rủi ro không".

Class dùng: RandomForestClassifier - đơn giản, không cần tinh chỉnh nhiều, chịu được
dữ liệu ít (phù hợp demo hackathon), và cho ra được feature_importance để giải thích.
"""

import json
from collections import defaultdict

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

MODEL_VERSION = "risk_model_v1_randomforest"
MODEL_PATH = "risk_model.joblib"

FEATURE_NAMES = [
    "avg_delay_days",       # số ngày trễ trung bình các dự án trước
    "quality_issue_rate",   # tỷ lệ dự án có lỗi chất lượng
    "num_past_projects",    # số dự án đã từng làm - càng nhiều dữ liệu càng đáng tin
    "avg_rating",           # điểm đánh giá thủ công trung bình (1-5) của các dự án trước
]


def build_features_from_history(history_rows: list[dict]) -> dict:
    """
    Chuyển 1 danh sách bản ghi supplier_performance_history (dạng dict) của MỘT NCC
    thành 1 vector đặc trưng (feature vector) - đây là bước "feature engineering"
    kinh điển trong ML, khác hẳn cách LLM xử lý (LLM đọc thẳng text, không cần bước này).
    """
    if not history_rows:
        # NCC mới, chưa có lịch sử -> trả về feature trung tính, model sẽ tự học cách
        # xử lý trường hợp này nếu được train với đủ dữ liệu "cold start" mẫu.
        return {
            "avg_delay_days": 0.0,
            "quality_issue_rate": 0.0,
            "num_past_projects": 0,
            "avg_rating": 3.0,  # giả định trung bình khi chưa có dữ liệu
        }

    delays = [h["delay_days"] for h in history_rows]
    issues = [1 if h["quality_issue_count"] > 0 else 0 for h in history_rows]
    ratings = [h["rating_given"] for h in history_rows if h.get("rating_given") is not None]

    return {
        "avg_delay_days": float(np.mean(delays)),
        "quality_issue_rate": float(np.mean(issues)),
        "num_past_projects": len(history_rows),
        "avg_rating": float(np.mean(ratings)) if ratings else 3.0,
    }


def train_demo_model() -> RandomForestClassifier:
    """
    Huấn luyện model bằng dữ liệu MẪU tự sinh (synthetic) - dùng cho demo hackathon khi
    chưa có đủ dữ liệu lịch sử thật. Logic sinh dữ liệu: NCC trễ nhiều + lỗi nhiều +
    rating thấp -> nhãn risk=1 (rủi ro cao) ở lần hợp tác kế tiếp, và ngược lại.

    Khi có dữ liệu thật đủ lớn, chỉ cần thay hàm này bằng việc query thật từ DB
    (supplier_performance_history) và ghép nhãn "dự án sau đó có trễ/lỗi không".
    """
    rng = np.random.default_rng(42)
    n = 300
    avg_delay = rng.uniform(0, 15, n)
    issue_rate = rng.uniform(0, 1, n)
    num_projects = rng.integers(1, 20, n)
    avg_rating = rng.uniform(1, 5, n)

    # Nhãn rủi ro: công thức giả lập có nhiễu, không phải rule cứng 1-1
    risk_prob = (
        0.35 * (avg_delay / 15)
        + 0.35 * issue_rate
        + 0.20 * (1 - avg_rating / 5)
        - 0.10 * np.minimum(num_projects / 20, 1)  # nhiều dự án từng làm -> giảm rủi ro
    )
    noise = rng.normal(0, 0.08, n)
    labels = (risk_prob + noise > 0.4).astype(int)

    X = np.column_stack([avg_delay, issue_rate, num_projects, avg_rating])
    model = RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)
    model.fit(X, labels)

    joblib.dump(model, MODEL_PATH)
    print(f"Đã huấn luyện và lưu model vào {MODEL_PATH}")
    print("Feature importance:", dict(zip(FEATURE_NAMES, model.feature_importances_.round(3))))
    return model


def load_model() -> RandomForestClassifier:
    return joblib.load(MODEL_PATH)


def predict_risk(model: RandomForestClassifier, features: dict) -> float:
    """Trả về xác suất (0-1) NCC này sẽ trễ/lỗi ở dự án tiếp theo."""
    x = np.array([[features[name] for name in FEATURE_NAMES]])
    return float(model.predict_proba(x)[0][1])  # xác suất thuộc lớp "risk=1"


if __name__ == "__main__":
    model = train_demo_model()

    # Thử dự đoán cho 1 NCC ví dụ
    sample_features = {
        "avg_delay_days": 4.0,
        "quality_issue_rate": 0.2,
        "num_past_projects": 6,
        "avg_rating": 4.1,
    }
    risk = predict_risk(model, sample_features)
    print(f"\nVí dụ: NCC với features {sample_features}")
    print(f"-> Xác suất rủi ro chậm/lỗi: {risk:.2%}")
