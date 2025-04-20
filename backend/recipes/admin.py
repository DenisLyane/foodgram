from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    empty_value_display = '-отсутствует-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-отсутствует-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-отсутствует-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
