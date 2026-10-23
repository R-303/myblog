# 项目交接笔记

## 目标

做一个自己的 Django 博客，作为第一个完整项目和简历作品。循序渐进，不追求一次做完。

## 当前阶段

阶段 5 进行中：评论已完成，顶/踩投票待做。
最近代码提交：`7a8fbb5 feat: add post comments`。

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
- `Category`、`Tag`、`Post`、`SiteSetting` 模型
- Admin 后台和文章、分类、标签、站点设置管理
- 文章列表、详情、分类、标签、归档页面
- 浏览量和统一分页
- 最新文章 / 分类 / 归档侧边栏
- Markdown 正文、代码高亮和表格
- `Comment` 模型、`CommentForm`、评论提交和评论列表
- 评论默认转义，`<script>` 只显示为文字
- 15 个模型与视图测试

## 下一步

1. 新增 `Vote` 模型；
2. 用 `UniqueConstraint` 限制同一 Session 对同一文章只能投一次；
3. 在详情页增加顶/踩按钮；
4. 用 `F()` 更新票数并补测试；
5. 提交阶段 5 的投票部分；
6. 然后进入用户认证。

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
