from django.shortcuts import get_object_or_404, render
from django.db.models import F

from .models import Post,Category,Tag

def post_list(request):
    posts=(
        Post.published.select_related("category").prefetch_related("tags")
    )
    # posts=Post.published.all()
    return render(request,"blog/post_list.html",
                  {"posts":posts,"page_title":"文章列表",})


def post_detail(request,pk):
    post=get_object_or_404(
        Post.published.select_related("category").prefetch_related("tags"),
        pk=pk,
    )
    Post.objects.filter(pk=pk).update(views=F("views")+1)
    post.refresh_from_db(fields=["views"])
    # post=get_object_or_404(Post.published,pk=pk)
    return render(request,"blog/post_detail.html",{"post":post})


"""
两个视图分别做两件事：
- post_list：查出所有已发布文章，交给列表模板；
- post_detail：按主键查一篇文章，找不到就返回 404。
这里用 Post.published 而不是 Post.objects，
所以草稿不会出现在前台。

为什么用 F("views") + 1：
- 先 post.views += 1 再 save()，是“读出来、加一、写回去”，并发时可能互相覆盖；
- F("views") + 1 让数据库直接执行 views = views + 1，更安全；
- refresh_from_db 是为了让页面显示加完后的数字。
select_related 用于外键分类，prefetch_related 用于多对多标签，可以减少列表页的 SQL 数量。

并发就是两个请求几乎同时操作同一份数据。
在博客里，可能是一个人开了两个浏览器标签，
也可能是两个访客同时点开同一篇文章，或者生产环境里 Gunicorn 开了多个 worker 同时处理请求。
F(views)数据库在自己的内部完成“读取当前值、加一、写回”，这是一个原子操作。两个请求同时来，数据库会依次执行两次 UPDATE，最终变成 12，不会互相覆盖。
F() 解决的是这一类“基于当前值做增减”的并发问题

"""

def category_posts(request,slug):
    category=get_object_or_404(Category,slug=slug)
    posts=(
        Post.published.filter(category=category).select_related("category").prefetch_related("tags")
    )
    return render(request,"blog/post_list.html",
                  {"posts":posts,
                   "page_title":f"分类：{category.name}",
                   })

def tag_posts(request,slug):
    tag=get_object_or_404(Tag,slug=slug)
    posts=(
        Post.published.filter(tags=tag).select_related("category").prefetch_related("tags")
    )
    return render(request,"blog/post_list.html",
                  {"posts":posts,
                   "page_title":f"标签：{tag.name}",
                   })

def archive_posts(request,year,month):
    posts=(
        Post.published.filter(published_at__year=year,published_at__month=month)
        .select_related("category")
        .prefetch_related("tags")
    )
    return render(request,"blog/post_list.html",
                  {"posts":posts,
                   "page_title":f"{year} 年 {month} 月归档",
                   })

"""
重点看过滤条件：
- 分类：filter(category=category)；
- 标签：filter(tags=tag)；
- 归档：published_at__year=year、published_at__month=month。
__year、__month 是 Django ORM 的字段查询语法，不是 Python 的普通属性。
"""
