from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram import F

import app.keyboards.main as main_keyboard

import app.database.requests as requests

main_router = Router()


@main_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await requests.set_user(message.from_user.id)

    content = f"Здравствуйте, {message.from_user.full_name}!\n" \
              f"Я - бот технической поддержки Акросс.\n" \
              f"Пожалуйста, выберите пункт из меню ниже 🔽"
              
    await message.answer(content, reply_markup=main_keyboard.main())


@main_router.callback_query(F.data == "main")
async def main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    content = f"Пожалуйста, выберите пункт из меню ниже 🔽"
              
    await callback.message.edit_text(content,
                                     reply_markup=main_keyboard.main())