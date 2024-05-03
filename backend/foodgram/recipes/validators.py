import re

from django.core.exceptions import ValidationError

from .constants import MIN_VALUE


def validate_username(value):
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError('Имя пользователя должно состоять '
                              'только из букв латинского алфавита, '
                              'цифр и следующих специальных символов: '
                              '"@", ".", "-", "+". '
                              'Допустимы также символы подчеркивания.')


def validate_hex_color(value):
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$', value):
        raise ValidationError('Пожалуйста, введите цвет в формате HEX.')


def validate_amount(value):
    if int(value) < MIN_VALUE:
        raise ValidationError(
            f'Минимальное количество продукта: {MIN_VALUE}.'
        )
