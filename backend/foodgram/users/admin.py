from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, Follow


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'email',
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = (
        'user__username',
        'author__username',
    )
    list_filter = (
        'user',
        'author',
    )


admin.site.empty_value_display = 'Не задано'
