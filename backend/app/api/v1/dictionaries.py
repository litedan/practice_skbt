"""Справочники: отделы, должности, типы заявок, статусы."""

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, MainDB
from app.core.template_fields import get_template_fields
from app.models.main.department import Department
from app.models.main.position import Position
from app.models.main.request_type import RequestType
from app.models.main.status import Status
from app.models.main.template import Template
from app.schemas.dictionary import DictionaryItem, RequestTypeItem, TemplateItem

router = APIRouter(prefix="/dictionaries", tags=["Dictionaries"])


@router.get("/departments", response_model=list[DictionaryItem])
async def get_departments(_: CurrentUser, db: MainDB) -> list[DictionaryItem]:
    result = await db.execute(select(Department).order_by(Department.name))
    return [DictionaryItem.model_validate(item) for item in result.scalars()]


@router.get("/positions", response_model=list[DictionaryItem])
async def get_positions(_: CurrentUser, db: MainDB) -> list[DictionaryItem]:
    result = await db.execute(select(Position).order_by(Position.name))
    return [DictionaryItem.model_validate(item) for item in result.scalars()]


@router.get("/request-types", response_model=list[RequestTypeItem])
async def get_request_types(_: CurrentUser, db: MainDB) -> list[RequestTypeItem]:
    result = await db.execute(select(RequestType).order_by(RequestType.name))
    return [RequestTypeItem.model_validate(item) for item in result.scalars()]


@router.get("/statuses", response_model=list[DictionaryItem])
async def get_statuses(_: CurrentUser, db: MainDB) -> list[DictionaryItem]:
    result = await db.execute(select(Status).order_by(Status.name))
    return [DictionaryItem.model_validate(item) for item in result.scalars()]


@router.get("/templates", response_model=list[TemplateItem])
async def get_templates(_: CurrentUser, db: MainDB) -> list[TemplateItem]:
    """Активные шаблоны документов, доступные при создании заявки."""
    result = await db.execute(
        select(Template).where(Template.is_active.is_(True)).order_by(Template.name)
    )
    return [
        TemplateItem(
            id=item.id,
            name=item.name,
            code=item.code,
            fields=[field.__dict__ for field in get_template_fields(item.code)],
        )
        for item in result.scalars()
    ]
