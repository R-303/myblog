# 项目交接笔记

## 目标

做一个自己的 Django 博客，作为第一个完整项目和简历作品。循序渐进，不追求一次做完。

## 当前阶段

阶段 9 进行中：本地可部署配置、健康检查和 CI 已完成，等待真正部署到 Linux 服务器。
最近代码提交：`4ae4aa3 chore: prepare production deployment and ci`。
当前测试：28 个。

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
- `Vote` 模型、顶/踩按钮和 Session 限投一次
- 用 `UniqueConstraint` 防止重复投票
- 用 `F()` 原子更新顶/踩计数
- `UserRegistrationForm`、注册后自动登录
- 登录、登出页面和导航栏登录状态
- 登出使用 POST + CSRF
- 首页搜索、搜索词分页保持和后台文章统计
- `Attachment` 模型、本地媒体文件上传和详情页图片展示
- `MEDIA_URL` / `MEDIA_ROOT` 和开发环境媒体文件路由
- 侧边栏 LocMemCache 缓存
- 环境变量驱动的生产配置
- `/healthz/` 健康检查
- Dockerfile、`.dockerignore` 和 GitHub Actions CI
- 28 个模型与视图测试

## 下一步

1. 准备 Linux 服务器或云主机；
2. 用 Docker 或 Gunicorn 启动应用；
3. 用 Nginx 提供 HTTPS、静态文件和媒体文件；
4. 配置生产环境变量；
5. 验证公网地址和 `/healthz/`；
6. 把阶段 9 标为完成。

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
