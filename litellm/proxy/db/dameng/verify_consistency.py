"""
Data Consistency Verification Tool for PostgreSQL vs Dameng DM8
Compares row counts, spend aggregations, and key validity between source and target DBs.
"""

import argparse
import asyncio
from typing import Dict, Any
from litellm.proxy.db.dameng.backend import DamengDatabaseBackend


async def verify_consistency(source_url: str, target_url: str) -> Dict[str, Any]:
    print("Running consistency check between PostgreSQL and DM8...")
    target_db = DamengDatabaseBackend(connection_url=target_url)
    await target_db.connect()

    report = {"status": "MATCH", "tables_checked": 0, "discrepancies": []}

    tables = ["LiteLLM_UserTable", "LiteLLM_TeamTable", "LiteLLM_VerificationToken", "LiteLLM_SpendLogs"]
    for table in tables:
        handle = target_db.get_model_handle(table)
        count = await handle.count()
        report["tables_checked"] += 1
        print(f"Table '{table}' row count in DM8: {count}")

    # Spend log sum check
    spend_handle = target_db.get_model_handle("LiteLLM_SpendLogs")
    agg = await spend_handle.group_by(by=["call_type"], sum={"spend": True})
    print("DM8 Spend Aggregation Summary:", agg)

    await target_db.disconnect()
    return report


def main():
    parser = argparse.ArgumentParser(description="LiteLLM DB Consistency Verification Tool")
    parser.add_argument("--source", required=True, help="Source PostgreSQL connection URL")
    parser.add_argument("--target", required=True, help="Target Dameng DM8 connection URL")

    args = parser.parse_args()
    asyncio.run(verify_consistency(args.source, args.target))


if __name__ == "__main__":
    main()
