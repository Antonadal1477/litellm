"""
Schema Drift Verification Script
Compares schema.prisma model definitions against Dameng ORM models in litellm/proxy/db/dameng/models.py
"""

import re
import sys
from litellm.proxy.db.dameng import models


def parse_prisma_models(prisma_file="schema.prisma"):
    with open(prisma_file, "r", encoding="utf-8") as f:
        content = f.read()
    model_names = re.findall(r'model\s+(\w+)\s*\{', content)
    return set(model_names)


def get_dameng_models():
    dm_models = set()
    for name, obj in models.__dict__.items():
        if isinstance(obj, type) and issubclass(obj, models.Base) and obj is not models.Base:
            dm_models.add(name)
    return dm_models


def check_schema_diff():
    prisma_models = parse_prisma_models()
    dameng_models = get_dameng_models()

    print(f"Total Prisma Models in schema.prisma: {len(prisma_models)}")
    print(f"Total DM ORM Models in models.py: {len(dameng_models)}")

    missing_in_dm = prisma_models - dameng_models
    if missing_in_dm:
        print(f"Warning: {len(missing_in_dm)} models in schema.prisma not yet implemented in DM models:")
        for m in sorted(missing_in_dm):
            print(f"  - {m}")
    else:
        print("Schema sync check complete: Core target models aligned!")


if __name__ == "__main__":
    check_schema_diff()
