# 项目交接笔记

## 目标

做一个自己的 Django 博客，作为第一个完整项目和简历作品。循序渐进，不追求一次做完。

## 当前阶段

阶段 0 / 项目骨架，已完成。

## 技术栈

- Python 3.14.6
- Django 6.1
- uv 0.13.1
- SQLite

## 重要命令

```powershell
uv sync
uv run manage.py check
uv run manage.py runserver
uv run manage.py test
```

## 已完成

- Git 仓库初始化
- uv 项目与虚拟环境
- Django `config` 项目骨架
- 内置迁移已执行（`db.sqlite3` 已生成，未提交）
- `manage.py check` 通过

## 下一步

1. 在 PyCharm 里打开本目录；
2. 确认解释器指向 `.venv\Scripts\python.exe`；
3. 运行 `uv run manage.py runserver`，打开 <http://127.0.0.1:8000/>；
4. 做第一次 Git 提交；
5. 进入阶段 1：创建 `blog` 应用，写 `Category`、`Tag`、`Post` 模型。

## 约定

- 核心代码由我自己写，Codex 负责讲解、提示和 review；
- 每个阶段一个分支 / PR / tag；
- 每次结束写 `docs/devlog/YYYY-MM-DD.md`；
- 每个阶段结束必须能运行、测试通过、有提交。

## 关键决策

- 先用 SQLite，不在入门阶段引入 PostgreSQL；
- 先用函数视图，理解请求流向后再考虑类视图；
- 项目根目录就是 Django 根目录，教程里的 `source/` 对应这里；
- 入门阶段不装 OSS、Redis，相关功能留到加分阶段。
