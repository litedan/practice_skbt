"""Справочники: отделы, должности, типы заявок, статусы."""

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, MainDB
from app.models.main.department import Department
from app.models.main.position import Position
from app.models.main.request_type import RequestType
from app.models.main.status import Status
from app.schemas.dictionary import DictionaryItem, RequestTypeItem

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
