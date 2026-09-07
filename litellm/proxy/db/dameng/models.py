"""
SQLAlchemy ORM Models for Dameng DM8 Database
Generated from schema.prisma for full compatibility.
"""

import datetime
from typing import Any, Dict
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Float,
    Boolean,
    DateTime,
    Text,
    LargeBinary,
    Index,
    UniqueConstraint,
    PrimaryKeyConstraint,
    select,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LiteLLM_BudgetTable(Base):
    __tablename__ = "LiteLLM_BudgetTable"

    budget_id = Column(String(255), primary_key=True)
    max_budget = Column(Float, nullable=True)
    soft_budget = Column(Float, nullable=True)
    max_parallel_requests = Column(Integer, nullable=True)
    tpm_limit = Column(BigInteger, nullable=True)
    rpm_limit = Column(BigInteger, nullable=True)
    model_max_budget = Column(Text, nullable=True)
    budget_duration = Column(String(255), nullable=True)
    budget_reset_at = Column(DateTime, nullable=True)
    allowed_models = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_CredentialsTable(Base):
    __tablename__ = "LiteLLM_CredentialsTable"

    credential_id = Column(String(255), primary_key=True)
    credential_name = Column(String(255), unique=True, nullable=False)
    credential_values = Column(Text, nullable=False)
    credential_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_ProxyModelTable(Base):
    __tablename__ = "LiteLLM_ProxyModelTable"

    model_id = Column(String(255), primary_key=True)
    model_name = Column(String(255), nullable=False)
    litellm_params = Column(Text, nullable=False)
    model_info = Column(Text, nullable=True)
    blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_AgentsTable(Base):
    __tablename__ = "LiteLLM_AgentsTable"

    agent_id = Column(String(255), primary_key=True)
    agent_name = Column(String(255), unique=True, nullable=False)
    litellm_params = Column(Text, nullable=True)
    agent_card_params = Column(Text, nullable=False)
    static_headers = Column(Text, default="{}")
    extra_headers = Column(Text, default="[]")
    agent_access_groups = Column(Text, default="[]")
    object_permission_id = Column(String(255), nullable=True)
    spend = Column(Float, default=0.0)
    tpm_limit = Column(Integer, nullable=True)
    rpm_limit = Column(Integer, nullable=True)
    session_tpm_limit = Column(Integer, nullable=True)
    session_rpm_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_OrganizationTable(Base):
    __tablename__ = "LiteLLM_OrganizationTable"

    organization_id = Column(String(255), primary_key=True)
    organization_alias = Column(String(255), nullable=False)
    budget_id = Column(String(255), nullable=False)
    metadata_col = Column("metadata", Text, default="{}")
    models = Column(Text, default="[]")
    spend = Column(Float, default=0.0)
    model_spend = Column(Text, default="{}")
    object_permission_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_ModelTable(Base):
    __tablename__ = "LiteLLM_ModelTable"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_aliases = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_TeamTable(Base):
    __tablename__ = "LiteLLM_TeamTable"

    team_id = Column(String(255), primary_key=True)
    team_alias = Column(String(255), nullable=True, index=True)
    organization_id = Column(String(255), nullable=True, index=True)
    object_permission_id = Column(String(255), nullable=True)
    admins = Column(Text, default="[]")
    members = Column(Text, default="[]")
    members_with_roles = Column(Text, default="{}")
    metadata_col = Column("metadata", Text, default="{}")
    max_budget = Column(Float, nullable=True)
    soft_budget = Column(Float, nullable=True)
    spend = Column(Float, default=0.0)
    models = Column(Text, default="[]")
    max_parallel_requests = Column(Integer, nullable=True)
    tpm_limit = Column(BigInteger, nullable=True)
    rpm_limit = Column(BigInteger, nullable=True)
    budget_duration = Column(String(255), nullable=True)
    budget_reset_at = Column(DateTime, nullable=True)
    blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    model_spend = Column(Text, default="{}")
    model_max_budget = Column(Text, default="{}")
    router_settings = Column(Text, default="{}")
    team_member_permissions = Column(Text, default="[]")
    access_group_ids = Column(Text, default="[]")
    policies = Column(Text, default="[]")
    default_team_member_models = Column(Text, default="[]")
    budget_limits = Column(Text, nullable=True)
    model_id = Column(Integer, nullable=True, unique=True)
    allow_team_guardrail_config = Column(Boolean, default=False)


class LiteLLM_ProjectTable(Base):
    __tablename__ = "LiteLLM_ProjectTable"

    project_id = Column(String(255), primary_key=True)
    project_alias = Column(String(255), nullable=True)
    description = Column(String(1000), nullable=True)
    team_id = Column(String(255), nullable=True)
    budget_id = Column(String(255), nullable=True)
    metadata_col = Column("metadata", Text, default="{}")
    models = Column(Text, default="[]")
    spend = Column(Float, default=0.0)
    model_spend = Column(Text, default="{}")
    model_rpm_limit = Column(Text, default="{}")
    model_tpm_limit = Column(Text, default="{}")
    blocked = Column(Boolean, default=False)
    object_permission_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=False, default="")


class LiteLLM_UserTable(Base):
    __tablename__ = "LiteLLM_UserTable"

    user_id = Column(String(255), primary_key=True)
    user_alias = Column(String(255), nullable=True)
    team_id = Column(String(255), nullable=True)
    sso_user_id = Column(String(255), unique=True, nullable=True)
    organization_id = Column(String(255), nullable=True)
    object_permission_id = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    teams = Column(Text, default="[]")
    user_role = Column(String(255), nullable=True)
    max_budget = Column(Float, nullable=True)
    spend = Column(Float, default=0.0)
    user_email = Column(String(255), nullable=True)
    models = Column(Text, default="[]")
    metadata_col = Column("metadata", Text, default="{}")
    max_parallel_requests = Column(Integer, nullable=True)
    tpm_limit = Column(BigInteger, nullable=True)
    rpm_limit = Column(BigInteger, nullable=True)
    budget_duration = Column(String(255), nullable=True)
    budget_reset_at = Column(DateTime, nullable=True)
    allowed_cache_controls = Column(Text, default="[]")
    policies = Column(Text, default="[]")
    model_spend = Column(Text, default="{}")
    model_max_budget = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class LiteLLM_VerificationToken(Base):
    __tablename__ = "LiteLLM_VerificationToken"

    token = Column(String(255), primary_key=True)
    key_name = Column(String(255), nullable=True)
    key_alias = Column(String(255), nullable=True)
    soft_budget_cooldown = Column(Boolean, default=False)
    spend = Column(Float, default=0.0)
    expires = Column(DateTime, nullable=True)
    models = Column(Text, default="[]")
    aliases = Column(Text, default="{}")
    config = Column(Text, default="{}")
    router_settings = Column(Text, default="{}")
    user_id = Column(String(255), nullable=True)
    team_id = Column(String(255), nullable=True)
    agent_id = Column(String(255), nullable=True)
    project_id = Column(String(255), nullable=True)
    permissions = Column(Text, default="{}")
    max_parallel_requests = Column(Integer, nullable=True)
    metadata_col = Column("metadata", Text, default="{}")
    blocked = Column(Boolean, nullable=True)
    tpm_limit = Column(BigInteger, nullable=True)
    rpm_limit = Column(BigInteger, nullable=True)
    max_budget = Column(Float, nullable=True)
    budget_duration = Column(String(255), nullable=True)
    budget_reset_at = Column(DateTime, nullable=True)
    allowed_cache_controls = Column(Text, default="[]")
    allowed_routes = Column(Text, default="[]")
    policies = Column(Text, default="[]")
    access_group_ids = Column(Text, default="[]")
    model_spend = Column(Text, default="{}")
    model_max_budget = Column(Text, default="{}")
    budget_id = Column(String(255), nullable=True)
    organization_id = Column(String(255), nullable=True)
    object_permission_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(String(255), nullable=True)
    last_active = Column(DateTime, nullable=True)
    rotation_count = Column(Integer, default=0)
    auto_rotate = Column(Boolean, default=False)
    rotation_interval = Column(String(255), nullable=True)
    last_rotation_at = Column(DateTime, nullable=True)
    key_rotation_at = Column(DateTime, nullable=True)
    budget_limits = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_vt_user_team", "user_id", "team_id"),
        Index("idx_vt_team", "team_id"),
        Index("idx_vt_budget_expires", "budget_reset_at", "expires"),
    )


class LiteLLM_SpendLogs(Base):
    __tablename__ = "LiteLLM_SpendLogs"

    request_id = Column(String(255), primary_key=True)
    call_type = Column(String(255), nullable=False, default="")
    api_key = Column(String(255), nullable=False, default="")
    spend = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    startTime = Column(DateTime, nullable=False, index=True)
    endTime = Column(DateTime, nullable=False)
    request_duration_ms = Column(Integer, nullable=True)
    completionStartTime = Column(DateTime, nullable=True)
    model = Column(String(255), default="")
    model_id = Column(String(255), default="")
    model_group = Column(String(255), default="")
    custom_llm_provider = Column(String(255), default="")
    api_base = Column(String(255), default="")
    user = Column(String(255), default="")
    metadata_col = Column("metadata", Text, default="{}")
    cache_hit = Column(String(255), default="")
    cache_key = Column(String(255), default="")
    request_tags = Column(Text, default="[]")
    team_id = Column(String(255), nullable=True)
    organization_id = Column(String(255), nullable=True)
    end_user = Column(String(255), nullable=True, index=True)
    requester_ip_address = Column(String(255), nullable=True)
    messages = Column(Text, default="{}")
    response = Column(Text, default="{}")
    session_id = Column(String(255), nullable=True, index=True)
    status = Column(String(255), nullable=True)
    mcp_namespaced_tool_name = Column(String(255), nullable=True)
    agent_id = Column(String(255), nullable=True)
    proxy_server_request = Column(Text, default="{}")

    __table_args__ = (
        Index("idx_sl_starttime_reqid", "startTime", "request_id"),
    )


class LiteLLM_Config(Base):
    __tablename__ = "LiteLLM_Config"

    param_name = Column(String(255), primary_key=True)
    param_value = Column(Text, nullable=True)


class LiteLLM_AuditLog(Base):
    __tablename__ = "LiteLLM_AuditLog"

    id = Column(String(255), primary_key=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    changed_by = Column(String(255), default="")
    changed_by_api_key = Column(String(255), default="")
    action = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    object_id = Column(String(255), nullable=False)
    before_value = Column(Text, nullable=True)
    updated_values = Column(Text, nullable=True)


class LiteLLM_SchemaVersion(Base):
    __tablename__ = "LITELLM_SCHEMA_VERSION"

    version = Column(Integer, primary_key=True)
    migration_name = Column(String(255), nullable=False)
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)


def to_dict(model_obj: Any) -> Dict[str, Any]:
    """Utility function to convert SQLAlchemy ORM instance to a clean Python dict DTO."""
    import json
    if model_obj is None:
        return None
    res = {}
    for col in model_obj.__table__.columns:
        col_name = col.name
        val = getattr(model_obj, col.name if col_name != "metadata" else "metadata_col")
        if isinstance(val, str) and (val.startswith("{") or val.startswith("[")):
            try:
                val = json.loads(val)
            except Exception:
                pass
        res[col_name] = val
    return res
