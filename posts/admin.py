from django.contrib import admin
from .models import Post, Comment, Follow

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author") 
    search_fields = ("text",) 
    list_filter = ("pub_date",) 
    empty_value_display = '-пусто-'

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "created") 
    search_fields = ("text",) 
    list_filter = ("created",) 
    empty_value_display = '-пусто-'

admin.site.register(Comment, CommentAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author") 
    search_fields = ("user",) 
    empty_value_display = '-пусто-'

admin.site.register(Follow, FollowAdmin)