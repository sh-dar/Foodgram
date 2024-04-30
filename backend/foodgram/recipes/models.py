from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    MAX_LENGTH_CHAR,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_STRING,
    MAX_TIME,
    MIN_TIME,
    MAX_COLOR_FIELD,
)

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        'Рецепт',
        max_length=MAX_LENGTH_CHAR,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Текстовое описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=(
            MinValueValidator(
                MIN_TIME,
                message=f'Время приготовления должно быть '
                        f'не менее {MIN_TIME} мин.'
            ),
            MaxValueValidator(
                MAX_TIME,
                message=f'Время приготовления не должно '
                        f'превышать {MAX_TIME} мин.'
            ),
        ),
        help_text=f'Введите время приготовления в минутах. '
                  f'Минимум: {MIN_TIME} , максимум: {MAX_TIME}'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRecipe',
        verbose_name='ингредиенты',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGTH_STRING]


class Tag(models.Model):
    name = models.CharField(
        'Тег',
        max_length=MAX_LENGTH_CHAR,
        unique=True,
    )
    color = models.CharField(
        'Цветовой код',
        max_length=MAX_COLOR_FIELD,
        unique=True,
    )
    slug = models.SlugField(
        'Идентификатор тега',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGTH_STRING]


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=MAX_LENGTH_CHAR,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_CHAR,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGTH_STRING]


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        default_related_name = 'ingredients_in_recipe'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredient_in_recipe'
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} '
            f'({self.ingredient.measurement_unit} - {self.amount})'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite_user_recipe'
            ),
        )

    def __str__(self):
        return self.recipe.name[:MAX_LENGTH_STRING]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_cart_user_recipe'
            ),
        )

    def __str__(self):
        return self.recipe.name[:MAX_LENGTH_STRING]
