from django.shortcuts import get_object_or_404
from posts.models import Group, Post, User
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import AuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class CreateListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет только для методов Create и List."""

    pass


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


class FollowViewSet(CreateListViewSet):
    """ViewSet для модели FollowViewSet."""

    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def perform_create(self, serializer):
        """Метод для заполнения поля user."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Фильтрация подписок по текущему пользователю."""
        return self.request.user.user
