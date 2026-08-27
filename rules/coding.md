---
purpose: 编码规范
content: Python、静态前端、业务边界和提交前检查规则
created_at: 2026-07-15 00:00:00
updated_at: 2026-07-15 00:00:00
---

# 编码规范

- Python 代码保持现有 FastAPI + SQLAlchemy + Pydantic 风格。
- 前端保持 `app/static/` 原生 HTML/CSS/JS 架构，不引入框架除非有明确 Change。
- 业务逻辑优先放在 `app/services.py` 或专门模块，存储逻辑放 `app/storage.py`，认证逻辑放 `app/auth*.py`。
- 变更应保持向后兼容；若会破坏历史数据或 API，必须补充迁移与回滚说明。
