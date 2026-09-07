"""
Integration tests for DM8 Dameng database backend.
Runs against real DM8 instance when DM_TEST_ENABLED=true is set in environment.
"""

import os
import pytest
import asyncio
from datetime import datetime
from litellm.proxy.db.dameng.backend import DamengDatabaseBackend

DM_TEST_ENABLED = os.getenv("DM_TEST_ENABLED", "false").lower() in ("true", "1")

pytestmark = pytest.mark.skipif(
    not DM_TEST_ENABLED,
    reason="DM8 live integration tests disabled. Set DM_TEST_ENABLED=true to run."
)


@pytest.fixture
async def live_dm_backend():
    url = os.getenv("DM_DATABASE_URL") or os.getenv("DATABASE_URL")
    backend = DamengDatabaseBackend(connection_url=url)
    await backend.connect()
    yield backend
    await backend.disconnect()


@pytest.mark.asyncio
async def test_live_dm_full_lifecycle(live_dm_backend):
    db = live_dm_backend

    health = await db.health_check()
    assert health["connected"] is True
    assert health["database_type"] == "dameng"

    # User creation
    user_handle = db.litellm_usertable
    created_user = await user_handle.create({
        "user_id": "dm-test-user-1",
        "user_email": "dmtest@example.com",
        "max_budget": 100.0,
    })
    assert created_user["user_id"] == "dm-test-user-1"

    # Team creation
    team_handle = db.litellm_teamtable
    created_team = await team_handle.create({
        "team_id": "dm-test-team-1",
        "team_alias": "infra_team",
        "max_budget": 500.0,
    })
    assert created_team["team_id"] == "dm-test-team-1"

    # Virtual Key creation
    vt_handle = db.litellm_verificationtoken
    created_key = await vt_handle.create({
        "token": "sk-dm-live-key-1",
        "key_name": "live_key",
        "user_id": "dm-test-user-1",
        "team_id": "dm-test-team-1",
        "models": ["gpt-4o", "deepseek-v3"],
    })
    assert created_key["token"] == "sk-dm-live-key-1"

    # Cleanup
    await vt_handle.delete({"token": "sk-dm-live-key-1"})
    await team_handle.delete({"team_id": "dm-test-team-1"})
    await user_handle.delete({"user_id": "dm-test-user-1"})
