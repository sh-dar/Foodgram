import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.constants import MIN_INGREDIENT_AMOUNT as MIN_ING
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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UsersSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.follower.filter(author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'password',
        )


class FollowSerializer(UsersSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        subscription = Follow.objects.filter(
            user=user,
            author=author,
        )
        request_method = self.context.get('request').method

        if user == author:
            raise serializers.ValidationError(
                'Не нужно подписываться на самого себя')
        if request_method == 'POST' and subscription.exists():
            raise serializers.ValidationError(
                'Вы уже подписались на данного автора')
        if request_method == 'DELETE' and not subscription.exists():
            raise serializers.ValidationError(
                'Невозможно удалить несуществующую подписку')
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeLiteSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


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
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('__all__',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)

    def validate_amount(self, amount_value):
        if amount_value < MIN_ING:
            raise serializers.ValidationError(
                f'Количество ингредиентов должно быть больше {MIN_ING}.'
            )
        return amount_value


class RecipeSafeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
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
        read_only_fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        recipe = obj
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredients_in_recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(
        source='ingredients_in_recipe', many=True, required=True)
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

    def validate(self, data):
        ingredients_data = data.get('ingredients_in_recipe')
        if not ingredients_data:
            raise serializers.ValidationError(
                {'ingredients_in_recipe': 'Ингредиенты не указаны'}
            )
        ingredient_list = []
        for item in ingredients_data:
            ingredient = item['ingredients']['id']
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты в рецепте не должны повторяться')
            if not Ingredient.objects.filter(id=ingredient).exists():
                raise serializers.ValidationError(
                    'Ингредиент не существует')
            ingredient_list.append(ingredient)
        tags_data = data.get('tags')
        if not tags_data:
            raise serializers.ValidationError(
                {'tags': 'Поле тегов обязательно'}
            )
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError('Теги не должны повторяться')
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_in_recipe')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        self.create_tags(recipe, tags)
        return recipe

    def create_ingredients(self, recipe, ingredients):
        ingredients_in_recipe = []
        for item in ingredients:
            ingredient = IngredientRecipe(
                recipe=recipe,
                ingredient_id=item['ingredients']['id'],
                amount=item['amount'],
            )
            ingredients_in_recipe.append(ingredient)
        IngredientRecipe.objects.bulk_create(ingredients_in_recipe)

    def create_tags(self, recipe, tags):
        recipe.tags.set(tags)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_in_recipe')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        self.create_tags(instance, tags)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSafeSerializer(instance, context=context).data


class BaseRecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('user', 'recipe')

    def validate(self, data):
        recipe = data.get('recipe')
        user = self.context.get('request').user
        if self.Meta.model.objects.filter(user=user,
                                          recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже существует')
        if not Recipe.objects.filter(id=recipe.id).exists():
            raise serializers.ValidationError('Рецепт не существует')
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['recipe'] = RecipeLiteSerializer(instance.recipe).data
        return representation['recipe']


class FavoriteSerializer(BaseRecipeSerializer):
    class Meta(BaseRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseRecipeSerializer):
    class Meta(BaseRecipeSerializer.Meta):
        model = ShoppingCart
