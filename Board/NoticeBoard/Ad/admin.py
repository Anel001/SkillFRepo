from django.contrib import admin
from .models import Category, Comment, Notice, Author, UserCategory

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Notice)
admin.site.register(Author)
admin.site.register(UserCategory)

# Register your models here.
