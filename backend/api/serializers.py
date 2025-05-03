from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.constants import MAX, MIN
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import Subscription
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(max_value=MAX, min_value=MIN)
    amount = serializers.IntegerField(max_value=MAX, min_value=MIN)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class FavouriteAndShoppingCrtSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(required=False)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'author',
            'ingredients', 'tags', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited'
        ]

    def get_user(self):
        request = self.context.get('request')
        return request.user if request else None

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user and not user.is_anonymous:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user and not user.is_anonymous:
            return obj.shopping_carts.filter(user=user).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients', required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(required=False)
    cooking_time = serializers.IntegerField(max_value=MAX, min_value=MIN)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'author',
            'ingredients', 'tags', 'cooking_time',
        ]

    @staticmethod
    def _set_ingredients_and_tags(validated_data, recipe):
        ingredients = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            image=validated_data.pop('image'),
            name=validated_data.pop('name'),
            text=validated_data.pop('text'),
            cooking_time=validated_data.pop('cooking_time'), )
        self._set_ingredients_and_tags(
            validated_data,
            recipe
        )
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data

    def validate(self, value):
        tags = value.get('tags')
        ingredients = value.get('recipe_ingredients')

        if not tags:
            raise serializers.ValidationError('Необходимо выбрать тэги.')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо выбрать ингредиенты.')

        return value

    def validate_tags(self, value):

        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate_ingredients(self, value):
        ingredient_set = {}

        for item in value:
            item_tuple = tuple(sorted(item.items()))
            if item_tuple in ingredient_set:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            ingredient_set.add(item_tuple)

        return value

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        self._set_ingredients_and_tags(
            validated_data,
            instance,
        )
        return super().update(instance, validated_data)


class SubscribingSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('id',)

    def get_is_subscribed(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()

    def get_recipes(self, object):
        recipes = object.recipes.all()[:3]
        return FavouriteAndShoppingCrtSerializer(recipes, many=True).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'subscribing',)
        validators = [
            UniqueTogetherValidator(
                fields=('user', 'subscribing'),
                queryset=model.objects.all(),
                message='Вы уже подписаны на этого пользователя.',
            )
        ]

    def validate_subscribing(self, data):

        if self.context.get('request').user == data:
            raise serializers.ValidationError(
                'Вы не можете подписаться сами на себя.'
            )
        return data

    def to_representation(self, instance):
        return SubscribingSerializer(
            instance.subscribing,
            context=self.context,
        ).data


class FavouriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
        )

    def validate(self, data):
        user = self.context['request'].user
        pk = self.context['id']
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.favorites.filter(user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже был добавлен в избранное.')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        pk = self.context['id']
        recipe = get_object_or_404(Recipe, id=pk)
        favourite_item = user.favorites.create(recipe=recipe)
        return favourite_item.recipe

    def delete(self, user):
        pk = self.context['id']
        recipe = get_object_or_404(Recipe, id=pk)
        favourite = user.favorites.filter(recipe=recipe).first()
        if not favourite:
            raise serializers.ValidationError(
                'Рецепт уже был удален из избранного.')
        favourite.delete()


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id',)

    def validate(self, data):
        user = self.context['request'].user
        pk = self.context['id']
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.shopping_carts.filter(user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже был добавлен в корзину.')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        pk = self.context['id']
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart_item = user.shopping_carts.create(recipe=recipe)
        return shopping_cart_item.recipe

    def delete(self, user):
        pk = self.context['id']
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart_item = user.shopping_carts.filter(recipe=recipe).first()
        if not shopping_cart_item:
            raise serializers.ValidationError(
                'Рецепт уже был удален из корзины.')
        shopping_cart_item.delete()
