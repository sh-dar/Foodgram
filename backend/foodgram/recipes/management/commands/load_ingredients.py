import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from ingredients.json'

    def handle(self, *args, **options):
        file_path = '../../data/ingredients.json'

        with open(file_path, 'r', encoding='utf-8') as file:
            ingredients = json.load(file)

            for ingredient in ingredients:
                name = ingredient['name']
                measurement_unit = ingredient['measurement_unit']

                ingredient, created = Ingredient.objects.update_or_create(
                    name=name,
                    defaults={'measurement_unit': measurement_unit}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Добавлен ингредиент: {ingredient.name}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Ингредиент уже существует: {ingredient.name}'
                    ))
