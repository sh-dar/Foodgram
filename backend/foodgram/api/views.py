from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
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
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow


User = get_user_model()


class UserViewSet(UserViewSet):
    pagination_class = LimitPagination

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,
                                       AuthorOrReadOnly,)
        return super().get_permissions()

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        serializer = FollowSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=user, author=author
            )
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = get_object_or_404(User, username=request.user)
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSafeSerializer
    pagination_class = LimitPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSafeSerializer
        return RecipeSerializer

    def create_recipe(self, user, pk, serializer):
        serializer = serializer(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт не существует'},
            status=HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=('POST', 'DELETE'))
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_recipe(request.user, pk, FavoriteSerializer)
        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_recipe(
                request.user, pk, ShoppingCartSerializer
            )
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request.user, pk)
        return None

    @action(
        methods=('GET',),
        detail=False,
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        shopping = ShoppingCart.objects.filter(user=user).values_list(
            'recipe',
            flat=True
        )
        file_name = 'shopping_cart.txt'
        shopping_list = []
        shopping_list.append(f'Список покупок пользователя {user.username}:\n')
        ingredients = IngredientRecipe.objects.filter(
            recipe_id__in=shopping
        ).values('ingredient').annotate(total_amount=Sum('amount'))
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(
                id=ingredient['ingredient']
            )
            shopping_list.append('{0} ({1}) - {2}'.format(
                ingredient_obj.name,
                ingredient_obj.measurement_unit,
                ingredient['total_amount']
            ))
        response_content = '\n'.join(shopping_list)
        response = HttpResponse(response_content, content_type="text")
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            file_name
        )
        return response


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
