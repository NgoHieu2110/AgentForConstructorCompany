"""
api/main.py
===========
FastAPI backend - lớp "cổng vào" duy nhất cho giao diện web (Streamlit sau này) hoặc
bất kỳ client nào khác gọi tới hệ thống. KHÔNG chứa logic tính toán - mọi logic thật
nằm ở services/evaluation_service.py, ở đây chỉ nhận request/trả response.

Chạy từ thư mục gốc project:
    uvicorn api.main:app --reload
Sau đó mở http://127.0.0.1:8000/docs để thấy giao diện thử API tự động (Swagger UI).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.database import get_session
from db.models import Supplier, Project, MaterialCategory, Bid, Decision
from ml.ml_risk_model import train_demo_model
from services.evaluation_service import evaluate_project

app = FastAPI(title="AI Chọn Nhà Cung Cấp Xây Dựng")

# Cho phép frontend (chạy ở địa chỉ/cổng khác, vd http://localhost:8080) gọi được API này.
# Để "*" cho tiện demo hackathon - khi triển khai thật nên giới hạn lại domain cụ thể.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Train 1 lần lúc khởi động server, dùng lại cho mọi request - tránh train lại mỗi lần gọi
_ml_model = train_demo_model()


# ---------------------------------------------------------------------------
# Pydantic schemas - định nghĩa "hình dạng" dữ liệu JSON mà client gửi lên/nhận về.
# Khác với models.py (bảng trong DB), đây chỉ là hình dạng cho request/response.
# ---------------------------------------------------------------------------
class SupplierIn(BaseModel):
    name: str
    province: str
    financial_rating: Optional[str] = None


class ProjectIn(BaseModel):
    name: str
    province: str
    budget: float
    required_deadline: Optional[date] = None
    requires_public_bidding: bool = False


class BidIn(BaseModel):
    project_id: str
    supplier_id: str
    category_name: str
    unit_price: float
    quantity_offered: float
    proposed_delivery_days: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/suppliers")
def create_supplier(data: SupplierIn):
    session = get_session()
    supplier = Supplier(name=data.name, province=data.province, financial_rating=data.financial_rating)
    session.add(supplier)
    session.commit()
    return {"supplier_id": supplier.supplier_id, "name": supplier.name}


@app.post("/projects")
def create_project(data: ProjectIn):
    session = get_session()
    project = Project(
        name=data.name, province=data.province, budget=data.budget,
        required_deadline=data.required_deadline,
        requires_public_bidding=data.requires_public_bidding,
    )
    session.add(project)
    session.commit()
    return {"project_id": project.project_id, "name": project.name}


@app.post("/bids")
def create_bid(data: BidIn):
    session = get_session()
    project = session.get(Project, data.project_id)
    supplier = session.get(Supplier, data.supplier_id)
    if project is None or supplier is None:
        raise HTTPException(status_code=404, detail="project_id hoặc supplier_id không tồn tại")

    category = session.query(MaterialCategory).filter_by(name=data.category_name).first()
    if category is None:
        category = MaterialCategory(name=data.category_name)
        session.add(category)
        session.commit()

    bid = Bid(
        project=project, supplier=supplier, category=category,
        unit_price=data.unit_price, quantity_offered=data.quantity_offered,
        proposed_delivery_days=data.proposed_delivery_days,
    )
    session.add(bid)
    session.commit()
    return {"bid_id": bid.bid_id}


@app.post("/projects/{project_id}/evaluate")
def evaluate(project_id: str):
    """Chạy toàn bộ pipeline (LLM đề xuất trọng số + rule-based + ML + LLM chấm điểm + LLM giải thích)."""
    session = get_session()
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_id không tồn tại")

    suppliers = list({bid.supplier for bid in project.bids})
    if not suppliers:
        raise HTTPException(status_code=400, detail="Dự án chưa có báo giá (bid) nào để đánh giá")

    decision = evaluate_project(session, project, suppliers, _ml_model)
    return {
        "decision_id": decision.decision_id,
        "chosen_supplier_id": decision.chosen_supplier_id,
        "ranking": decision.ranking_snapshot,
        "explanation": decision.explanation_text,
    }


@app.get("/projects/{project_id}/decision")
def get_decision(project_id: str):
    """Lấy lại kết quả đánh giá gần nhất đã lưu, không chạy lại pipeline."""
    session = get_session()
    decision = (
        session.query(Decision)
        .filter_by(project_id=project_id)
        .order_by(Decision.decided_at.desc())
        .first()
    )
    if decision is None:
        raise HTTPException(status_code=404, detail="Dự án chưa có quyết định nào - hãy gọi /evaluate trước")

    return {
        "chosen_supplier_id": decision.chosen_supplier_id,
        "ranking": decision.ranking_snapshot,
        "explanation": decision.explanation_text,
        "decided_at": decision.decided_at,
    }


@app.get("/")
def root():
    return {"message": "API đang chạy. Xem /docs để thử các endpoint."}
