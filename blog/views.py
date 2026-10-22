from django.shortcuts import get_object_or_404, render
from django.db.models import F,Count,Q
from django.core.paginator import Paginator
from django.utils import archive

from .models import Post,Category,Tag,SiteSetting

def sidebar_context():
    archives=(
        Post.published
        .filter(published_at__isnull=False)
        .values("published_at__year","published_at__month")
        .annotate(total=Count("id"))
        .order_by("-published_at__year","-published_at__month")
    )
    categories=(
        Category.objects
        .annotate(
            total=Count(
                "posts",
                filter=Q(posts__status=Post.Status.PUBLISHED),
            )
        )
        .filter(total__gt=0)
        .order_by("name")
    )
    return {
        "latest_posts":Post.published.all()[:5],
        "sidebar_categories":categories,
        "archives":archives,
    }

def paginate_posts(request,posts):
    page_size=max(1,SiteSetting.load().page_size)
    return Paginator(posts,page_size).get_page(request.GET.get("page"))

def post_list(request):
    posts=(
        Post.published
        .select_related("category")
        .prefetch_related("tags")
    )
    page_obj=paginate_posts(request,posts)
    return render(request,"blog/post_list.html",{
        **sidebar_context(),
        "posts":page_obj,
        "page_obj":page_obj,
        "page_title":"文章列表",
    })

def post_detail(request,pk):
    post=get_object_or_404(
        Post.published.select_related("category").prefetch_related("tags"),
        pk=pk,
    )
    Post.objects.filter(pk=pk).update(views=F("views")+1)
    post.refresh_from_db(fields=["views"])
    return render(request,"blog/post_detail.html",{
        **sidebar_context(),
        "post":post,
    })

def category_posts(request,slug):
    category=get_object_or_404(Category,slug=slug)
    posts=(
        Post.published.filter(category=category)
        .select_related("category")
        .prefetch_related("tags")
    )
    page_obj=paginate_posts(request,posts)
    return render(request,"blog/post_list.html",{
        **sidebar_context(),
        "posts":page_obj,
        "page_obj":page_obj,
        "page_title":f"分类：{category.name}",
    })

def tag_posts(request,slug):
    tag=get_object_or_404(Tag,slug=slug)
    posts=(
        Post.published.filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )
    page_obj=paginate_posts(request,posts)
    return render(request,"blog/post_list.html",{
        **sidebar_context(),
        "posts":page_obj,
        "page_obj":page_obj,
        "page_title":f"标签：{tag.name}",
    })

def archive_posts(request,year,month):
    posts=(
        Post.published.filter(
            published_at__year=year,
            published_at__month=month,
        )
        .select_related("category")
        .prefetch_related("tags")
    )
    page_obj=paginate_posts(request,posts)
    return render(request,"blog/post_list.html",{
        **sidebar_context(),
        "posts":page_obj,
        "page_obj":page_obj,
        "page_title":f"{year} 年 {month} 月归档",
    })

"""
这里的核心是：
- Paginator(posts, page_size) 把文章切成页；
- get_page() 读取 ?page=2 并返回对应页；
- sidebar_context() 给所有页面提供最新文章、分类和归档；
- 分类数量只统计已发布文章。
"""