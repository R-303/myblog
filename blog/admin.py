from django.contrib import admin
from django.http import HttpRequest
from django.db.models import Count,Q,Sum
# Register your models here.

from .models import Category,Post,Tag,SiteSetting,Comment,Vote,Attachment

#语法糖 ,添加功能
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title","category","author","status","published_at"]
    list_filter = ["status","category","tags","author"]
    search_fields = ["title","summary","body"]
    prepopulated_fields = {"slug":["title"]}
    date_hierarchy = "published_at"

    def changelist_view(self,request,extra_context=None):
        stats=Post.objects.aggregate(
            total=Count("id"),
            published=Count(
                "id",
                filter=Q(status=Post.Status.PUBLISHED),
            ),
            draft=Count(
                "id",
                filter=Q(status=Post.Status.DRAFT),
            ),
            views=Sum("views"),
        )

        total=stats["total"] or 1
        stats["average_views"]=(stats["views"] or 0)/total

        extra_context={
            "blog_stats":stats,
            **(extra_context or {}),
        }
        return super().changelist_view(request,extra_context)
# Count("id") 统计文章总数；  filter=Q(...) 只统计已发布或草稿；
# Sum("views") 统计总浏览量； average_views 用总浏览量除以文章数。

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name","slug","created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug":["name"]}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name","slug","created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug":["name"]}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["nickname","post","email","created_at"]
    search_fields = ["nickname","email","body"]
    list_filter = ["created_at"]

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["post","value","session_key","created_at"]
    list_filter = ["value","created_at"]

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ["site_name","page_size","updated_at"]

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()
"""
Admin 是 Django 自带的后台管理界面。
@admin.register 把模型注册进去，
list_display 控制列表显示哪些列，
search_fields 控制搜索框搜哪些字段。
"""

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["title","post","created_at"]
    search_fields = ["title","post__title"]
    list_filter = ["created_at"]
