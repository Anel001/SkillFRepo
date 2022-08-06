import django_filters
from .models import Comment, Notice


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            'notice'
        }

