import markdown
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register=template.Library()

@register.filter
def markdown_html(value):
    """把管理员写的 Markdown 转成 HTML。"""

    return mark_safe(
        markdown.markdown(
            value,
            extensions=["fenced_code","tables","codehilite"],
            extension_configs={
                "codehilite": {
                    "pygments_style":settings.PYGMENTS_STYLE,
                }
            }
        )
    )

"""
__init__.py 很重要，没有它，templatetags 不会被当成 Python 包，Django 找不到过滤器。
给 Django 模板增加一个自定义过滤器，把数据库里的 Markdown 原文转换成 HTML。
Admin 里写 Markdown
  → 保存到 Post.body（数据库里存的是 Markdown 原文）
  → 模板渲染时调用 {{ post.body|markdown_html }}
  → blog_extras.py 里的 markdown.markdown(...) 转成 HTML
  → mark_safe 告诉 Django“这段 HTML 可以按原样输出”
  → 浏览器显示标题、代码块、表格
codehilite：把代码块交给 Pygments 处理，生成带语法高亮 class 的 HTML，通常包在 .codehilite 容器里。
"""