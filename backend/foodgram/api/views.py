from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import LimitPagination
from .permissions import AuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSafeSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from .utils import generate_shopping_list_text


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(), AuthorOrReadOnly(),)
        return super().get_permissions()

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        follower = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        serializer = FollowSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            Follow.objects.create(follower=follower, author=author)
            return Response(serializer.data, status=HTTP_201_CREATED)

        get_object_or_404(Follow, follower=follower, author=author).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        serializer = FollowSerializer(
            self.paginate_queryset(
                User.objects.filter(
                    authors__follower=request.user
                )
            ),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSafeSerializer
        return RecipeSerializer

    @staticmethod
    def add_to_delete_from(request, pk, model, serializer):
        if request.method == 'POST':
            serializer = serializer(
                data={'user': request.user.id, 'recipe': pk},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        get_object_or_404(
            model,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST', 'DELETE'))
    def favorite(self, request, pk):
        return self.add_to_delete_from(
            request, pk, Favorite, FavoriteSerializer
        )

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk):
        return self.add_to_delete_from(
            request, pk, ShoppingCart, ShoppingCartSerializer
        )

    @action(
        methods=('GET',),
        detail=False,
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        shopping_list = RecipeIngredients.objects.filter(
            recipe__shoppingcarts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        recipes = [
            recipe for recipe in Recipe.objects.filter(
                shoppingcarts__user=user
            )
        ]
        return FileResponse(
            generate_shopping_list_text(
                user,
                shopping_list,
                recipes
            ),
            content_type='text',
            filename='shopping_cart.txt'
        )


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
