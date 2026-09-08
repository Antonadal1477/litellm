# LiteLLM 达梦 DM8 数据库适配 Code Review 报告 (docs/dm_cr.md)

## 1. 概述与背景

本 Code Review 针对 LiteLLM Proxy 适配国产达梦 DM8 数据库的需求进行全面检查。

达梦数据库官方目前已提供了标准的 Python 生态支持：
- **达梦 dmSQLAlchemy 方言包文档**: [https://eco.dameng.com/document/dm/zh-cn/pm/dmsqlalchemy-dialect-package.html](https://eco.dameng.com/document/dm/zh-cn/pm/dmsqlalchemy-dialect-package.html)
- **GitHub 官方开源仓库**: [https://github.com/DamengDB/dmSQLAlchemy](https://github.com/DamengDB/dmSQLAlchemy)

根据官方规范，`dmPython` 是基于底层 C API 的 Python DB-API 驱动，而 `dmSQLAlchemy` 是 SQLAlchemy 的官方方言（Dialect）扩展，注册连接协议为 `dm+dmPython://user:pass@host:port/schema`。

---

## 2. 检查项与评估结果

### 2.1 依赖与包管理 (Dependencies)
| 检查项 | 状态 | 说明 |
| :--- | :---: | :--- |
| `pyproject.toml` 依赖 | **通过** | 在 `pyproject.toml` 中添加了 `sqlalchemy>=2.0.49` 核心依赖，并在 `[project.optional-dependencies]` 中增加了 `dameng = ["dmPython", "dmSQLAlchemy"]` 可选依赖组，符合标准 Python 包发布规范。 |
| 镜像与部署 | **通过** | 文档 `docs/dameng_dm8_guide.md` 明确了使用 `pip install dmPython dmSQLAlchemy` 进行驱动安装的步骤。 |

### 2.2 数据库连接与线程池 (Session & Connection Pool)
| 检查项 | 状态 | 说明 |
| :--- | :---: | :--- |
| 方言连接字符串 | **通过** | `litellm/proxy/db/dameng/session.py` 正确采用了官方标准连接格式 `dm+dmPython://...`。 |
| 连接池参数 | **通过** | `DamengSessionManager` 配置了 `pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`, `pool_pre_ping` 等关键连接池属性，支持通过环境变量控制。 |
| 异步 Event Loop 防阻塞 | **通过** | 鉴于 `dmPython` / `dmSQLAlchemy` 为同步驱动，通过受控的 `ThreadPoolExecutor`（线程数由 `DM_DB_WORKERS` 控制）与 `asyncio.to_thread` 进行了异步封装，确保上层 `async def` 接口不会阻塞 FastAPI 主事件循环。 |

### 2.3 ORM 模型与数据类型兼容 (Models & Types)
| 检查项 | 状态 | 说明 |
| :--- | :---: | :--- |
| 核心表覆覆盖 | **通过** | `litellm/proxy/db/dameng/models.py` 覆盖了 `VerificationToken`, `UserTable`, `TeamTable`, `BudgetTable`, `OrganizationTable`, `SpendLogs`, `AuditLog` 等 LiteLLM 核心表。 |
| JSON / Array 类型转换 | **注意项** | `litellm/proxy/db/dameng/types.py` 实现了 `JSONType` 和 `ArrayType` 的 `TypeDecorator`。当前 `models.py` 中列定义为了保证 SQLite 单元测试兼容，混用了 `Text` 加 `to_dict()` 自动解析逻辑。建议后续重构中直接在 SQLAlchemy Model 列定义中使用 `JSONType` / `ArrayType`。 |

### 2.4 CRUD、Upsert 与事务语义 (Repository Operations)
| 检查项 | 状态 | 说明 |
| :--- | :---: | :--- |
| 基础 CRUD | **通过** | `DamengModelHandle` 实现了 `find_unique`, `find_first`, `find_many`, `create`, `create_many`, `update`, `update_many`, `delete`, `delete_many`, `count`, `group_by`。 |
| Upsert 并发安全性 | **需优化** | 当前 `_sync_upsert` 采用了 `SELECT` -> 判断存在 -> `UPDATE / INSERT` 模式。在极高并发场景下（如虚拟 Key 批量创建），建议后续利用 DM8 的 `MERGE INTO` 语法或行级锁机制强化原子性。 |
| 事务管理 | **通过** | 实现了异步上下文管理器 `transaction()`，发生异常时支持回滚。 |

### 2.5 DDL 迁移与工具链 (Migrations & CLI Tools)
| 检查项 | 状态 | 说明 |
| :--- | :---: | :--- |
| DDL Migration | **通过** | 提供了版本化的达梦 DDL 建表脚本 (`001_core_schema.sql` 和 `002_extended_schema.sql`)，并包含 `LITELLM_SCHEMA_VERSION` 版本表。 |
| 数据迁移与校验工具 | **通过** | 提供了 `litellm/proxy/db/dameng/migrate.py` 和 `verify_consistency.py` 脚本框架。 |
| Upstream Schema Diff | **通过** | 提供了 `tools/check_schema_diff.py` 用于校验 `schema.prisma` 与达梦 SQLAlchemy ORM 模型间的字段差异。 |

---

## 3. 改进与后续建议

1. **业务代码深度解耦 (Business Logic Refactoring)**
   - 现阶段已完成数据库抽象层 (`litellm/proxy/db/`) 与达梦 Backend 的封装。
   - 下一阶段需逐步将 `proxy_server.py` 及各个管理路由中的直接 `prisma_client.db.xxx` 调用全面替换为抽象 Handle 调用（如 `db.verification_token`）。

2. **`MERGE INTO` 原生优化**
   - 针对达梦 DM8，可进一步在 `DamengModelHandle.upsert` 中直接构建达梦原生 SQL `MERGE INTO` 语句，提升在高并发冲突下的吞吐量。

3. **模型字段自动化同步**
   - 结合 `tools/check_schema_diff.py`，建立 CI 自动化检测机制，确保 Upstream `schema.prisma` 变动时能自动提示更新 `models.py`。
