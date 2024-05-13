from ast import literal_eval

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Q
from django.utils.safestring import mark_safe

from .constants import FAST_COOKING, SLOW_COOKING
from .constants import MAX_LENGTH_STRING
from .models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)

User = get_user_model()


class SubscriptionsFollowersFilter(admin.SimpleListFilter):
    title = 'Есть подписки/подписчики'
    parameter_name = 'has_subscriptions_or_followers'

    def lookups(self, request, model_admin):
        return (
            ('has_subscriptions', 'Есть подписки'),
            ('has_followers', 'Есть подписчики'),
        )

    def queryset(self, request, users):
        if self.value() == 'has_subscriptions':
            return users.filter(
                Q(followers__isnull=False)
            )
        if self.value() == 'has_followers':
            return users.filter(
                Q(authors__isnull=False)
            )


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):

        fast = (0, FAST_COOKING - 1)
        medium = (FAST_COOKING, SLOW_COOKING)
        slow = (SLOW_COOKING + 1, 10**10)

        fast_recipes_count = Recipe.objects.filter(
            cooking_time__range=fast
        ).count()
        medium_recipes_count = Recipe.objects.filter(
            cooking_time__range=medium
        ).count()
        slow_recipes_count = Recipe.objects.filter(
            cooking_time__range=slow
        ).count()

        return (
            (
                fast,
                f'Быстрые (< {FAST_COOKING} мин) '
                f'({fast_recipes_count})'
            ),
            (
                medium,
                f'Средние ({FAST_COOKING} - {SLOW_COOKING} мин) '
                f'({medium_recipes_count})'
            ),
            (
                slow,
                f'Долгие (> {SLOW_COOKING} мин) '
                f'({slow_recipes_count})'
            ),
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(
                cooking_time__range=literal_eval(self.value())
            )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'total_recipes',
        'total_followers',
        'total_subscriptions',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (SubscriptionsFollowersFilter,)

    @admin.display(description='Рецепты')
    def total_recipes(self, recipe):
        return recipe.recipes.count()

    @admin.display(description='Подписки')
    def total_subscriptions(self, user):
        return user.followers.count()

    @admin.display(description='Подписчики')
    def total_followers(self, user):
        return user.authors.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'follower',
        'author',
    )
    search_fields = (
        'follower__username',
        'author__username',
    )
    list_filter = (
        'author',
    )


class IngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 3
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'display_image',
        'cooking_time',
        'display_tags',
        'display_ingredients',
        'total_favorite',
        'pub_date',
    )
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = (
        'author__username',
        'tags',
        CookingTimeFilter
    )
    filter_horizontal = (
        'tags',
        'ingredients',
    )
    inlines = (
        IngredientInline,
    )

    @admin.display(description='Изображение')
    @mark_safe
    def display_image(self, recipe):
        return f'<img src="{recipe.image.url}" width="80" height="60">'

    @admin.display(description='В избранном')
    def total_favorite(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):
        return '<br> '.join(
            f'{ingredient.ingredient.name[:MAX_LENGTH_STRING]} - '
            f'{ingredient.amount} '
            f'{ingredient.ingredient.measurement_unit} '
            for ingredient in recipe.recipe_ingredients.all()
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'used_in_recipes_count',
    )
    search_fields = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'measurement_unit',
    )

    @admin.display(description='В рецептах')
    def used_in_recipes_count(self, ingredient):
        return RecipeIngredients.objects.filter(ingredient=ingredient).count()


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'display_color',
        'color',
        'slug',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )

    @admin.display(description='Цвет')
    @mark_safe
    def display_color(self, tag):
        return (
            f'<div style="background-color:{tag.color}; '
            f'width:30px; height:30px;">'
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = (
        'user__username',
        'recipe__name',
    )
    list_filter = (
        'user__username',
        'recipe__name',
        'recipe__tags',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = (
        'user__username',
        'recipe__name',
    )
    list_filter = (
        'user__username',
        'recipe__name',
        'recipe__tags',
    )


admin.site.empty_value_display = 'Не задано'
