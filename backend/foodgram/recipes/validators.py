import re

from django.core.exceptions import ValidationError


INVALID_USERNAME_ERROR = ('Недопустимые символы в имени пользователя: '
                          '{invalid_symbols}.')


def validate_username(username):
    invalid_symbols = re.findall(r'[^\w@.+-]', username)
    if invalid_symbols:
        raise ValidationError(
            INVALID_USERNAME_ERROR.format(
                invalid_symbols=''.join(set(invalid_symbols)))
        )
    return username


def validate_hex_color(value):
    if re.match(r'^#([A-Fa-f0-9]{6})$', value):
        return value
    raise ValidationError('Пожалуйста, введите цвет в формате HEX.')
