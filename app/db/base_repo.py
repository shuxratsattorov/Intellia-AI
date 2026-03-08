from __future__ import annotations
from abc import ABC
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from typing import Any, Generic, Sequence, TypeVar
from sqlalchemy import Select, delete, exists, func, select, update

from app.db.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    model: type[ModelType]

    def __init__(self, session: Session | AsyncSession = None) -> None:
        self.session: Session | AsyncSession = session

    def query(self) -> Select[tuple[ModelType]]:
        return select(self.model)

    # @abstractmethod
    # def get(self):
    #     pass

    # @abstractmethod
    # def get_many(self):
    #     pass

    # @abstractmethod
    # def exists(self):
    #     pass

    # @abstractmethod
    # def update(self):
    #     pass

    # @abstractmethod
    # def create(self):
    #     pass

    # @abstractmethod
    # def delete(self):
    #     pass     


class AsyncRepository(BaseRepository[ModelType], Generic[ModelType]):
    def _apply_filters(
        self,
        stmt: Select[tuple[ModelType]],
        filters: Sequence[ColumnElement[bool]] | None = None,
    ) -> Select[tuple[ModelType]]:
        if filters:
            stmt = stmt.where(*filters)
        return stmt

    def _apply_ordering(
        self,
        stmt: Select[tuple[ModelType]],
        order_by: Sequence[InstrumentedAttribute[Any]] | None = None,
    ) -> Select[tuple[ModelType]]:
        if order_by:
            stmt = stmt.order_by(*order_by)
        return stmt

    def _apply_pagination(
        self,
        stmt: Select[tuple[ModelType]],
        limit: int | None = None,
        offset: int | None = None,
    ) -> Select[tuple[ModelType]]:
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return stmt

    async def get_by_id(self, obj_id: Any) -> ModelType | None:
        return await self.session.get(self.model, obj_id)

    async def get_or_404(self, obj_id: Any) -> ModelType:
        obj = await self.get_by_id(obj_id)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} with id={obj_id} not found")
        return obj

    async def get_one_by(self, **filters: Any) -> ModelType | None:
        stmt = self.query().filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        *,
        filters: Sequence[ColumnElement[bool]] | None = None,
        order_by: Sequence[InstrumentedAttribute[Any]] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ModelType]:
        stmt = self.query()
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, order_by)
        stmt = self._apply_pagination(stmt, limit, offset)

        result = await self.session.execute(stmt)
        return list[ModelType](result.scalars().all())

    async def first(
        self,
        *,
        filters: Sequence[ColumnElement[bool]] | None = None,
        order_by: Sequence[InstrumentedAttribute[Any]] | None = None,
    ) -> ModelType | None:
        rows = await self.get_many(filters=filters, order_by=order_by, limit=1)
        return rows[0] if rows else None

    async def exists(self, **filters: Any) -> bool:
        conditions = [getattr(self.model, key) == value for key, value in filters.items()]
        stmt = select(exists().where(*conditions))
        result = await self.session.execute(stmt)
        return bool(result.scalar())

    async def count(
        self,
        *,
        filters: Sequence[ColumnElement[bool]] | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        if filters:
            stmt = stmt.where(*filters)

        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def create(
        self,
        data: dict[str, Any],
        *,
        flush: bool = True,
        refresh: bool = False,
    ) -> ModelType:
        obj = self.model(**data)
        self.session.add(obj)

        if flush:
            await self.session.flush()

        if refresh:
            await self.session.refresh(obj)

        return obj

    async def create_many(
        self,
        data_list: list[dict[str, Any]],
        *,
        flush: bool = True,
    ) -> list[ModelType]:
        objs = [self.model(**data) for data in data_list]
        self.session.add_all(objs)

        if flush:
            await self.session.flush()

        return objs

    async def update(
        self,
        obj: ModelType,
        data: dict[str, Any],
        *,
        flush: bool = True,
        refresh: bool = False,
    ) -> ModelType:
        for field, value in data.items():
            setattr(obj, field, value)

        self.session.add(obj)

        if flush:
            await self.session.flush()

        if refresh:
            await self.session.refresh(obj)

        return obj

    async def update_by_id(
        self,
        obj_id: Any,
        data: dict[str, Any],
        *,
        flush: bool = True,
        refresh: bool = False,
    ) -> ModelType:
        obj = await self.get_or_404(obj_id)
        return await self.update(obj, data, flush=flush, refresh=refresh)

    async def patch_by_filters(
        self,
        filters: Sequence[ColumnElement[bool]],
        data: dict[str, Any],
        *,
        synchronize_session: str = "fetch",
    ) -> int:
        stmt = (
            update(self.model)
            .where(*filters)
            .values(**data)
            .execution_options(synchronize_session=synchronize_session)
        )
        result = await self.session.execute(stmt)
        return int(result.rowcount or 0)

    async def delete(self, obj: ModelType, *, flush: bool = True) -> None:
        await self.session.delete(obj)

        if flush:
            await self.session.flush()

    async def delete_by_id(self, obj_id: Any, *, flush: bool = True) -> None:
        obj = await self.get_or_404(obj_id)
        await self.delete(obj, flush=flush)

    async def delete_by_filters(
        self,
        filters: Sequence[ColumnElement[bool]],
    ) -> int:
        stmt = delete(self.model).where(*filters)
        result = await self.session.execute(stmt)
        return int(result.rowcount or 0)