from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
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
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from .utils import generate_shopping_list_text


User = get_user_model()


class CustomUserViewSet(UserViewSet):
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

        recipe_in_list = model.objects.filter(
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        )
        if recipe_in_list.exists():
            recipe_in_list.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт не существует'},
            status=HTTP_400_BAD_REQUEST
        )

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
        shopping = ShoppingCart.objects.filter(user=user).values_list(
            'recipe',
            flat=True
        )
        file_name = 'shopping_cart.txt'
        shopping_list = []
        ingredients = RecipeIngredients.objects.filter(
            recipe_id__in=shopping
        ).values('ingredient').annotate(total_amount=Sum('amount'))
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(
                id=ingredient['ingredient']
            )
            shopping_list.append({
                'name': ingredient_obj.name,
                'measurement_unit': ingredient_obj.measurement_unit,
                'total_amount': ingredient['total_amount']
            })
        recipes = [
            recipe.name for recipe in Recipe.objects.filter(id__in=shopping)
        ]
        response_content = generate_shopping_list_text(
            user,
            shopping_list,
            recipes
        )
        response = FileResponse(response_content, content_type="text")
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
