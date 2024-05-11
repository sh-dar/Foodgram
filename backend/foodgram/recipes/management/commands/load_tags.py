import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tags from tags.json'

    def handle(self, *args, **options):
        file_path = f'{settings.IMPORT_FOLDER}/tags.json'

        with open(file_path, 'r', encoding='utf-8') as file:
            tags = json.load(file)

            tags_to_create = []
            existing_tags = Tag.objects.values_list('name', flat=True)

            for tag in tags:
                name = tag['name']
                color = tag['color']
                slug = tag['slug']

                if name not in existing_tags:
                    tags_to_create.append(
                        Tag(name=name, color=color, slug=slug)
                    )

            with transaction.atomic():
                Tag.objects.bulk_create(tags_to_create)

        self.stdout.write(self.style.SUCCESS(
            'Теги успешно импортированы'
        ))
