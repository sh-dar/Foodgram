from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = CharFilter(
        field_name='tags__slug',
        method='filter_tags'
    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_tags(self, recipe_queryset, slug, tags):
        tags = self.request.query_params.getlist('tags')
        return recipe_queryset.filter(
            tags__slug__in=tags
        ).distinct()

    def filter_is_favorited(self, recipe_queryset, name, value):
        if value and self.request.user.is_authenticated:
            return recipe_queryset.filter(
                recipes_favorite_related__user=self.request.user
            )
        return recipe_queryset

    def filter_is_in_shopping_cart(self, recipe_queryset, name, value):
        if value and self.request.user.is_authenticated:
            return recipe_queryset.filter(
                recipes_shoppingcart_related__user=self.request.user
            )
        return recipe_queryset
