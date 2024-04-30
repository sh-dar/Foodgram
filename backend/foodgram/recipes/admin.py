from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'display_image',
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
    )
    filter_horizontal = (
        'tags',
        'ingredients',
    )
    inlines = (
        IngredientInline,
    )

    @admin.display(description='Изображение')
    def display_image(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="80" height="60">'
            )
        return 'No Image'

    @admin.display(description='В избранном')
    def total_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


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
