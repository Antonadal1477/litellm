"""
Dameng DM8 Database Backend
Integrates SessionManager, SQLAlchemy Models, Migrations, and Repositories.
"""

import os
from typing import Any, Dict, Optional
from litellm.proxy.db.base import BaseDatabaseBackend, BaseModelHandle
from litellm.proxy.db.dameng.session import DamengSessionManager
from litellm.proxy.db.dameng import models
from litellm.proxy.db.dameng.repository import DamengModelHandle


class DamengDatabaseBackend(BaseDatabaseBackend):
    def __init__(
        self,
        connection_url: Optional[str] = None,
        pool_size: int = 20,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        max_workers: int = 20,
    ):
        self.session_manager = DamengSessionManager(
            connection_url=connection_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            max_workers=max_workers,
        )
        self._handles: Dict[str, DamengModelHandle] = {}

    async def connect(self) -> None:
        self.session_manager.initialize()
        await self._run_migrations_if_needed()

    async def _run_migrations_if_needed(self) -> None:
        def _migrate():
            # For SQLite / testing fallback, create tables directly using ORM metadata
            models.Base.metadata.create_all(bind=self.session_manager.engine)

        await self.session_manager.run_in_db_thread(_migrate)

    async def disconnect(self) -> None:
        self.session_manager.close()

    async def health_check(self) -> Dict[str, Any]:
        def _check():
            with self.session_manager.get_session() as session:
                session.execute(models.select(1))
            return True

        try:
            connected = await self.session_manager.run_in_db_thread(_check)
            return {
                "database_type": "dameng",
                "connected": connected,
                "schema": os.getenv("DATABASE_SCHEMA", "LITELLM"),
                "version": "DM8",
            }
        except Exception as e:
            return {
                "database_type": "dameng",
                "connected": False,
                "error": str(e),
            }

    def transaction(self) -> Any:
        class DamengTx:
            def __init__(self, session_manager: DamengSessionManager):
                self.session_manager = session_manager
                self.session = None

            async def __aenter__(self):
                self.session = self.session_manager.get_session()
                return self.session

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.session:
                    if exc_type:
                        self.session.rollback()
                    else:
                        self.session.commit()
                    self.session.close()

        return DamengTx(self.session_manager)

    def get_model_handle(self, table_name: str) -> BaseModelHandle:
        clean_name = table_name.lower()
        if clean_name not in self._handles:
            # Map clean name to ORM model class
            model_cls = None
            for name, obj in models.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, models.Base) and obj is not models.Base:
                    if name.lower() == clean_name or getattr(obj, "__tablename__", "").lower() == clean_name:
                        model_cls = obj
                        break

            if model_cls is None:
                raise AttributeError(f"Dameng DB model '{table_name}' not found")

            self._handles[clean_name] = DamengModelHandle(model_cls, self.session_manager)
        return self._handles[clean_name]

    def __getattr__(self, name: str) -> BaseModelHandle:
        try:
            return self.get_model_handle(name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute or model '{name}'")
