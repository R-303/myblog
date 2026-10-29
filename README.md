# My Blog

[![CI](https://github.com/R-303/myblog/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/R-303/myblog/actions/workflows/ci.yml)

一个使用 Django 6.1 构建的个人博客，正在按阶段学习和实现。

## 当前状态

阶段 9 已完成：博客已部署到腾讯云轻量服务器，公网地址为 <http://49.232.18.58/>，CI 的 test 和 docker 均通过；私密站点已上线，当前有 31 个测试（3 个私密测试待提交）。

当前工作项：私密站点已部署，待加固注册接口的 POST 边界。

最近一次代码提交：

```text
89f26c8 feat: make comment email optional
```

## 开发阶段进度

| 阶段 | 内容 | 状态 | 完成标准 |
| --- | --- | --- | --- |
| 0 | 项目初始化、Git、uv、Django 骨架 | ✅ 已完成 | `manage.py check` 通过，首页可访问 |
| 1 | 模型与 Admin：`Category`、`Tag`、`Post` | ✅ 已完成 | 迁移成功，后台可写文章 |
| 2 | 列表页、详情页、浏览量、基础样式 | ✅ 已完成 | 首页和详情 200，草稿详情 404 |
| 3 | Markdown、代码高亮、表格 | ✅ 已完成 | 标题/代码/表格正常，测试通过 |
| 4 | 分类、标签、归档、分页、站点设置、侧边栏 | ✅ 已完成 | 各页面可访问，分页和侧边栏正常 |
| 5 | 评论、顶/踩、Session 限投一次 | ✅ 已完成 | 评论可提交并转义；顶/踩可计数，同一 Session 只能投一次 |
| 6 | 用户认证：注册、登录、登出 | ✅ 已完成 | 注册后自动登录，登录后显示用户名，登出使用 POST + CSRF |
| 7 | 搜索与后台统计 | ✅ 已完成 | 搜索只命中已发布文章，统计数字正确 |
| 8 | 图片上传、缓存 | ✅ 已完成 | 图片可上传展示，缓存减少查询 |
| 9 | 部署、健康检查、CI | ✅ 已完成 | 公网地址可访问，图片和后台正常，`/healthz/` 正常，CI 通过 |
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
- Markdown + Pygments

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

当前共 31 个测试，覆盖模型、列表/详情、浏览量、分类、标签、归档、分页、侧边栏、Markdown、评论、投票、用户认证、搜索、后台统计、图片附件、缓存、健康检查和私密访问。

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

私密站点已上线，剩余加固工作：

- 把 `ALLOW_REGISTRATION` 判断移到 `register()` 开头；
- 增加直接 POST 注册被拒绝的测试；
- 提交并推送剩余的私密测试；
- 服务器更新后再次验证登录跳转和 `/healthz/`。

完成后再进入阶段 10：个人化与作品化。

阶段 10：个人化与作品化。

- 修改站点名称、标语、头像和主色；
- 增加“关于我”页面；
- 增加 RSS 和 sitemap；
- 截图、录制演示视频；
- 完善 README 和面试素材。

## 私密站点模式（已上线，待加固）

目标是把当前公开博客临时改成“登录后才能访问”：

```text
游客访问首页
  → 跳转 /account/login/
  → 输入管理员创建的朋友账号
  → 登录后回到原文章页面
```

注意：

- 隐藏注册链接不等于关闭注册，后端也必须拒绝注册请求；
- 普通朋友账号不要赋予 staff/superuser 权限；
- Nginx 直接提供 `/media/`，页面登录保护不等于图片直链完全私密；
- 以后把 `PRIVATE_SITE=false` 和 `ALLOW_REGISTRATION=true` 写入 `.env`，即可恢复公开访问。
- 当前注册视图的关闭判断还需要移到函数开头，防止恢复公开模式后被直接 POST 绕过。

## 说明

本项目参考 [yidao620c/simpleblog](https://github.com/yidao620c/simpleblog) 的教程，但代码按自己的节奏分阶段实现。教程中的 `source/` 目录对应本仓库根目录。

## 学习记录

- 学习路线：`docs/roadmap.md`
- 每日日志：`docs/devlog/`
- 架构决策：`docs/adr/`
- 面试素材：`docs/interview/`
- 服务器入门：`docs/server-basics.md`
