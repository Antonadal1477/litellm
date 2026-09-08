# LiteLLM 达梦 DM8 数据库适配指南 (LiteLLM Dameng DM8 Database Guide)

## 概述
LiteLLM 支持 **PostgreSQL (Prisma)** 与 **达梦数据库 DM8 (SQLAlchemy + dmPython)** 两种持久化模式。

达梦官方已提供标准的 Python 生态包：
- [达梦 dmSQLAlchemy 方言包说明](https://eco.dameng.com/document/dm/zh-cn/pm/dmsqlalchemy-dialect-package.html)
- [DamengDB dmSQLAlchemy GitHub 仓库](https://github.com/DamengDB/dmSQLAlchemy)

## 依赖安装

在使用达梦 DM8 模式前，请通过 pip 安装官方驱动包：

```bash
pip install dmPython
pip install dmSQLAlchemy
```

---

## 配置说明

### 环境变量配置

#### 1. 达梦 DM8 模式
```bash
DATABASE_TYPE=dameng
DATABASE_URL=dm+dmPython://LITELLM:password@10.0.0.10:5236/LITELLM
DATABASE_SCHEMA=LITELLM
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=20
DM_DB_WORKERS=20
```

#### 2. PostgreSQL 模式 (默认保持兼容)
```bash
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/litellm
```

---

## 运维工具与脚本

### 1. PostgreSQL -> DM8 数据迁移工具
```bash
python -m litellm.proxy.db.dameng.migrate \
    --source postgresql://user:pass@10.0.0.1:5432/litellm \
    --target dm+dmPython://LITELLM:pass@10.0.0.10:5236/LITELLM
```

### 2. 数据一致性校验工具
```bash
python -m litellm.proxy.db.dameng.verify_consistency \
    --source postgresql://user:pass@10.0.0.1:5432/litellm \
    --target dm+dmPython://LITELLM:pass@10.0.0.10:5236/LITELLM
```

### 3. Upstream Schema Diff 检查脚本
```bash
python tools/check_schema_diff.py
```

---

## Helm / K8s 配置
在 Helm `values.yaml` 中配置：
```yaml
database:
  type: dameng
  dameng:
    host: 10.0.0.10
    port: 5236
    database: LITELLM
    schema: LITELLM
    username: LITELLM
    existingSecret: dameng-secret
```
