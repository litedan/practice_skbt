"""Файлы/сканы, прикреплённые к заявкам."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class DocumentFile(MainBase):
    __tablename__ = "document_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"))

    request: Mapped["Request"] = relationship(back_populates="document_files")
