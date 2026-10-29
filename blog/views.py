from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import F,Count,Q
from django.core.paginator import Paginator
from django.utils import archive
from django.contrib import messages
from django.http import Http404
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.views import LoginView,LogoutView
from django.core.cache import  cache

from .models import Post,Category,Tag,SiteSetting,Vote
from .forms import CommentForm,UserRegistrationForm

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
        "latest_posts":list(Post.published.all()[:5]),
        "sidebar_categories":list(categories),
        "archives":list(archives),
    }
# 把 sidebar_context() 的返回改成列表，避免缓存惰性 QuerySet：

def cached_sidebar_context():
    return cache.get_or_set(
        "blog:sidebar:v1",
        sidebar_context,
        timeout=60,
    )

def paginate_posts(request,posts):
    page_size=max(1,SiteSetting.load().page_size)
    return Paginator(posts,page_size).get_page(request.GET.get("page"))

def post_list(request):
    posts=(
        Post.published
        .select_related("category")
        .prefetch_related("tags")
    )

    query=request.GET.get("q","").strip()

    if query:
        posts=posts.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(body__icontains=query)
        )

    page_obj=paginate_posts(request,posts)

    return render(request,"blog/post_list.html",{
        **cached_sidebar_context(),
        "posts":page_obj,
        "page_obj":page_obj,
        "query":query,
        "page_title":f"搜索： {query}" if query else "文章列表",
    })

def post_detail(request,pk):
    post=get_object_or_404(
        Post.published.select_related("category").prefetch_related("tags"),
        pk=pk,
    )
    Post.objects.filter(pk=pk).update(views=F("views")+1)
    post.refresh_from_db(fields=["views"])

    form=CommentForm()
    return render(request,"blog/post_detail.html",{
        "post":post,
        "form":form,
        **cached_sidebar_context(),
    })

def add_comment(request,pk):
    post=get_object_or_404(Post.published,pk=pk)

    if request.method=="POST":
        form=CommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.post=post
            comment.save()
            messages.success(request,"评论已提交。")
            return redirect("blog:detail",pk=post.pk)
        messages.error(request,"请检查昵称、邮箱和评论内容。")
    else:
        form=CommentForm()

    return render(request,"blog/post_detail.html",{
        "post":post,
        "form":form,
        **cached_sidebar_context(),
    })
# 这里用了 POST → 保存 → 重定向，避免用户刷新页面时重复提交评论。

@require_POST
def vote(request,pk,value):
    if value  not in {"like","dislike"}:
        raise Http404("Oh,无效的投票类型!")

    post=get_object_or_404(Post.published,pk=pk)

    if not request.session.session_key:
        request.session.create()

    vote_value=1 if value=="like" else -1

    _,created=Vote.objects.get_or_create(
        post=post,
        session_key=request.session.session_key,
        defaults={"value":vote_value},
    )

    if not created:
        messages.info(request,"你已经对这篇文章投过票了。")
        return redirect("blog:detail",pk=post.pk)

    field="likes" if vote_value ==1 else "dislikes"
    Post.objects.filter(pk=post.pk).update(
        **{field:F(field)+1}
    )

    messages.success(request,"感谢亲的反馈。")
    return redirect("blog:detail",pk=post.pk)
"""
流程是：
1. 只允许 POST，防止用 GET 链接刷票；
2. 先拿到或创建 Session；
3. 尝试创建一条 Vote；
4. 如果已经存在，就提示“已投过”；
5. 只有新建成功，才给文章计数 +1。
"""


def category_posts(request,slug):
    category=get_object_or_404(Category,slug=slug)
    posts=(
        Post.published.filter(category=category)
        .select_related("category")
        .prefetch_related("tags")
    )
    page_obj=paginate_posts(request,posts)
    return render(request,"blog/post_list.html",{
        **cached_sidebar_context(),
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
        **cached_sidebar_context(),
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
        **cached_sidebar_context(),
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

from django.conf import settings
from django.http import Http404
def register(request):
    if not settings.ALLOW_REGISTRATION:
        raise Http404

    if request.user.is_authenticated:
        return redirect("blog:list")

    form=UserRegistrationForm(request.POST or None)

    if request.method=="POST" and form.is_valid():
        user=form.save()
        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        messages.success(request,"注册成功，欢迎您的加入。")
        return redirect("blog:list")

    return render(request,"registration/register.html",{
        "form":form,
    })




class BlogLoginView(LoginView):
    template_name = "registration/login.html"

class BlogLogoutView(LogoutView):
    pass

# 显式写 backend 是为了明确告诉 Django 用哪个认证后端，避免以后加多个后端时产生歧义。

