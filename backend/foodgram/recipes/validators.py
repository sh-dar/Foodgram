import re

from django.core.exceptions import ValidationError

from .constants import MIN_INGREDIENT_AMOUNT as MIN_ING


INVALID_USERNAME_ERROR = ('Недопустимые символы в имени пользователя: '
                          '{invalid_symbols}.')


def validate_username(username):
    invalid_symbols = set(re.findall(r'[^\w@.+-]', username))
    if invalid_symbols:
        raise ValidationError(
            INVALID_USERNAME_ERROR.format(
                invalid_symbols=''.join(invalid_symbols))
        )
    return username


def validate_hex_color(value):
    if not re.match(r'^#([A-Fa-f0-9]{6})$', value):
        raise ValidationError('Пожалуйста, введите цвет в формате HEX.')
