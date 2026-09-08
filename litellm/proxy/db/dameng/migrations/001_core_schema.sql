-- Migration 001: Baseline Schema for LiteLLM on DM8 Dameng Database

CREATE TABLE LITELLM_SCHEMA_VERSION (
    version INT NOT NULL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "LiteLLM_BudgetTable" (
    budget_id VARCHAR(255) NOT NULL PRIMARY KEY,
    max_budget DOUBLE,
    soft_budget DOUBLE,
    max_parallel_requests INT,
    tpm_limit BIGINT,
    rpm_limit BIGINT,
    model_max_budget CLOB,
    budget_duration VARCHAR(255),
    budget_reset_at TIMESTAMP,
    allowed_models CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_CredentialsTable" (
    credential_id VARCHAR(255) NOT NULL PRIMARY KEY,
    credential_name VARCHAR(255) NOT NULL UNIQUE,
    credential_values CLOB NOT NULL,
    credential_info CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_ProxyModelTable" (
    model_id VARCHAR(255) NOT NULL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    litellm_params CLOB NOT NULL,
    model_info CLOB,
    blocked BIT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_AgentsTable" (
    agent_id VARCHAR(255) NOT NULL PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL UNIQUE,
    litellm_params CLOB,
    agent_card_params CLOB NOT NULL,
    static_headers CLOB,
    extra_headers CLOB,
    agent_access_groups CLOB,
    object_permission_id VARCHAR(255),
    spend DOUBLE DEFAULT 0.0,
    tpm_limit INT,
    rpm_limit INT,
    session_tpm_limit INT,
    session_rpm_limit INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_OrganizationTable" (
    organization_id VARCHAR(255) NOT NULL PRIMARY KEY,
    organization_alias VARCHAR(255) NOT NULL,
    budget_id VARCHAR(255) NOT NULL,
    metadata CLOB,
    models CLOB,
    spend DOUBLE DEFAULT 0.0,
    model_spend CLOB,
    object_permission_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_ModelTable" (
    id INT IDENTITY(1, 1) NOT NULL PRIMARY KEY,
    model_aliases CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_TeamTable" (
    team_id VARCHAR(255) NOT NULL PRIMARY KEY,
    team_alias VARCHAR(255),
    organization_id VARCHAR(255),
    object_permission_id VARCHAR(255),
    admins CLOB,
    members CLOB,
    members_with_roles CLOB,
    metadata CLOB,
    max_budget DOUBLE,
    soft_budget DOUBLE,
    spend DOUBLE DEFAULT 0.0,
    models CLOB,
    max_parallel_requests INT,
    tpm_limit BIGINT,
    rpm_limit BIGINT,
    budget_duration VARCHAR(255),
    budget_reset_at TIMESTAMP,
    blocked BIT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_spend CLOB,
    model_max_budget CLOB,
    router_settings CLOB,
    team_member_permissions CLOB,
    access_group_ids CLOB,
    policies CLOB,
    default_team_member_models CLOB,
    budget_limits CLOB,
    model_id INT UNIQUE,
    allow_team_guardrail_config BIT DEFAULT 0
);

CREATE INDEX idx_team_org ON "LiteLLM_TeamTable"(organization_id);
CREATE INDEX idx_team_alias ON "LiteLLM_TeamTable"(team_alias);
CREATE INDEX idx_team_created ON "LiteLLM_TeamTable"(created_at);

CREATE TABLE "LiteLLM_ProjectTable" (
    project_id VARCHAR(255) NOT NULL PRIMARY KEY,
    project_alias VARCHAR(255),
    description VARCHAR(1000),
    team_id VARCHAR(255),
    budget_id VARCHAR(255),
    metadata CLOB,
    models CLOB,
    spend DOUBLE DEFAULT 0.0,
    model_spend CLOB,
    model_rpm_limit CLOB,
    model_tpm_limit CLOB,
    blocked BIT DEFAULT 0,
    object_permission_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE "LiteLLM_UserTable" (
    user_id VARCHAR(255) NOT NULL PRIMARY KEY,
    user_alias VARCHAR(255),
    team_id VARCHAR(255),
    sso_user_id VARCHAR(255) UNIQUE,
    organization_id VARCHAR(255),
    object_permission_id VARCHAR(255),
    password VARCHAR(255),
    teams CLOB,
    user_role VARCHAR(255),
    max_budget DOUBLE,
    spend DOUBLE DEFAULT 0.0,
    user_email VARCHAR(255),
    models CLOB,
    metadata CLOB,
    max_parallel_requests INT,
    tpm_limit BIGINT,
    rpm_limit BIGINT,
    budget_duration VARCHAR(255),
    budget_reset_at TIMESTAMP,
    allowed_cache_controls CLOB,
    policies CLOB,
    model_spend CLOB,
    model_max_budget CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "LiteLLM_VerificationToken" (
    token VARCHAR(255) NOT NULL PRIMARY KEY,
    key_name VARCHAR(255),
    key_alias VARCHAR(255),
    soft_budget_cooldown BIT DEFAULT 0,
    spend DOUBLE DEFAULT 0.0,
    expires TIMESTAMP,
    models CLOB,
    aliases CLOB,
    config CLOB,
    router_settings CLOB,
    user_id VARCHAR(255),
    team_id VARCHAR(255),
    agent_id VARCHAR(255),
    project_id VARCHAR(255),
    permissions CLOB,
    max_parallel_requests INT,
    metadata CLOB,
    blocked BIT,
    tpm_limit BIGINT,
    rpm_limit BIGINT,
    max_budget DOUBLE,
    budget_duration VARCHAR(255),
    budget_reset_at TIMESTAMP,
    allowed_cache_controls CLOB,
    allowed_routes CLOB,
    policies CLOB,
    access_group_ids CLOB,
    model_spend CLOB,
    model_max_budget CLOB,
    budget_id VARCHAR(255),
    organization_id VARCHAR(255),
    object_permission_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    last_active TIMESTAMP,
    rotation_count INT DEFAULT 0,
    auto_rotate BIT DEFAULT 0,
    rotation_interval VARCHAR(255),
    last_rotation_at TIMESTAMP,
    key_rotation_at TIMESTAMP,
    budget_limits CLOB
);

CREATE INDEX idx_vt_user_team ON "LiteLLM_VerificationToken"(user_id, team_id);
CREATE INDEX idx_vt_team ON "LiteLLM_VerificationToken"(team_id);
CREATE INDEX idx_vt_budget_expires ON "LiteLLM_VerificationToken"(budget_reset_at, expires);

CREATE TABLE "LiteLLM_SpendLogs" (
    request_id VARCHAR(255) NOT NULL PRIMARY KEY,
    call_type VARCHAR(255) NOT NULL DEFAULT '',
    api_key VARCHAR(255) NOT NULL DEFAULT '',
    spend DOUBLE DEFAULT 0.0,
    total_tokens INT DEFAULT 0,
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    startTime TIMESTAMP NOT NULL,
    endTime TIMESTAMP NOT NULL,
    request_duration_ms INT,
    completionStartTime TIMESTAMP,
    model VARCHAR(255) DEFAULT '',
    model_id VARCHAR(255) DEFAULT '',
    model_group VARCHAR(255) DEFAULT '',
    custom_llm_provider VARCHAR(255) DEFAULT '',
    api_base VARCHAR(255) DEFAULT '',
    user VARCHAR(255) DEFAULT '',
    metadata CLOB,
    cache_hit VARCHAR(255) DEFAULT '',
    cache_key VARCHAR(255) DEFAULT '',
    request_tags CLOB,
    team_id VARCHAR(255),
    organization_id VARCHAR(255),
    end_user VARCHAR(255),
    requester_ip_address VARCHAR(255),
    messages CLOB,
    response CLOB,
    session_id VARCHAR(255),
    status VARCHAR(255),
    mcp_namespaced_tool_name VARCHAR(255),
    agent_id VARCHAR(255),
    proxy_server_request CLOB
);

CREATE INDEX idx_sl_starttime ON "LiteLLM_SpendLogs"(startTime);
CREATE INDEX idx_sl_starttime_reqid ON "LiteLLM_SpendLogs"(startTime, request_id);
CREATE INDEX idx_sl_enduser ON "LiteLLM_SpendLogs"(end_user);
CREATE INDEX idx_sl_sessionid ON "LiteLLM_SpendLogs"(session_id);

CREATE TABLE "LiteLLM_Config" (
    param_name VARCHAR(255) NOT NULL PRIMARY KEY,
    param_value CLOB
);

CREATE TABLE "LiteLLM_AuditLog" (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(255) DEFAULT '',
    changed_by_api_key VARCHAR(255) DEFAULT '',
    action VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    object_id VARCHAR(255) NOT NULL,
    before_value CLOB,
    updated_values CLOB
);

INSERT INTO LITELLM_SCHEMA_VERSION (version, migration_name) VALUES (1, '001_core_schema.sql');
