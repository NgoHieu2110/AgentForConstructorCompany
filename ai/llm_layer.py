"""
llm_layer.py
============
Đây là phần "LLM" trong hệ thống - dùng Claude cho 3 việc mà ML model KHÔNG làm tốt:

  1. suggest_criteria_weights()  -> đọc bối cảnh dự án (ngôn ngữ tự nhiên/thuộc tính),
                                     đề xuất trọng số hợp lý. Đây là suy luận theo ngữ cảnh,
                                     không phải học từ dữ liệu số - hợp với LLM hơn ML.
  2. score_reputation_from_text() -> đọc văn bản tự do (ghi chú sự cố, review, tài liệu)
                                     rồi cho điểm uy tín + giải thích - ML model không đọc
                                     được text phi cấu trúc kiểu này nếu không có bước NLP riêng.
  3. generate_final_explanation() -> tổng hợp toàn bộ điểm số (rule-based + ML + LLM)
                                     thành 1 đoạn giải thích minh bạch, dễ hiểu cho người ra
                                     quyết định.

Nếu chưa có ANTHROPIC_API_KEY trong biến môi trường, các hàm sẽ dùng fallback đơn giản
(heuristic) để code vẫn chạy được khi demo mà không cần key - nhưng bạn nên set key thật
khi nộp bài để thể hiện đúng "hiệu quả ứng dụng AI".
"""

import json
import os

import anthropic

MODEL_NAME = "claude-sonnet-4-6"

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _call_claude_json(prompt: str) -> dict | None:
    """Gọi Claude, yêu cầu trả về JSON thuần, tự parse. Trả None nếu không có API key."""
    client = _get_client()
    if client is None:
        return None
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# 1. Đề xuất trọng số tiêu chí theo bối cảnh dự án
# ---------------------------------------------------------------------------
def suggest_criteria_weights(project_context: dict, criteria_names: list[str]) -> list[dict]:
    """
    project_context: vd {"deadline_urgency": "gấp trong 2 tháng", "requires_public_bidding": True,
                          "budget_sensitivity": "cao"}
    Trả về: [{"criterion": "Giá", "weight": 0.4, "reasoning": "..."}, ...]
    """
    prompt = f"""Bạn là chuyên gia tư vấn đấu thầu xây dựng. Dựa trên bối cảnh dự án sau,
hãy đề xuất trọng số (tổng = 1.0) cho các tiêu chí đánh giá nhà cung cấp: {criteria_names}.

Bối cảnh dự án: {json.dumps(project_context, ensure_ascii=False)}

Chỉ trả về JSON thuần theo format:
[{{"criterion": "<tên tiêu chí>", "weight": <số 0-1>, "reasoning": "<lý do ngắn gọn>"}}]"""

    result = _call_claude_json(prompt)
    if result is not None:
        return result

    # Fallback khi chưa có API key: chia đều trọng số, đánh dấu rõ đây là fallback
    n = len(criteria_names)
    return [
        {"criterion": name, "weight": round(1 / n, 3),
         "reasoning": "[FALLBACK - chưa có ANTHROPIC_API_KEY] Chia đều do thiếu LLM."}
        for name in criteria_names
    ]


# ---------------------------------------------------------------------------
# 2. Chấm điểm uy tín từ văn bản tự do
# ---------------------------------------------------------------------------
def score_reputation_from_text(supplier_name: str, documents_text: list[str]) -> dict:
    """
    documents_text: danh sách đoạn văn bản (ghi chú sự cố, review, mô tả công ty...)
    Trả về: {"score": 0-100, "reasoning": "..."}
    """
    combined_text = "\n---\n".join(documents_text) if documents_text else "(Không có tài liệu nào)"
    prompt = f"""Đánh giá uy tín của nhà cung cấp "{supplier_name}" dựa trên các tài liệu sau,
thang điểm 0-100 (100 = rất uy tín):

{combined_text}

Chỉ trả về JSON thuần: {{"score": <số 0-100>, "reasoning": "<giải thích ngắn gọn>"}}"""

    result = _call_claude_json(prompt)
    if result is not None:
        return result

    return {
        "score": 50,
        "reasoning": "[FALLBACK - chưa có ANTHROPIC_API_KEY] Điểm trung tính do thiếu LLM.",
    }


# ---------------------------------------------------------------------------
# 3. Viết giải thích tổng hợp cuối cùng
# ---------------------------------------------------------------------------
def generate_final_explanation(project_name: str, ranking: list[dict]) -> str:
    """
    ranking: [{"supplier_name": ..., "total_score": ..., "criterion_breakdown": [...]}, ...]
    đã được sắp xếp từ cao xuống thấp.
    """
    prompt = f"""Dự án: {project_name}

Kết quả xếp hạng nhà cung cấp (đã tính điểm theo từng tiêu chí):
{json.dumps(ranking, ensure_ascii=False, indent=2)}

Hãy viết 1 đoạn giải thích ngắn gọn (4-6 câu), bằng tiếng Việt, cho người ra quyết định:
vì sao NCC đứng đầu được chọn, có đánh đổi (trade-off) nào đáng lưu ý so với các NCC khác không.
Chỉ trả về đoạn văn bản, không cần JSON."""

    client = _get_client()
    if client is None:
        top = ranking[0]
        return (
            f"[FALLBACK - chưa có ANTHROPIC_API_KEY] NCC được đề xuất: {top['supplier_name']} "
            f"với tổng điểm {top['total_score']:.1f}. Hãy set biến môi trường ANTHROPIC_API_KEY "
            f"để có giải thích chi tiết từ Claude."
        )

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
