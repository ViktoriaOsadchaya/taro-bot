import re
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        # Единообразно строим snake_case имена таблиц и множественное число в одном месте.
        table_name = re.sub(r"(?<!^)(?=[A-Z])", "_", self.__name__).lower()
        if table_name.endswith("analysis"):
            return f"{table_name[:-2]}es"
        if table_name.endswith("y"):
            return f"{table_name[:-1]}ies"
        return f"{table_name}s"

    primary_key: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        sort_order=-10,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
