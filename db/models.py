"""
models.py
=========
Mỗi class ở đây tương ứng với 1 bảng trong database (giống sơ đồ ER đã vẽ).
Đây là "ORM" (Object-Relational Mapping) - cầu nối giữa OOP và database quan hệ:
  - Bạn viết code như OOP bình thường (class, object, thuộc tính).
  - SQLAlchemy tự dịch nó thành câu lệnh SQL (CREATE TABLE, INSERT, JOIN...) phía sau.

Cách đọc file này nếu bạn quen OOP:
  - `Column(...)`         -> giống 1 thuộc tính (attribute) của class, nhưng có thêm ràng buộc
                             kiểu dữ liệu để lưu xuống đĩa.
  - `ForeignKey(...)`     -> đây chính là "ID tham chiếu" đã nói ở câu trước
                             (giống việc Bid giữ Supplier.id thay vì giữ cả object).
  - `relationship(...)`   -> đây là phần "phép màu" biến ID đó thành object thật khi bạn
                             truy cập, ví dụ `bid.supplier.name` sẽ tự động JOIN bảng suppliers.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship


def gen_uuid() -> str:
    """Sinh ID duy nhất dạng chuỗi - dùng thay cho auto-increment vì dễ mở rộng/merge dữ liệu sau này."""
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Class gốc mà mọi 'bảng' phải kế thừa - tương tự như abstract base class trong OOP."""
    pass


# ---------------------------------------------------------------------------
# 1. SUPPLIERS - Hồ sơ nhà cung cấp
# ---------------------------------------------------------------------------
class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    tax_code = Column(String, unique=True)
    address = Column(Text)
    province = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    established_year = Column(Integer)
    financial_rating = Column(String)  # 'A' / 'B' / 'C'
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(Text)
    created_at = Column(DateTime, default=now_utc)

    # relationship = phía "1" trong quan hệ 1-nhiều.
    # back_populates giúp 2 chiều đồng bộ: supplier.bids <-> bid.supplier
    bids = relationship("Bid", back_populates="supplier")
    certifications = relationship("SupplierCertification", back_populates="supplier")
    performance_history = relationship("SupplierPerformanceHistory", back_populates="supplier")
    documents = relationship("SupplierDocument", back_populates="supplier")
    scores = relationship("SupplierScore", back_populates="supplier")
    risk_predictions = relationship("SupplierRiskPrediction", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.name} ({self.province})>"


# ---------------------------------------------------------------------------
# 2. MATERIAL_CATEGORIES - Danh mục vật tư/dịch vụ
# ---------------------------------------------------------------------------
class MaterialCategory(Base):
    __tablename__ = "material_categories"

    category_id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)  # vd: 'Xi măng', 'Thép xây dựng'
    unit = Column(String)  # tấn, m3, ngày công...

    def __repr__(self):
        return f"<MaterialCategory {self.name}>"


# ---------------------------------------------------------------------------
# 3. SUPPLIER_CERTIFICATIONS - Chứng chỉ, giấy phép
# ---------------------------------------------------------------------------
class SupplierCertification(Base):
    __tablename__ = "supplier_certifications"

    certification_id = Column(String, primary_key=True, default=gen_uuid)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    cert_type = Column(String)  # 'ISO 9001', 'Giấy phép kinh doanh'...
    cert_number = Column(String)
    issued_date = Column(Date)
    expiry_date = Column(Date)
    is_mandatory = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

    supplier = relationship("Supplier", back_populates="certifications")


# ---------------------------------------------------------------------------
# 4. SUPPLIER_PERFORMANCE_HISTORY - Lịch sử hợp tác trước đây
# ---------------------------------------------------------------------------
class SupplierPerformanceHistory(Base):
    __tablename__ = "supplier_performance_history"

    history_id = Column(String, primary_key=True, default=gen_uuid)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.project_id"))
    on_time_delivery = Column(Boolean)
    quality_issue_count = Column(Integer, default=0)
    delay_days = Column(Integer, default=0)
    incident_notes = Column(Text)
    rating_given = Column(Float)  # 1-5 hoặc 1-10
    recorded_at = Column(DateTime, default=now_utc)

    supplier = relationship("Supplier", back_populates="performance_history")


# ---------------------------------------------------------------------------
# 5. SUPPLIER_DOCUMENTS - Dữ liệu phi cấu trúc cho AI đọc
# ---------------------------------------------------------------------------
class SupplierDocument(Base):
    __tablename__ = "supplier_documents"

    document_id = Column(String, primary_key=True, default=gen_uuid)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    doc_type = Column(String)  # 'contract', 'incident_report', 'review'
    file_path = Column(Text)
    extracted_summary = Column(Text)
    source = Column(String)  # 'internal' hoặc 'public'
    created_at = Column(DateTime, default=now_utc)

    supplier = relationship("Supplier", back_populates="documents")


# ---------------------------------------------------------------------------
# 6. PROJECTS - Dự án xây dựng
# ---------------------------------------------------------------------------
class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    province = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    budget = Column(Float)
    required_deadline = Column(Date)
    requires_public_bidding = Column(Boolean, default=False)
    status = Column(String, default="sourcing")
    created_at = Column(DateTime, default=now_utc)

    bids = relationship("Bid", back_populates="project")
    criteria_weights = relationship("ProjectCriteriaWeight", back_populates="project")
    scores = relationship("SupplierScore", back_populates="project")
    decisions = relationship("Decision", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name} ({self.province})>"


# ---------------------------------------------------------------------------
# 7. CRITERIA - Danh mục tiêu chí đánh giá (dùng chung toàn hệ thống)
# ---------------------------------------------------------------------------
class Criterion(Base):
    __tablename__ = "criteria"

    criterion_id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)  # 'Giá', 'Thời gian giao', 'Rủi ro chậm/lỗi', 'Uy tín'
    data_type = Column(String)  # 'numeric_lower_better', 'numeric_higher_better', 'qualitative'
    # Tiêu chí này nên được tính bởi thành phần nào - giúp code biết gọi đúng "nguồn" khi chấm điểm
    score_source = Column(String)  # 'rule_based' | 'ml_model' | 'llm'
    description = Column(Text)

    def __repr__(self):
        return f"<Criterion {self.name} ({self.score_source})>"


# ---------------------------------------------------------------------------
# 8. PROJECT_CRITERIA_WEIGHTS - Trọng số tiêu chí theo TỪNG dự án
# ---------------------------------------------------------------------------
class ProjectCriteriaWeight(Base):
    """
    Khác với thiết kế ban đầu: trọng số ở đây mặc định do LLM ĐỀ XUẤT dựa trên bối cảnh
    dự án (deadline gấp hay không, có bắt buộc đấu thầu công khai không, ngân sách...),
    chứ không phải người dùng tự gõ tay ngay từ đầu. Con người vẫn có thể chỉnh lại,
    nhưng mọi thay đổi được đánh dấu qua cột `source` để giữ minh bạch.
    """
    __tablename__ = "project_criteria_weights"

    project_id = Column(String, ForeignKey("projects.project_id"), primary_key=True)
    criterion_id = Column(String, ForeignKey("criteria.criterion_id"), primary_key=True)
    weight = Column(Float, nullable=False)  # tổng các weight của 1 project nên = 1.0
    source = Column(String, default="ai_suggested")  # 'ai_suggested' | 'user_override'
    reasoning = Column(Text)  # lý do LLM đưa ra trọng số này (hoặc lý do người dùng sửa)

    project = relationship("Project", back_populates="criteria_weights")
    criterion = relationship("Criterion")


# ---------------------------------------------------------------------------
# 9. BIDS - Báo giá của NCC cho từng dự án
# ---------------------------------------------------------------------------
class Bid(Base):
    __tablename__ = "bids"

    bid_id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    category_id = Column(String, ForeignKey("material_categories.category_id"))
    unit_price = Column(Float)
    quantity_offered = Column(Float)
    proposed_delivery_days = Column(Integer)
    payment_terms = Column(Text)
    submitted_at = Column(DateTime, default=now_utc)

    # relationship = phía "nhiều" trong quan hệ 1-nhiều.
    project = relationship("Project", back_populates="bids")
    supplier = relationship("Supplier", back_populates="bids")
    category = relationship("MaterialCategory")

    def __repr__(self):
        return f"<Bid {self.supplier_id} -> {self.project_id}: {self.unit_price}>"


# ---------------------------------------------------------------------------
# 10. SUPPLIER_SCORES - Điểm từng tiêu chí, tính bởi rule-based / ML model / LLM
# ---------------------------------------------------------------------------
class SupplierScore(Base):
    """
    Mỗi dòng = điểm của 1 NCC cho 1 tiêu chí trong 1 dự án cụ thể.
    Cột `computed_by` cho biết điểm này đến từ đâu:
      - 'rule_based' : tính thẳng bằng công thức (vd: giá, thời gian giao - lấy từ Bid)
      - 'ml_model'   : lấy từ SupplierRiskPrediction (mô hình học từ lịch sử)
      - 'llm'        : Claude đọc supplier_documents/performance_history rồi cho điểm
    Nhờ tách theo criterion, Explanation Layer có thể giải thích breakdown rõ ràng
    thay vì chỉ đưa 1 con số tổng "hộp đen".
    """
    __tablename__ = "supplier_scores"

    score_id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    criterion_id = Column(String, ForeignKey("criteria.criterion_id"), nullable=False)

    raw_value = Column(Float)  # giá trị gốc, vd: 18_500_000 (VND) hoặc 0.23 (xác suất rủi ro)
    normalized_score = Column(Float)  # chuẩn hoá 0-1 để so sánh công bằng giữa các tiêu chí
    computed_by = Column(String)  # 'rule_based' | 'ml_model' | 'llm'
    reasoning = Column(Text)  # bắt buộc có nếu computed_by = 'llm' - lý do LLM chấm điểm này
    computed_at = Column(DateTime, default=now_utc)

    project = relationship("Project", back_populates="scores")
    supplier = relationship("Supplier", back_populates="scores")
    criterion = relationship("Criterion")


# ---------------------------------------------------------------------------
# 11. SUPPLIER_RISK_PREDICTIONS - Kết quả của ML model (không phải LLM)
# ---------------------------------------------------------------------------
class SupplierRiskPrediction(Base):
    """
    Đây là nơi ML model (vd: RandomForest/Logistic Regression huấn luyện trên
    supplier_performance_history) ghi lại dự đoán của nó. Tách riêng bảng này khỏi
    SupplierScore để giữ lại đầy đủ input features + version model dùng để dự đoán -
    phục vụ việc audit/tái huấn luyện sau này, điều mà LLM không cần (LLM không có
    "feature vector" cố định như ML model).
    """
    __tablename__ = "supplier_risk_predictions"

    prediction_id = Column(String, primary_key=True, default=gen_uuid)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    predicted_delay_risk = Column(Float)  # xác suất 0-1: NCC này có khả năng giao trễ/lỗi
    feature_snapshot = Column(JSON)  # input đưa vào model lúc dự đoán, vd: {"avg_delay_days": 4.2, ...}
    model_version = Column(String)  # vd: 'risk_model_v1_randomforest'
    predicted_at = Column(DateTime, default=now_utc)

    supplier = relationship("Supplier", back_populates="risk_predictions")


# ---------------------------------------------------------------------------
# 12. DECISIONS - Quyết định cuối cùng
# ---------------------------------------------------------------------------
class Decision(Base):
    __tablename__ = "decisions"

    decision_id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    chosen_supplier_id = Column(String, ForeignKey("suppliers.supplier_id"))
    total_score = Column(Float)
    ranking_snapshot = Column(JSON)  # đóng băng toàn bộ bảng xếp hạng tại thời điểm quyết định
    explanation_text = Column(Text)  # do LLM sinh ra
    decided_by = Column(String)
    decided_at = Column(DateTime, default=now_utc)

    project = relationship("Project", back_populates="decisions")
    chosen_supplier = relationship("Supplier")
    audit_logs = relationship("DecisionAuditLog", back_populates="decision")


# ---------------------------------------------------------------------------
# 13. DECISION_AUDIT_LOG - Nhật ký minh bạch
# ---------------------------------------------------------------------------
class DecisionAuditLog(Base):
    __tablename__ = "decision_audit_log"

    log_id = Column(String, primary_key=True, default=gen_uuid)
    decision_id = Column(String, ForeignKey("decisions.decision_id"), nullable=False)
    action = Column(String)  # 'weight_adjusted', 'supplier_excluded', 'manual_override'
    actor = Column(String)  # ai thực hiện (user hoặc 'system_ai')
    details = Column(JSON)
    created_at = Column(DateTime, default=now_utc)

    decision = relationship("Decision", back_populates="audit_logs")
