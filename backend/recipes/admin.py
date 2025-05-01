from django.contrib import admin

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)


class TagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_ingredients', 'get_tags')
    search_fields = ('author__username', 'name',)
    list_filter = ('tags',)
    empty_value_display = '-отсутствует-'
    inlines = [IngredientInline, TagInline]

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    empty_value_display = '-отсутствует-'


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)
    search_fields = ('recipe__name', 'tag__name',)
    empty_value_display = '-отсутствует-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)
    empty_value_display = '-отсутствует-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    empty_value_display = '-отсутствует-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-отсутствует-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-отсутствует-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
