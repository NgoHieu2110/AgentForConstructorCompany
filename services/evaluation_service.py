"""
services/evaluation_service.py
================================
Đây là nơi DUY NHẤT chứa logic "chấm điểm NCC cho 1 dự án". Cả api/main.py (khi có
request từ web) và scripts/seed_demo_data.py (khi tạo dữ liệu demo) đều gọi vào đây,
KHÔNG viết lại logic ở 2 nơi.

Khác biệt so với seed_data.py cũ: mọi hàm ở đây nhận project/suppliers/criteria làm
THAM SỐ, không tự tạo dữ liệu hard-code bên trong. Điều này giúp hàm evaluate_project()
dùng được cho BẤT KỲ dự án nào, không chỉ dự án mẫu "Xây cầu Sông Hàn".
"""

from sqlalchemy.orm import Session

from db.models import (
    Project, Supplier, Criterion, ProjectCriteriaWeight,
    SupplierScore, SupplierRiskPrediction, Decision,
)
from ml.ml_risk_model import build_features_from_history, predict_risk, MODEL_VERSION
from ai.llm_layer import suggest_criteria_weights, score_reputation_from_text, generate_final_explanation


DEFAULT_CRITERIA = [
    {"key": "price", "name": "Giá", "data_type": "numeric_lower_better", "score_source": "rule_based"},
    {"key": "delivery", "name": "Thời gian giao", "data_type": "numeric_lower_better", "score_source": "rule_based"},
    {"key": "risk", "name": "Rủi ro chậm/lỗi", "data_type": "numeric_lower_better", "score_source": "ml_model"},
    {"key": "reputation", "name": "Uy tín", "data_type": "numeric_higher_better", "score_source": "llm"},
]


def ensure_default_criteria(session: Session) -> dict:
    """
    Đảm bảo 4 tiêu chí mặc định tồn tại trong DB (chỉ tạo nếu chưa có - tránh tạo
    trùng lặp mỗi lần gọi). Trả về dict {key: Criterion object} để các hàm khác dùng.
    """
    result = {}
    for c in DEFAULT_CRITERIA:
        existing = session.query(Criterion).filter_by(name=c["name"]).first()
        if existing is None:
            existing = Criterion(name=c["name"], data_type=c["data_type"], score_source=c["score_source"])
            session.add(existing)
            session.commit()
        result[c["key"]] = existing
    return result


def suggest_weights_with_llm(session: Session, project: Project, criteria: dict) -> list[dict]:
    """Bước 1: LLM đề xuất trọng số dựa trên bối cảnh dự án. Ghi vào project_criteria_weights."""
    context = {
        "deadline": str(project.required_deadline) if project.required_deadline else "không rõ",
        "requires_public_bidding": project.requires_public_bidding,
        "budget": project.budget,
    }
    criteria_names = [c.name for c in criteria.values()]
    suggestions = suggest_criteria_weights(context, criteria_names)

    name_to_criterion = {c.name: c for c in criteria.values()}
    for s in suggestions:
        crit = name_to_criterion.get(s["criterion"])
        if crit is None:
            continue
        session.add(ProjectCriteriaWeight(
            project=project, criterion=crit,
            weight=s["weight"], source="ai_suggested", reasoning=s["reasoning"],
        ))
    session.commit()
    return suggestions


def score_price_and_delivery(session: Session, project: Project, criteria: dict):
    """Bước 2a: tiêu chí rule-based - tính thẳng từ Bid, không cần AI."""
    bids = project.bids
    if not bids:
        return
    prices = [b.unit_price for b in bids]
    deliveries = [b.proposed_delivery_days for b in bids]
    min_p, max_p = min(prices), max(prices)
    min_d, max_d = min(deliveries), max(deliveries)

    for bid in bids:
        price_norm = 1 - (bid.unit_price - min_p) / (max_p - min_p) if max_p > min_p else 1.0
        delivery_norm = 1 - (bid.proposed_delivery_days - min_d) / (max_d - min_d) if max_d > min_d else 1.0

        session.add(SupplierScore(
            project=project, supplier=bid.supplier, criterion=criteria["price"],
            raw_value=bid.unit_price, normalized_score=price_norm, computed_by="rule_based",
        ))
        session.add(SupplierScore(
            project=project, supplier=bid.supplier, criterion=criteria["delivery"],
            raw_value=bid.proposed_delivery_days, normalized_score=delivery_norm, computed_by="rule_based",
        ))
    session.commit()


def score_risk_with_ml(session: Session, project: Project, suppliers: list[Supplier], criteria: dict, ml_model):
    """Bước 2b: tiêu chí ML model - dự đoán rủi ro từ lịch sử hợp tác."""
    for supplier in suppliers:
        history_rows = [
            {"delay_days": h.delay_days, "quality_issue_count": h.quality_issue_count,
             "rating_given": h.rating_given}
            for h in supplier.performance_history
        ]
        features = build_features_from_history(history_rows)
        risk = predict_risk(ml_model, features)

        session.add(SupplierRiskPrediction(
            supplier=supplier, predicted_delay_risk=risk,
            feature_snapshot=features, model_version=MODEL_VERSION,
        ))
        session.add(SupplierScore(
            project=project, supplier=supplier, criterion=criteria["risk"],
            raw_value=risk, normalized_score=1 - risk, computed_by="ml_model",
        ))
    session.commit()


def score_reputation_with_llm(session: Session, project: Project, suppliers: list[Supplier], criteria: dict):
    """Bước 2c: tiêu chí LLM - đọc tài liệu phi cấu trúc, chấm điểm uy tín."""
    for supplier in suppliers:
        texts = [d.extracted_summary for d in supplier.documents if d.extracted_summary]
        result = score_reputation_from_text(supplier.name, texts)

        session.add(SupplierScore(
            project=project, supplier=supplier, criterion=criteria["reputation"],
            raw_value=result["score"], normalized_score=result["score"] / 100,
            computed_by="llm", reasoning=result["reasoning"],
        ))
    session.commit()


def finalize_decision(session: Session, project: Project, suppliers: list[Supplier]) -> Decision:
    """Bước 3: tổng hợp điểm theo trọng số, gọi LLM viết giải thích, lưu Decision."""
    weights = {w.criterion_id: w.weight for w in project.criteria_weights}

    ranking = []
    for supplier in suppliers:
        scores = [s for s in supplier.scores if s.project_id == project.project_id]
        total = sum(s.normalized_score * weights.get(s.criterion_id, 0) for s in scores)
        breakdown = [
            {"criterion": s.criterion.name, "normalized_score": round(s.normalized_score, 3),
             "computed_by": s.computed_by}
            for s in scores
        ]
        ranking.append({
            "supplier_id": supplier.supplier_id,
            "supplier_name": supplier.name,
            "total_score": round(total * 100, 1),
            "criterion_breakdown": breakdown,
        })

    ranking.sort(key=lambda r: r["total_score"], reverse=True)
    explanation = generate_final_explanation(project.name, ranking)

    decision = Decision(
        project=project,
        chosen_supplier_id=ranking[0]["supplier_id"],
        total_score=ranking[0]["total_score"],
        ranking_snapshot=ranking,
        explanation_text=explanation,
        decided_by="system_ai_pipeline",
    )
    session.add(decision)
    session.commit()
    return decision


def evaluate_project(session: Session, project: Project, suppliers: list[Supplier], ml_model) -> Decision:
    """
    HÀM CHÍNH - gọi hàm này từ bên ngoài (API hoặc script) để chạy toàn bộ pipeline
    cho 1 project + danh sách suppliers BẤT KỲ, không hard-code.
    """
    criteria = ensure_default_criteria(session)
    suggest_weights_with_llm(session, project, criteria)
    score_price_and_delivery(session, project, criteria)
    score_risk_with_ml(session, project, suppliers, criteria, ml_model)
    score_reputation_with_llm(session, project, suppliers, criteria)
    return finalize_decision(session, project, suppliers)
