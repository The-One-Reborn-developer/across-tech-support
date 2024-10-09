from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)


def confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Понятно 👍',
                    callback_data='further'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад в главное меню ◀️',
                    callback_data='main'
                )
            ]
        ]
    )