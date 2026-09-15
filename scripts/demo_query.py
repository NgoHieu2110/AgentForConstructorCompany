"""
scripts/demo_query.py
======================
Đọc lại database, in ra kết quả để kiểm tra/debug. Chạy SAU khi đã có seed_demo_data.py
hoặc sau khi đã tạo dữ liệu qua API.

Chạy từ thư mục gốc project:
    python -m scripts.demo_query
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from db.database import get_session
from db.models import Project, Decision, SupplierRiskPrediction


def main():
    session = get_session()
    project = session.query(Project).order_by(Project.created_at.desc()).first()
    if project is None:
        print("Chưa có dự án nào trong database. Chạy scripts/seed_demo_data.py trước.")
        return

    print(f"\n=== Dự án: {project.name} ({project.province}) ===")

    print("\n--- Trọng số tiêu chí (do LLM đề xuất) ---")
    for w in project.criteria_weights:
        print(f"  {w.criterion.name}: {w.weight*100:.0f}%  [{w.source}]")
        print(f"      -> {w.reasoning}")

    print("\n--- Điểm từng NCC theo từng tiêu chí (kèm nguồn tính) ---")
    suppliers_seen = {}
    for s in project.scores:
        suppliers_seen.setdefault(s.supplier.name, []).append(s)
    for name, scores in suppliers_seen.items():
        print(f"\n  {name}:")
        for s in scores:
            tag = f"[{s.computed_by}]"
            print(f"    {s.criterion.name:<18} {tag:<14} điểm chuẩn hoá: {s.normalized_score:.2f}")
            if s.reasoning:
                print(f"        lý do (LLM): {s.reasoning}")

    print("\n--- Dự đoán rủi ro từ ML model ---")
    for pred in session.query(SupplierRiskPrediction).all():
        print(f"  {pred.supplier.name}: rủi ro = {pred.predicted_delay_risk:.1%} "
              f"(model: {pred.model_version})")

    print("\n--- Quyết định cuối cùng ---")
    decision = session.query(Decision).filter_by(project_id=project.project_id).first()
    print(f"  NCC được chọn: {decision.chosen_supplier.name} ({decision.total_score} điểm)")
    print(f"\n  Giải thích:\n  {decision.explanation_text}")


if __name__ == "__main__":
    main()
