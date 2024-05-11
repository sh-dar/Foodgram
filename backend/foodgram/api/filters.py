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

    def filter_tags(self, recipes, slug, tags):
        return recipes.filter(
            tags__slug__in=self.request.GET.getlist('tags')
        ).distinct()

    def filter_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(
                favorites__user=self.request.user
            )
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(
                shoppingcarts__user=self.request.user
            )
        return recipes
