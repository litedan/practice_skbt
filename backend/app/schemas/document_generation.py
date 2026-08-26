from typing import Any

from pydantic import Field

from app.schemas.common import ORMModel


class GenerateRequestDocumentPayload(ORMModel):
    template_code: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    context: dict[str, Any] = Field(
        default_factory=dict,
    )


class GeneratedRequestDocumentResponse(ORMModel):
    id: int
    name: str
    request_id: int
    file_path: str