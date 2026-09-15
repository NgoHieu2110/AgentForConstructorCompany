"""
db/database.py
===============
Nơi duy nhất tạo "engine" (kết nối tới file database) và Session.
Mọi file khác cần dùng database đều import từ đây, KHÔNG tự tạo engine riêng -
tránh tình trạng mỗi file mở 1 kết nối khác nhau tới cùng 1 file .db.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()
from db.models import Base

DATABASE_URL = "sqlite:///supplier_selection.db"

engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Trả về 1 session mới. FastAPI sẽ gọi hàm này cho mỗi request."""
    return SessionLocal()
