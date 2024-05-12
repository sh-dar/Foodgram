from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import (
    MAX_LENGTH_CHAR,
    MAX_LENGHT_FIELD,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_STRING,
    MIN_TIME,
    MAX_COLOR_FIELD,
)
from .validators import validate_username


class User(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGHT_FIELD,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGHT_FIELD,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGHT_FIELD,
        unique=True,
        validators=(validate_username,),
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='authors',
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='followers',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('follower', 'author'),
                name='unique_follower_author',
            ),
        )

    def __str__(self):
        return f'Пользователь {self.follower} подписан на {self.author}'


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
        validators=(
            RegexValidator(
                r'^#([A-Fa-f0-9]{6})$',
                'Пожалуйста, введите цвет в формате HEX.'
            ),
        ),
    )
    slug = models.SlugField(
        'Идентификатор тега',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGTH_STRING]


class Ingredient(models.Model):
    name = models.CharField(
        'Продукт',
        max_length=MAX_LENGHT_FIELD,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_CHAR,
    )

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        default_related_name = 'ingredients'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name[:MAX_LENGTH_STRING]} ({self.measurement_unit})'


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
    cooking_time = models.PositiveIntegerField(
        'Время (мин)',
        validators=(
            MinValueValidator(
                MIN_TIME,
                message=f'Время приготовления должно быть '
                        f'не менее {MIN_TIME} мин.'
            ),
        ),
        help_text=f'Введите время приготовления в минутах. '
                  f'Минимум: {MIN_TIME}.'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='продукты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:MAX_LENGTH_STRING]


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Мера',
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецептах'
        default_related_name = 'recipe_ingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredient_in_recipe'
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name[:MAX_LENGTH_STRING]} '
            f'({self.ingredient.measurement_unit} - {self.amount})'
        )


class UserRelatedRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_%(class)s_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user.username}: {self.recipe.name[:MAX_LENGTH_STRING]}'


class Favorite(UserRelatedRecipe):

    class Meta(UserRelatedRecipe.Meta):
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'


class ShoppingCart(UserRelatedRecipe):

    class Meta(UserRelatedRecipe.Meta):
        verbose_name = 'рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
