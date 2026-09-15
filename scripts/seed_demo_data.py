"""
scripts/seed_demo_data.py
==========================
Script tạo NHANH 1 bộ dữ liệu mẫu để demo/test, KHÔNG chứa logic tính điểm nữa -
toàn bộ logic đó giờ nằm ở services/evaluation_service.py và được gọi lại từ đây.

Chạy từ thư mục gốc project (KHÔNG phải từ trong scripts/):
    python -m scripts.seed_demo_data
"""

import sys
from datetime import date
from pathlib import Path

# Cho phép import các module ở thư mục gốc (db/, ml/, ai/, services/) khi chạy trực tiếp
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db.database import get_session
from db.models import (
    Supplier, MaterialCategory, SupplierCertification,
    SupplierPerformanceHistory, SupplierDocument, Project, Bid,
)
from ml.ml_risk_model import train_demo_model
from services.evaluation_service import evaluate_project


def create_sample_data(session):
    thep = MaterialCategory(name="Thép xây dựng", unit="tấn")
    session.add(thep)

    s1 = Supplier(name="Công ty Thép ABC", province="Đà Nẵng", financial_rating="A")
    s2 = Supplier(name="Công ty Thép XYZ", province="Đà Nẵng", financial_rating="B")
    s3 = Supplier(name="Công ty Thép Miền Trung", province="Huế", financial_rating="A")
    session.add_all([s1, s2, s3])

    session.add(SupplierCertification(
        supplier=s1, cert_type="ISO 9001", is_mandatory=True, verified=True,
    ))

    session.add_all([
        SupplierPerformanceHistory(supplier=s1, delay_days=2, quality_issue_count=0, rating_given=4.5),
        SupplierPerformanceHistory(supplier=s1, delay_days=5, quality_issue_count=0, rating_given=4.2),
        SupplierPerformanceHistory(supplier=s2, delay_days=10, quality_issue_count=1, rating_given=3.0),
        SupplierPerformanceHistory(supplier=s2, delay_days=12, quality_issue_count=2, rating_given=2.5),
        SupplierPerformanceHistory(supplier=s3, delay_days=0, quality_issue_count=0, rating_given=4.8),
    ])

    session.add_all([
        SupplierDocument(
            supplier=s1, doc_type="review", source="internal",
            extracted_summary="Từng giao chậm 5 ngày ở 1 dự án nhỏ năm 2023 nhưng chủ động báo trước và bồi thường hợp đồng.",
        ),
        SupplierDocument(
            supplier=s2, doc_type="incident_report", source="internal",
            extracted_summary="Có 2 lần bị khiếu nại chất lượng thép không đạt tiêu chuẩn trong năm 2024, đang trong diện theo dõi.",
        ),
        SupplierDocument(
            supplier=s3, doc_type="review", source="public",
            extracted_summary="Doanh nghiệp mới nhưng đội ngũ kỹ thuật xuất thân từ các công ty thép lớn, chưa có sự cố nào được ghi nhận.",
        ),
    ])

    project = Project(
        name="Xây cầu Sông Hàn giai đoạn 2",
        province="Đà Nẵng",
        budget=15_000_000_000,
        required_deadline=date(2026, 12, 31),
        requires_public_bidding=True,
    )
    session.add(project)

    session.add_all([
        Bid(project=project, supplier=s1, category=thep, unit_price=18_500_000,
            quantity_offered=500, proposed_delivery_days=20),
        Bid(project=project, supplier=s2, category=thep, unit_price=17_800_000,
            quantity_offered=500, proposed_delivery_days=25),
        Bid(project=project, supplier=s3, category=thep, unit_price=19_000_000,
            quantity_offered=500, proposed_delivery_days=15),
    ])

    session.commit()
    return project, [s1, s2, s3]


def main():
    session = get_session()

    print("== Tạo dữ liệu mẫu ==")
    project, suppliers = create_sample_data(session)

    print("== Huấn luyện ML model ==")
    ml_model = train_demo_model()

    print("== Chạy pipeline đánh giá (evaluation_service.evaluate_project) ==")
    decision = evaluate_project(session, project, suppliers, ml_model)

    print("\n== Kết quả ==")
    for i, r in enumerate(decision.ranking_snapshot, start=1):
        print(f"  #{i}: {r['supplier_name']} - {r['total_score']} điểm")
    print(f"\nGiải thích: {decision.explanation_text}")
    print("\nHoàn tất - dữ liệu đã lưu vào supplier_selection.db")


if __name__ == "__main__":
    main()
