from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .constants import FAST_COOKING as FC, SLOW_COOKING as SC
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


class HasSubscriptionsOrFollowersFilter(admin.SimpleListFilter):
    title = 'Есть подписки/подписчики'
    parameter_name = 'has_subscriptions_or_followers'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Да'),
            ('false', 'Нет'),
        )

    def queryset(self, request, users):
        if self.value() == 'true':
            return users.filter(
                Q(followers__isnull=False) | Q(authors__isnull=False)
            )
        elif self.value() == 'false':
            return users.exclude(
                Q(followers__isnull=False) | Q(authors__isnull=False)
            )


class CookingTimeFilter(admin.SimpleListFilter):
    title = _('Время приготовления')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return (
            ('fast', _('Быстрые')),
            ('medium', _('Средние')),
            ('slow', _('Долгие')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lt=FC)
        elif self.value() == 'medium':
            return queryset.filter(cooking_time__gte=FC, cooking_time__lt=SC)
        elif self.value() == 'slow':
            return queryset.filter(cooking_time__gte=SC)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'total_recipes',
        'total_followers',
        'total_authors',
    )
    search_fields = (
        'username',
        'email',
    )

    @admin.display(description='Количество рецептов')
    def total_recipes(self, recipe):
        return recipe.recipes.count()

    @admin.display(description='Количество подписок')
    def total_authors(self, author):
        return Follow.objects.filter(author=author).count()

    @admin.display(description='Количество подписчиков')
    def total_followers(self, follower):
        return Follow.objects.filter(follower=follower).count()

    def get_list_filter(self, request):
        return (HasSubscriptionsOrFollowersFilter,)


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
    readonly_fields = ('measurement_unit',)

    @admin.display(description='Единица измерения')
    def measurement_unit(self, item):
        return item.ingredient.measurement_unit


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
    )
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = (
        'name',
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
    def display_image(self, recipe):
        return format_html(
            f'<img src="{recipe.image.url}" width="80" height="60">'
        )

    @admin.display(description='В избранном')
    def total_favorite(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()

    @admin.display(description='Теги')
    def display_tags(self, recipe):
        tags_list = [
            f'<li>{tag.name}</li>'
            for tag in recipe.tags.all()
        ]
        return mark_safe('<ul>' + ''.join(tags_list) + '</ul>')

    @admin.display(description='Продукты')
    def display_ingredients(self, recipe):
        ingredients_list = []
        for ingredient in recipe.ingredients.all():
            recipe_ingredient = RecipeIngredients.objects.get(
                recipe=recipe,
                ingredient=ingredient
            )
            ingredients_list.append(
                f'<li>{ingredient.name}: '
                f'{recipe_ingredient.amount} '
                f'{ingredient.measurement_unit}</li>')
        return mark_safe('<ul>' + ''.join(ingredients_list) + '</ul>')

    def get_formsets_with_inlines(self, request, recipe=None):
        for inline in self.get_inline_instances(request, recipe):
            yield inline.get_formset(request, recipe), inline


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

    @admin.display(description='Количество применения в рецептах')
    def used_in_recipes_count(self, ingredient):
        return RecipeIngredients.objects.filter(ingredient=ingredient).count()


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount', 'measurement_unit')
    search_fields = ('recipe__name', 'ingredient__name')

    @admin.display(description='Мера')
    def measurement_unit(self, recipe_ingredient):
        return recipe_ingredient.ingredient.measurement_unit


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
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
