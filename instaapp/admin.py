from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'birth_date', 'profile_picture', 'website')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'birth_date', 'profile_picture', 'website')}),
    )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
