# My Blog

一个使用 Django 6.1 构建的个人博客，正在按阶段学习和实现。

## 当前状态

阶段 4 已完成，Markdown 与代码高亮也已完成。当前准备进入阶段 5：评论与投票。

最近一次代码提交：

```text
7c5a9d8 feat: render post body with markdown
```

## 开发阶段进度

| 阶段 | 内容 | 状态 | 完成标准 |
| --- | --- | --- | --- |
| 0 | 项目初始化、Git、uv、Django 骨架 | ✅ 已完成 | `manage.py check` 通过，首页可访问 |
| 1 | 模型与 Admin：`Category`、`Tag`、`Post` | ✅ 已完成 | 迁移成功，后台可写文章 |
| 2 | 列表页、详情页、浏览量、基础样式 | ✅ 已完成 | 首页和详情 200，草稿详情 404 |
| 3 | Markdown、代码高亮、表格 | ✅ 已完成 | 标题/代码/表格正常，测试通过 |
| 4 | 分类、标签、归档、分页、站点设置、侧边栏 | ✅ 已完成 | 各页面可访问，分页和侧边栏正常 |
| 5 | 评论、顶/踩、Session 限投一次 | 🟡 下一步 | 评论可提交并转义，投票不能重复 |
| 6 | 用户认证：注册、登录、登出 | ⬜ 未开始 | 注册后自动登录，登出使用 POST + CSRF |
| 7 | 搜索与后台统计 | ⬜ 未开始 | 搜索只命中已发布文章，统计数字正确 |
| 8 | 图片上传、缓存 | ⬜ 未开始 | 图片可上传展示，缓存减少查询 |
| 9 | 部署、健康检查、CI | ⬜ 未开始 | 公网可访问，`/healthz/` 正常，CI 通过 |
| 10 | 个人化、RSS/sitemap、作品化 | ⬜ 未开始 | 有个人主页、截图、README 和演示地址 |

### 可选扩展

| 扩展 | 状态 | 说明 |
| --- | --- | --- |
| 中英文国际化 | ⬜ 可选 | 教程第 13 篇 |
| 阿里云 OSS | ⬜ 可选 | 图片上传的云端方案 |
| Redis 缓存 | ⬜ 可选 | 多进程共享缓存 |
| PostgreSQL | ⬜ 可选 | 更接近生产环境 |
| 真正全文搜索 | ⬜ 可选 | SQLite FTS5 或 PostgreSQL SearchVector |
| RSS / sitemap | ⬜ 可选 | 适合博客的 SEO 和订阅功能 |

### 阶段完成标准

每个阶段至少满足以下四条才算完成：

1. 页面或功能可以正常运行；
2. `uv run manage.py check` 无错误；
3. `uv run manage.py test` 通过；
4. 有对应 Git 提交和开发日志。

## 技术栈

- Python 3.14
- Django 6.1
- uv
- SQLite
- Django Templates + 原生 CSS

## 本地运行

```powershell
uv sync
uv run manage.py runserver
```

打开 <http://127.0.0.1:8000/>。

后台地址：

```text
http://127.0.0.1:8000/admin/
```

## 测试

```powershell
uv run manage.py test
```

当前测试覆盖模型、列表/详情、浏览量、分类、标签、归档、分页和侧边栏。

## 项目结构

```text
.
├── blog/            # 文章模型、视图、Admin、测试、模板过滤器
├── config/          # 项目配置与根路由
├── templates/       # 页面模板和侧边栏
├── static/          # CSS 和代码高亮样式
├── docs/            # 学习路线、开发日志、决策记录
├── manage.py
└── pyproject.toml
```

## 下一步

阶段 5：评论与投票。

- 写 `CommentForm`；
- 在详情页正确渲染评论输入框；
- 提交评论并显示评论列表；
- 实现顶/踩，同一 Session 只能投一次；
- 补评论和投票测试；
- 修复参考教程中“评论表单只有按钮、没有输入框”的问题。

## 说明

本项目参考 [yidao620c/simpleblog](https://github.com/yidao620c/simpleblog) 的教程，但代码按自己的节奏分阶段实现。教程中的 `source/` 目录对应本仓库根目录。

## 学习记录

- 学习路线：`docs/roadmap.md`
- 每日日志：`docs/devlog/`
- 架构决策：`docs/adr/`
- 面试素材：`docs/interview/`
