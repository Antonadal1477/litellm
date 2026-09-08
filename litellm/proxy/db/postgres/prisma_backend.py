"""
Prisma Backend Adapter for PostgreSQL
Adapts existing Prisma Client to the unified BaseDatabaseBackend interface.
"""

import sys
from typing import Any, Dict, List, Optional, Union
from litellm.proxy.db.base import (
    BaseDatabaseBackend,
    BaseModelHandle,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseNotFoundError,
    DatabaseIntegrityError,
)

class PrismaModelHandle(BaseModelHandle):
    def __init__(self, prisma_model_client: Any):
        self._model = prisma_model_client

    async def find_unique(self, where: Dict[str, Any], include: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        try:
            kwargs = {"where": where}
            if include:
                kwargs["include"] = include
            return await self._model.find_unique(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def find_first(
        self,
        where: Optional[Dict[str, Any]] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        try:
            kwargs = {}
            if where is not None:
                kwargs["where"] = where
            if order is not None:
                kwargs["order"] = order
            if include is not None:
                kwargs["include"] = include
            return await self._model.find_first(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def find_many(
        self,
        where: Optional[Dict[str, Any]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        try:
            kwargs = {}
            if where is not None:
                kwargs["where"] = where
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            if order is not None:
                kwargs["order"] = order
            if include is not None:
                kwargs["include"] = include
            return await self._model.find_many(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def create(self, data: Dict[str, Any], include: Optional[Dict[str, Any]] = None) -> Any:
        try:
            kwargs = {"data": data}
            if include is not None:
                kwargs["include"] = include
            return await self._model.create(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def create_many(self, data: List[Dict[str, Any]], skip_duplicates: Optional[bool] = None) -> int:
        try:
            kwargs = {"data": data}
            if skip_duplicates is not None:
                kwargs["skip_duplicates"] = skip_duplicates
            return await self._model.create_many(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def update(
        self,
        where: Dict[str, Any],
        data: Dict[str, Any],
        include: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        try:
            kwargs = {"where": where, "data": data}
            if include is not None:
                kwargs["include"] = include
            return await self._model.update(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def update_many(self, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        try:
            return await self._model.update_many(where=where, data=data)
        except Exception as e:
            raise self._map_exception(e)

    async def delete(self, where: Dict[str, Any]) -> Optional[Any]:
        try:
            return await self._model.delete(where=where)
        except Exception as e:
            raise self._map_exception(e)

    async def delete_many(self, where: Optional[Dict[str, Any]] = None) -> int:
        try:
            kwargs = {}
            if where is not None:
                kwargs["where"] = where
            return await self._model.delete_many(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def upsert(
        self,
        where: Dict[str, Any],
        data: Dict[str, Any],
        include: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            kwargs = {"where": where, "data": data}
            if include is not None:
                kwargs["include"] = include
            return await self._model.upsert(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        try:
            kwargs = {}
            if where is not None:
                kwargs["where"] = where
            return await self._model.count(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    async def group_by(
        self,
        by: List[str],
        where: Optional[Dict[str, Any]] = None,
        sum: Optional[Dict[str, bool]] = None,
        count: Optional[Dict[str, bool]] = None,
        avg: Optional[Dict[str, bool]] = None,
        min: Optional[Dict[str, bool]] = None,
        max: Optional[Dict[str, bool]] = None,
        having: Optional[Dict[str, Any]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    ) -> List[Dict[str, Any]]:
        try:
            kwargs = {"by": by}
            if where is not None:
                kwargs["where"] = where
            if sum is not None:
                kwargs["sum"] = sum
            if count is not None:
                kwargs["count"] = count
            if avg is not None:
                kwargs["avg"] = avg
            if min is not None:
                kwargs["min"] = min
            if max is not None:
                kwargs["max"] = max
            if having is not None:
                kwargs["having"] = having
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            if order is not None:
                kwargs["order"] = order
            return await self._model.group_by(**kwargs)
        except Exception as e:
            raise self._map_exception(e)

    def _map_exception(self, e: Exception) -> Exception:
        exc_type = type(e).__name__
        if "UniqueConstraintViolation" in exc_type or "ForeignKeyConstraintViolation" in exc_type:
            return DatabaseIntegrityError(str(e))
        if "RecordNotFound" in exc_type:
            return DatabaseNotFoundError(str(e))
        if "PrismaError" in exc_type:
            return DatabaseError(str(e))
        return e


class PrismaDatabaseBackend(BaseDatabaseBackend):
    def __init__(self, prisma_client: Any):
        self.prisma_client = prisma_client
        self._handles: Dict[str, PrismaModelHandle] = {}

    async def connect(self) -> None:
        if self.prisma_client and not getattr(self.prisma_client, "is_connected", lambda: False)():
            await self.prisma_client.connect()

    async def disconnect(self) -> None:
        if self.prisma_client and getattr(self.prisma_client, "is_connected", lambda: False)():
            await self.prisma_client.disconnect()

    async def health_check(self) -> Dict[str, Any]:
        is_connected = False
        if self.prisma_client:
            is_connected = getattr(self.prisma_client, "is_connected", lambda: False)()
            if not is_connected and hasattr(self.prisma_client, "execute_raw"):
                try:
                    await self.prisma_client.execute_raw("SELECT 1;")
                    is_connected = True
                except Exception:
                    is_connected = False
        return {
            "database_type": "postgresql",
            "connected": is_connected,
            "version": "PostgreSQL",
        }

    def transaction(self) -> Any:
        if hasattr(self.prisma_client, "tx"):
            return self.prisma_client.tx()
        class DummyTx:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        return DummyTx()

    def get_model_handle(self, table_name: str) -> BaseModelHandle:
        clean_name = table_name.lower()
        if clean_name not in self._handles:
            model_attr = getattr(self.prisma_client, clean_name, None)
            if model_attr is None:
                db_obj = getattr(self.prisma_client, "db", self.prisma_client)
                model_attr = getattr(db_obj, clean_name, None)
            if model_attr is None:
                raise AttributeError(f"Prisma client has no model '{table_name}'")
            self._handles[clean_name] = PrismaModelHandle(model_attr)
        return self._handles[clean_name]

    def __getattr__(self, name: str) -> BaseModelHandle:
        try:
            return self.get_model_handle(name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute or model '{name}'")
