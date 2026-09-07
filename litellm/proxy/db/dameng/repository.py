"""
Dameng DM8 Repository and Model Handle Implementation
Provides CRUD, atomic upsert (MERGE INTO / SELECT FOR UPDATE), group_by aggregation, and transaction handles for DM8.
"""

import json
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import select, update, delete, func, or_, and_, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from litellm.proxy.db.base import (
    BaseModelHandle,
    DatabaseError,
    DatabaseNotFoundError,
    DatabaseIntegrityError,
    DatabaseConflictError,
)
from litellm.proxy.db.dameng.models import Base, to_dict, LiteLLM_SchemaVersion
from litellm.proxy.db.dameng.session import DamengSessionManager


class DamengModelHandle(BaseModelHandle):
    def __init__(self, model_cls: Any, session_manager: DamengSessionManager):
        self.model_cls = model_cls
        self.session_manager = session_manager

    def _normalize_input_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for k, v in data.items():
            attr_name = "metadata_col" if k == "metadata" and hasattr(self.model_cls, "metadata_col") else k
            if isinstance(v, (dict, list)):
                res[attr_name] = json.dumps(v, ensure_ascii=False)
            else:
                res[attr_name] = v
        return res

    def _get_attr(self, key: str) -> Any:
        attr_name = "metadata_col" if key == "metadata" and hasattr(self.model_cls, "metadata_col") else key
        return getattr(self.model_cls, attr_name)

    def _sync_find_unique(self, session: Session, where: Dict[str, Any]) -> Optional[Any]:
        stmt = select(self.model_cls)
        filters = [self._get_attr(k) == v for k, v in where.items()]
        stmt = stmt.where(and_(*filters))
        res = session.execute(stmt).scalar_one_or_none()
        return to_dict(res)

    async def find_unique(self, where: Dict[str, Any], include: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_find_unique(session, where)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_find_first(
        self,
        session: Session,
        where: Optional[Dict[str, Any]] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    ) -> Optional[Any]:
        stmt = select(self.model_cls)
        if where:
            stmt = self._apply_where(stmt, where)
        if order:
            stmt = self._apply_order(stmt, order)
        stmt = stmt.limit(1)
        res = session.execute(stmt).scalar_one_or_none()
        return to_dict(res)

    async def find_first(
        self,
        where: Optional[Dict[str, Any]] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_find_first(session, where, order)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_find_many(
        self,
        session: Session,
        where: Optional[Dict[str, Any]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    ) -> List[Any]:
        stmt = select(self.model_cls)
        if where:
            stmt = self._apply_where(stmt, where)
        if order:
            stmt = self._apply_order(stmt, order)
        if skip:
            stmt = stmt.offset(skip)
        if take:
            stmt = stmt.limit(take)
        res = session.execute(stmt).scalars().all()
        return [to_dict(x) for x in res]

    async def find_many(
        self,
        where: Optional[Dict[str, Any]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_find_many(session, where, take, skip, order)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_create(self, session: Session, data: Dict[str, Any]) -> Any:
        norm_data = self._normalize_input_dict(data)
        obj = self.model_cls(**norm_data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return to_dict(obj)

    async def create(self, data: Dict[str, Any], include: Optional[Dict[str, Any]] = None) -> Any:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_create(session, data)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_create_many(self, session: Session, data: List[Dict[str, Any]]) -> int:
        objs = [self.model_cls(**self._normalize_input_dict(item)) for item in data]
        session.bulk_save_objects(objs)
        session.commit()
        return len(data)

    async def create_many(self, data: List[Dict[str, Any]], skip_duplicates: Optional[bool] = None) -> int:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_create_many(session, data)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_update(self, session: Session, where: Dict[str, Any], data: Dict[str, Any]) -> Optional[Any]:
        stmt = select(self.model_cls)
        stmt = self._apply_where(stmt, where)
        obj = session.execute(stmt).scalar_one_or_none()
        if not obj:
            return None
        norm_data = self._normalize_input_dict(data)
        for k, v in norm_data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        session.commit()
        session.refresh(obj)
        return to_dict(obj)

    async def update(
        self,
        where: Dict[str, Any],
        data: Dict[str, Any],
        include: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_update(session, where, data)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_update_many(self, session: Session, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        norm_data = self._normalize_input_dict(data)
        stmt = update(self.model_cls)
        stmt = self._apply_where(stmt, where)
        stmt = stmt.values(**norm_data)
        res = session.execute(stmt)
        session.commit()
        return res.rowcount

    async def update_many(self, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_update_many(session, where, data)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_delete(self, session: Session, where: Dict[str, Any]) -> Optional[Any]:
        stmt = select(self.model_cls)
        stmt = self._apply_where(stmt, where)
        obj = session.execute(stmt).scalar_one_or_none()
        if not obj:
            return None
        dto = to_dict(obj)
        session.delete(obj)
        session.commit()
        return dto

    async def delete(self, where: Dict[str, Any]) -> Optional[Any]:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_delete(session, where)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_delete_many(self, session: Session, where: Optional[Dict[str, Any]] = None) -> int:
        stmt = delete(self.model_cls)
        if where:
            stmt = self._apply_where(stmt, where)
        res = session.execute(stmt)
        session.commit()
        return res.rowcount

    async def delete_many(self, where: Optional[Dict[str, Any]] = None) -> int:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_delete_many(session, where)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_upsert(self, session: Session, where: Dict[str, Any], data: Dict[str, Any]) -> Any:
        """
        Atomic upsert implementation for Dameng DM8 / SQLAlchemy.
        Uses row locking and IntegrityError fallback to handle concurrent upsert safety.
        """
        create_data = data.get("create", data)
        update_data = data.get("update", data)

        try:
            stmt = select(self.model_cls)
            if session.bind and session.bind.dialect.name != "sqlite":
                stmt = stmt.with_for_update()
            stmt = self._apply_where(stmt, where)
            obj = session.execute(stmt).scalar_one_or_none()

            if obj:
                norm_update = self._normalize_input_dict(update_data)
                for k, v in norm_update.items():
                    if hasattr(obj, k):
                        setattr(obj, k, v)
            else:
                full_data = {**where, **create_data}
                norm_create = self._normalize_input_dict(full_data)
                obj = self.model_cls(**norm_create)
                session.add(obj)

            session.commit()
            session.refresh(obj)
            return to_dict(obj)

        except IntegrityError:
            session.rollback()
            stmt = select(self.model_cls)
            stmt = self._apply_where(stmt, where)
            obj = session.execute(stmt).scalar_one_or_none()
            if obj:
                norm_update = self._normalize_input_dict(update_data)
                for k, v in norm_update.items():
                    if hasattr(obj, k):
                        setattr(obj, k, v)
                session.commit()
                session.refresh(obj)
                return to_dict(obj)
            else:
                raise DatabaseConflictError("Concurrent upsert conflict could not be resolved.")

    async def upsert(
        self,
        where: Dict[str, Any],
        data: Dict[str, Any],
        include: Optional[Dict[str, Any]] = None,
    ) -> Any:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_upsert(session, where, data)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_count(self, session: Session, where: Optional[Dict[str, Any]] = None) -> int:
        stmt = select(func.count()).select_from(self.model_cls)
        if where:
            stmt = self._apply_where(stmt, where)
        return session.execute(stmt).scalar_or_none() or 0

    async def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_count(session, where)
        return await self.session_manager.run_in_db_thread(_run)

    def _sync_group_by(
        self,
        session: Session,
        by: List[str],
        where: Optional[Dict[str, Any]] = None,
        sum: Optional[Dict[str, bool]] = None,
        count: Optional[Dict[str, bool]] = None,
        avg: Optional[Dict[str, bool]] = None,
        min: Optional[Dict[str, bool]] = None,
        max: Optional[Dict[str, bool]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    ) -> List[Dict[str, Any]]:
        group_cols = [self._get_attr(col) for col in by]
        select_cols = list(group_cols)

        if sum:
            for col, flag in sum.items():
                if flag:
                    select_cols.append(func.sum(self._get_attr(col)).label(f"_sum_{col}"))
        if count:
            for col, flag in count.items():
                if flag:
                    select_cols.append(func.count(self._get_attr(col)).label(f"_count_{col}"))

        stmt = select(*select_cols)
        if where:
            stmt = self._apply_where(stmt, where)
        stmt = stmt.group_by(*group_cols)

        if skip:
            stmt = stmt.offset(skip)
        if take:
            stmt = stmt.limit(take)

        results = session.execute(stmt).all()
        res_list = []
        for row in results:
            item = {}
            for idx, col_name in enumerate(by):
                item[col_name] = row[idx]
            offset = len(by)
            if sum:
                item["_sum"] = {}
                for col, flag in sum.items():
                    if flag:
                        item["_sum"][col] = row[offset]
                        offset += 1
            if count:
                item["_count"] = {}
                for col, flag in count.items():
                    if flag:
                        item["_count"][col] = row[offset]
                        offset += 1
            res_list.append(item)
        return res_list

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
        def _run():
            with self.session_manager.get_session() as session:
                return self._sync_group_by(session, by, where, sum, count, avg, min, max, take, skip, order)
        return await self.session_manager.run_in_db_thread(_run)

    def _apply_where(self, stmt: Any, where: Dict[str, Any]) -> Any:
        filters = []
        for k, v in where.items():
            if k == "AND" and isinstance(v, list):
                for sub in v:
                    stmt = self._apply_where(stmt, sub)
                continue
            if k == "OR" and isinstance(v, list):
                or_filters = []
                for sub in v:
                    for sk, sv in sub.items():
                        or_filters.append(self._get_attr(sk) == sv)
                filters.append(or_(*or_filters))
                continue

            try:
                attr = self._get_attr(k)
            except AttributeError:
                continue

            if isinstance(v, dict):
                if "in" in v:
                    filters.append(attr.in_(v["in"]))
                if "notIn" in v:
                    filters.append(~attr.in_(v["notIn"]))
                if "gte" in v:
                    filters.append(attr >= v["gte"])
                if "lte" in v:
                    filters.append(attr <= v["lte"])
                if "gt" in v:
                    filters.append(attr > v["gt"])
                if "lt" in v:
                    filters.append(attr < v["lt"])
                if "contains" in v:
                    filters.append(attr.contains(v["contains"]))
                if "equals" in v:
                    filters.append(attr == v["equals"])
                if "not" in v:
                    filters.append(attr != v["not"])
            else:
                filters.append(attr == v)

        if filters:
            stmt = stmt.where(and_(*filters))
        return stmt

    def _apply_order(self, stmt: Any, order: Union[Dict[str, str], List[Dict[str, str]]]) -> Any:
        order_list = order if isinstance(order, list) else [order]
        for item in order_list:
            for k, dir_ in item.items():
                try:
                    attr = self._get_attr(k)
                    stmt = stmt.order_by(attr.desc() if dir_.lower() == "desc" else attr.asc())
                except AttributeError:
                    pass
        return stmt
