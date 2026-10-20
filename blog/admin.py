from django.contrib import admin

# Register your models here.

from .models import Category,Post,Tag

#语法糖 ,添加功能
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title","category","author","status","published_at"]
    list_filter = ["status","category","tags","author"]
    search_fields = ["title","summary","body"]
    prepopulated_fields = {"slug":["title"]}
    date_hierarchy = "published_at"

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

"""
Admin 是 Django 自带的后台管理界面。
@admin.register 把模型注册进去，
list_display 控制列表显示哪些列，
search_fields 控制搜索框搜哪些字段。
"""