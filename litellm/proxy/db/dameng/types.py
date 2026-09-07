"""
Custom SQLAlchemy TypeDecorators for Dameng DM8 compatibility.
Handles JSON and Array auto-serialization to CLOB/TEXT.
"""

import json
from typing import Any, List, Optional
from sqlalchemy.types import TypeDecorator, Text, VARCHAR, CLOB

class JSONType(TypeDecorator):
    """
    TypeDecorator that transparently serializes Python dicts/lists to JSON strings
    for database storage and deserializes them back to Python objects.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Optional[Any], dialect: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value: Optional[Any], dialect: Any) -> Optional[Any]:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except Exception:
            return value


class ArrayType(TypeDecorator):
    """
    TypeDecorator that transparently serializes Python lists to JSON strings
    for database storage and deserializes them back to Python lists.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Optional[Any], dialect: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (list, tuple, set)):
            return json.dumps(list(value), ensure_ascii=False)
        return json.dumps([value], ensure_ascii=False)

    def process_result_value(self, value: Optional[Any], dialect: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        try:
            res = json.loads(value)
            return res if isinstance(res, list) else [res]
        except Exception:
            return []
