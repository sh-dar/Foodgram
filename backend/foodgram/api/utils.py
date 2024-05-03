from datetime import date


def generate_shopping_list_text(user, shopping_list, recipes):
    current_date = date.today().strftime("%d-%m-%Y")
    shopping_text = '\n'.join(
        f'{index}. {item["name"].capitalize()} - '
        f'{item["total_amount"]} '
        f'({item["measurement_unit"]})'
        for index, item in enumerate(shopping_list, start=1)
    )
    recipe_text = '\n'.join(
        f'{index}. {recipe.capitalize()}'
        for index, recipe in enumerate(recipes, start=1)
    )
    return (
        f'Дата: {current_date}\n\n'
        f'Список покупок пользователя {user}:\n{shopping_text}\n\n'
        f'Рецепты:\n{recipe_text}'
    )
