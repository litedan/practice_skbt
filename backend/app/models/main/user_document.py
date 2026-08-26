"""Документы сотрудников."""

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import MainBase


class UserDocument(MainBase):
    __tablename__ = "user_documents"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "document_type",
            "version",
            name="user_documents_employee_id_document_type_version_key",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    template_id: Mapped[int] = mapped_column(
        ForeignKey("templates.id", ondelete="RESTRICT"),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    file_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_path_docx: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_path_pdf: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="draft",
    )

    context_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    signed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    signed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    generated_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    generated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )