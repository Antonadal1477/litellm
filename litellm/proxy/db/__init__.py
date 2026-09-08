"""
Database Abstraction Entry Point for LiteLLM
Dispatches between PostgreSQL (Prisma) and Dameng DB8 (SQLAlchemy/dmPython) based on configuration.
"""

import os
from typing import Any, Optional
from litellm.proxy.db.base import BaseDatabaseBackend


_db_instance: Optional[BaseDatabaseBackend] = None


def get_db_type() -> str:
    """
    Returns the configured database type: 'postgresql' or 'dameng'.
    """
    db_type = os.getenv("DATABASE_TYPE") or os.getenv("DB_TYPE") or "postgresql"
    return db_type.lower().strip()


def create_db_backend(
    db_type: Optional[str] = None,
    prisma_client: Optional[Any] = None,
    **kwargs
) -> BaseDatabaseBackend:
    """
    Factory function to initialize and return a BaseDatabaseBackend instance.
    """
    if db_type is None:
        db_type = get_db_type()

    if db_type == "dameng":
        from litellm.proxy.db.dameng.backend import DamengDatabaseBackend
        return DamengDatabaseBackend(**kwargs)
    else:
        from litellm.proxy.db.postgres.prisma_backend import PrismaDatabaseBackend
        return PrismaDatabaseBackend(prisma_client=prisma_client)


def set_global_db_instance(backend: BaseDatabaseBackend) -> None:
    global _db_instance
    _db_instance = backend


def get_global_db_instance() -> Optional[BaseDatabaseBackend]:
    return _db_instance
