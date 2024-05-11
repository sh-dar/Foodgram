import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from ingredients.json'

    def handle(self, *args, **options):
        file_path = f'{settings.IMPORT_FOLDER}/ingredients.json'

        with open(file_path, 'r', encoding='utf-8') as file:
            ingredients = json.load(file)

            ingredients_to_create = []
            existing_ingredients = Ingredient.objects.values_list(
                'name',
                flat=True
            )

            for ingredient in ingredients:
                name = ingredient['name']
                measurement_unit = ingredient['measurement_unit']

                if name not in existing_ingredients:
                    ingredients_to_create.append(
                        Ingredient(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    )

            with transaction.atomic():
                Ingredient.objects.bulk_create(ingredients_to_create)

        self.stdout.write(self.style.SUCCESS(
            'Продукты успешно импортированы'
        ))
