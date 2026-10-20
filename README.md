# My Blog

一个使用 Django 6.1 构建的个人博客，正在按阶段学习和实现。

## 当前状态

- 阶段 0：项目骨架完成
- 下一步：阶段 1 模型与 Admin

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

## 项目结构

```text
.
├── config/          # 项目配置与根路由
├── docs/            # 学习路线、开发日志、决策记录
├── manage.py
└── pyproject.toml
```

后续会加入 `blog/` 应用、`templates/` 和 `static/`。

## 说明

本项目参考 [yidao620c/simpleblog](https://github.com/yidao620c/simpleblog) 的教程，但代码按自己的节奏分阶段实现。教程中的 `source/` 目录对应本仓库根目录。

## 学习记录

- 学习路线：`docs/roadmap.md`
- 每日日志：`docs/devlog/`
- 架构决策：`docs/adr/`
- 面试素材：`docs/interview/`
