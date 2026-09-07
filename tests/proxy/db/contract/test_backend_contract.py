"""
Contract test suite for DatabaseBackend interface implementations.
Ensures identical behavior across backends.
"""

import pytest
import asyncio
from datetime import datetime
from litellm.proxy.db.dameng.backend import DamengDatabaseBackend


@pytest.fixture
async def dameng_backend():
    backend = DamengDatabaseBackend(connection_url="sqlite:///:memory:")
    await backend.connect()
    yield backend
    await backend.disconnect()


@pytest.mark.asyncio
async def test_contract_verification_token_crud(dameng_backend):
    db = dameng_backend
    vt = db.litellm_verificationtoken

    # 1. Create
    token_data = {
        "token": "contract-tok-1",
        "key_name": "contract_key",
        "models": ["gpt-4", "claude-3"],
        "metadata": {"team": "infra"},
        "spend": 10.5,
    }
    created = await vt.create(token_data)
    assert created["token"] == "contract-tok-1"
    assert created["key_name"] == "contract_key"
    assert created["models"] == ["gpt-4", "claude-3"]
    assert created["metadata"] == {"team": "infra"}
    assert created["spend"] == 10.5

    # 2. Find Unique
    found = await vt.find_unique({"token": "contract-tok-1"})
    assert found is not None
    assert found["token"] == "contract-tok-1"
    assert found["models"] == ["gpt-4", "claude-3"]

    # 3. Update
    updated = await vt.update(
        where={"token": "contract-tok-1"},
        data={"spend": 15.0, "models": ["gpt-4", "claude-3", "o1"]}
    )
    assert updated["spend"] == 15.0
    assert "o1" in updated["models"]

    # 4. Upsert (existing)
    upserted_exist = await vt.upsert(
        where={"token": "contract-tok-1"},
        data={
            "create": {"token": "contract-tok-1", "spend": 0.0},
            "update": {"spend": 20.0}
        }
    )
    assert upserted_exist["spend"] == 20.0

    # 5. Upsert (new)
    upserted_new = await vt.upsert(
        where={"token": "contract-tok-2"},
        data={
            "create": {"token": "contract-tok-2", "spend": 5.0, "key_name": "new_key"},
            "update": {"spend": 10.0}
        }
    )
    assert upserted_new["token"] == "contract-tok-2"
    assert upserted_new["spend"] == 5.0

    # 6. Delete
    deleted = await vt.delete({"token": "contract-tok-1"})
    assert deleted["token"] == "contract-tok-1"

    found_after_del = await vt.find_unique({"token": "contract-tok-1"})
    assert found_after_del is None


@pytest.mark.asyncio
async def test_contract_spend_logs_aggregation(dameng_backend):
    db = dameng_backend
    spend_logs = db.litellm_spendlogs
    now = datetime.utcnow()

    # Bulk create spend logs
    logs = [
        {"request_id": "r1", "spend": 1.0, "prompt_tokens": 100, "completion_tokens": 50, "startTime": now, "endTime": now, "api_key": "k1"},
        {"request_id": "r2", "spend": 2.0, "prompt_tokens": 200, "completion_tokens": 100, "startTime": now, "endTime": now, "api_key": "k1"},
        {"request_id": "r3", "spend": 3.0, "prompt_tokens": 300, "completion_tokens": 150, "startTime": now, "endTime": now, "api_key": "k2"},
    ]
    await spend_logs.create_many(logs)

    # Group by api_key
    agg = await spend_logs.group_by(by=["api_key"], sum={"spend": True, "prompt_tokens": True})
    assert len(agg) == 2
    agg_map = {item["api_key"]: item["_sum"] for item in agg}
    assert agg_map["k1"]["spend"] == 3.0
    assert agg_map["k1"]["prompt_tokens"] == 300
    assert agg_map["k2"]["spend"] == 3.0
    assert agg_map["k2"]["prompt_tokens"] == 300
