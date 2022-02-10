from django.shortcuts import get_object_or_404
from posts.models import Follow, Group, Post, User
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import AuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.AllowAny,)


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Post."""

    permission_classes = [AuthorOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """Метод для автоматического заполнения поля author."""
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Comment."""

    permission_classes = [AuthorOrReadOnly]
    serializer_class = CommentSerializer

    def get_post(self):
        """Метод для извлечения поста."""
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        """Метод для заполнения полей."""
        serializer.save(author=self.request.user,
                        post=self.get_post())

    def get_queryset(self):
        """Фильтрация комментариев по id поста."""
        return self.get_post().comments


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet для модели FollowViewSet."""

    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_following(self):
        """Метод для извлечения объекта Following."""
        return get_object_or_404(
            User, username=self.request.data.get('following')
        )

    def perform_create(self, serializer):
        """Метод для заполнения полей."""
        serializer.save(user=self.request.user,
                        following_id=self.get_following().id)

    def get_queryset(self):
        """Фильтрация подписок по текущему пользователю."""
        return Follow.objects.filter(user_id=self.request.user.id)
