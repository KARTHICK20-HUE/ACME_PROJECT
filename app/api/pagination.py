from typing import Any

from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typing_extensions import Annotated

PageParam = Annotated[int, Query(ge=1)]
PageSizeParam = Annotated[int, Query(ge=1, le=100)]


def paginate(db: Session, stmt, page: int, page_size: int) -> dict[str, Any]:
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0
    max_pages = (total + page_size - 1) // page_size if total else 0
    if page > max_pages:
        return {"items": [], "total": total, "page": page, "page_size": page_size}

    items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": list(items), "total": total, "page": page, "page_size": page_size}
