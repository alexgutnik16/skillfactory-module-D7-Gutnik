from django_filters import FilterSet
from .models import Post


class NewsFilter(FilterSet):
    class Meta:
        model = Post
        fields = {'creation_date': ['gt'],
                  'heading': ['icontains'],
                  'author__author_user__username': ['icontains'],
                  'post_category__category_name': ['icontains']
                  }
