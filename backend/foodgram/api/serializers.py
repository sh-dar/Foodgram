from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.constants import MIN_INGREDIENT_AMOUNT as MIN_ING
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)

User = get_user_model()


class UsersSerializer(DjoserUserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (*DjoserUserSerializer.Meta.fields, 'is_subscribed',)

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return not (
            user.is_anonymous or user == author
        ) and Follow.objects.filter(
            author=author,
            follower=user
        ).exists()


class FollowSerializer(UsersSerializer):
    recipes = SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UsersSerializer.Meta):
        fields = (
            *UsersSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def validate(self, data):
        follower = self.context.get('request').user
        author = self.instance
        subscription = Follow.objects.filter(
            follower=follower,
            author=author,
        )
        request_method = self.context.get('request').method

        if follower == author:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя')
        if request_method == 'POST' and subscription.exists():
            raise serializers.ValidationError(
                'Вы уже подписались на данного автора')
        if request_method == 'DELETE' and not subscription.exists():
            raise serializers.ValidationError(
                'Невозможно удалить несуществующую подписку')
        return data

    def get_recipes(self, user):
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 10**10))
        return RecipeLiteSerializer(
            user.recipes.all()[:limit],
            many=True,
            read_only=True
        ).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeLiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('__all__',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    amount = serializers.IntegerField(min_value=MIN_ING)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount',)


class RecipeSafeSerializer(serializers.ModelSerializer):
    author = DjoserUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'tags',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return not user.is_anonymous and \
            user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return not user.is_anonymous and \
            user.shoppingcarts.filter(recipe=recipe).exists()


class RecipeSerializer(serializers.ModelSerializer):
    author = DjoserUserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'ingredients',
            'tags',
            'image',
            'text',
            'cooking_time',
        )

    @staticmethod
    def check_duplicates(items, field_name):
        duplicates = [item for item in items if items.count(item) > 1]
        if duplicates:
            raise serializers.ValidationError(
                f'{field_name} не должны повторяться: {duplicates}'
            )

    def validate(self, data):
        ingredients_data = data.get('recipe_ingredients')
        tags_data = data.get('tags')

        if not ingredients_data:
            raise serializers.ValidationError(
                {'recipe_ingredients': 'Продукты не указаны'}
            )
        if not tags_data:
            raise serializers.ValidationError(
                {'tags': 'Поле тегов обязательно'}
            )

        ingredient_list = [
            item['ingredients']['id'] for item in ingredients_data
        ]
        non_existing_ingredients = [
            ingredient for ingredient in ingredient_list
            if not Ingredient.objects.filter(id=ingredient).exists()
        ]
        if non_existing_ingredients:
            raise serializers.ValidationError(
                f'Следующие продукты не существуют: {non_existing_ingredients}'
            )

        self.check_duplicates(ingredient_list, 'Продукты')
        self.check_duplicates(tags_data, 'Теги')
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле "image" не может быть пустым.'
            )
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredients.objects.bulk_create(
            RecipeIngredients(
                recipe=recipe,
                ingredient_id=item['ingredients']['id'],
                amount=item['amount'],
            ) for item in ingredients)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSafeSerializer(
            instance,
            context=self.context
        ).data


class RecipeRelationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('user', 'recipe')

    def validate_recipe(self, recipe):
        user = self.context.get('request').user
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен в список')
        if not Recipe.objects.filter(id=recipe.id).exists():
            raise serializers.ValidationError('Указанный рецепт не существует')
        return recipe

    def to_representation(self, instance):
        return RecipeLiteSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(RecipeRelationSerializer):
    class Meta(RecipeRelationSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(RecipeRelationSerializer):
    class Meta(RecipeRelationSerializer.Meta):
        model = ShoppingCart
