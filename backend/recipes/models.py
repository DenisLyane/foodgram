from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=32, unique=True)
    slug = models.SlugField(
        'Уникальный слаг', max_length=32, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингридиента', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.IntegerField('Количество в рецепте',)

    class Meta:
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )

    class Meta:

        verbose_name = 'Рецепт-тег'
        verbose_name_plural = 'Рецепты-теги'


class Recipe(models.Model):
    name = models.CharField('Название', max_length=256)
    image = models.ImageField(
        'Изображениe',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField('Описание рецепта')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredient,
        blank=False,
        verbose_name='Список ингридиентов',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        through=RecipeTag,
        blank=False,
        verbose_name='Список тэгов',
        related_name='recipes',
    )
    cooking_time = models.IntegerField('Время приготовления',)
    short_link = models.URLField(
        max_length=6, unique=True, blank=True, null=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.short_link:
            self.short_link = str(self.pk)
            self.save(update_fields=['short_link'])

    def __str__(self):
        return self.name


class Favourite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
    )

    class Meta:

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_carts',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_carts',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
