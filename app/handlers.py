from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F

import app.keyboards as keyboards
import app.database.requests as requests
import app.send_request as send_request

router = Router()

class Request(StatesGroup):
    region = State()
    medical_organization = State()
    name = State()
    position = State()
    phone = State()
    request_type = State()
    request_description = State()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await requests.set_user(message.from_user.id)

    content = f"Здравствуйте, {message.from_user.full_name}!\n" \
              f"Я - бот технической поддержки Акросс.\n" \
              f"Пожалуйста, выберите пункт из меню ниже 🔽"
              
    await message.answer(content, reply_markup=keyboards.main_keyboard())


@router.callback_query(F.data == "main")
async def main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    content = f"Пожалуйста, выберите пункт из меню ниже 🔽"
              
    await callback.message.edit_text(content,
                                     reply_markup=keyboards.main_keyboard())


@router.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery) -> None:
    content = "Телефон тех. поддержки: +78007070572 \n" \
              "Адрес электронной почты: support@across.ru"
    
    await callback.message.edit_text(content,
                                     reply_markup=keyboards.back_to_main_keyboard())


@router.callback_query(F.data == "make_request")
async def make_request(callback: CallbackQuery, state: FSMContext) -> None:
    content = "⚠️ ВНИМАНИЕ ⚠️\nЗаявки на доработку функционала, разработку " \
              "нового функционала, заявки на изменение состава пользователей " \
              "и их настроек доступа, а также на подключение нового " \
              "оборудования можно передать <b>ТОЛЬКО</b> письмом на почту " \
              "support@across.ru"
    
    user_data = await requests.get_user(callback.from_user.id)

    if user_data[0] and user_data[1] and user_data[2] and user_data[3] and user_data[4]:
        await callback.message.edit_text(content, parse_mode="HTML",
                                     reply_markup=keyboards.found_user_confirmation_keyboard())
    else:
        await callback.message.edit_text(content, parse_mode="HTML",
                                     reply_markup=keyboards.confirmation_keyboard())


@router.callback_query(F.data == "further")
async def futher(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.region)

    content = "Укажите Ваш регион 🌍🌎🌏 из списка внизу 🔽"

    await callback.message.edit_text(content,
                                     parse_mode="HTML",
                                     reply_markup=keyboards.region_keyboard())


@router.callback_query(Request.region)
async def region_state(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"region": callback.data})
    await requests.update_user(callback.from_user.id, region=callback.data)
    await state.set_state(Request.medical_organization)

    content = "Выберите Вашу медицинскую организацию 🏥"

    await callback.message.answer(content,
                                  reply_markup=keyboards.medical_organization_keyboard())


@router.callback_query(Request.medical_organization)
async def organization(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"medical_organization": str(callback.data)})
    await requests.update_user(callback.from_user.id, medical_organization=callback.data)
    await state.set_state(Request.name)

    content = "Напишите Ваше ФИО 🛂"

    await callback.message.answer(content,
                                  reply_markup=keyboards.back_to_main_keyboard())


@router.message(Request.name)
async def name(message: Message, state: FSMContext) -> None:
    await state.update_data({"name": message.text})
    await requests.update_user(message.from_user.id, name=message.text)
    await state.set_state(Request.position)

    content = "Напишите Вашу должность 👨‍⚕️👩‍⚕️"

    await message.answer(content,
                         reply_markup=keyboards.back_to_main_keyboard())


@router.message(Request.position)
async def position(message: Message, state: FSMContext) -> None:
    await state.update_data({"position": message.text})
    await requests.update_user(message.from_user.id, position=message.text)
    await state.set_state(Request.phone)

    content = "Напишите Ваш контактный телефон 📱"

    await message.answer(content,
                         reply_markup=keyboards.back_to_main_keyboard())


@router.message(Request.phone)
async def phone(message: Message, state: FSMContext) -> None:
    if len(message.text) != 11:
        content = "Некорректный номер телефона 🚫"

        return await message.answer(content)
    else:
        await state.update_data({"phone": message.text})
        await requests.update_user(message.from_user.id, phone=message.text)
        await state.set_state(Request.request_type)

        content = "Выберите тип заявки 📝"

        await message.answer(content,
                             reply_markup=keyboards.issue_type_keyboard())
        

@router.callback_query(F.data == "found_user_further")
async def found_user_further(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.request_type)

    content = "Выберите тип заявки 📝"

    await callback.message.edit_text(content,
                                     reply_markup=keyboards.issue_type_keyboard())


@router.callback_query(Request.request_type)
async def request_type(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"request_type": callback.data})
    await state.set_state(Request.request_description)

    if callback.data == "critical":
        content = "Опишите проблему 📝"
    elif callback.data == "no_exchange":
        content = "Опишите проблему 📝 и предоставьте ШК ЛИС или ИДМИС"
    elif callback.data == "no_connection":
        content = "Напишите наименование анализатора, ШК ЛИС и предоставьте " \
                  "описание проблемы 📝"
    elif callback.data == "other":
        content = "Подробно опишите Вашу проблему 📝"
        
    await callback.message.answer(content,
                                  reply_markup=keyboards.back_to_main_keyboard())


@router.message(Request.request_description)
async def request_description(message: Message, state: FSMContext) -> None:
    message_content = message.photo if message.photo else message.text
    await state.update_data({"request_description": message_content})

    content = "Ваша заявка принята ✅"

    user_data = await requests.get_user(message.from_user.id)
    fsm_user_data = await state.get_data()

    await send_request.send_request(user_data[0],
                                user_data[1],
                                user_data[2],
                                user_data[3],
                                user_data[4],
                                fsm_user_data["request_type"],
                                fsm_user_data["request_description"])

    await state.clear()

    await message.answer(content,
                         reply_markup=keyboards.back_to_main_keyboard())


@router.callback_query(F.data == "request_status")
async def request_status(callback: CallbackQuery) -> None:
    content = "Данная функция пока недоступна 🙁"

    await callback.message.edit_text(content,
                                     reply_markup=keyboards.back_to_main_keyboard())


@router.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery) -> None:
    content = "Данная функция пока недоступна 🙁"

    await callback.message.edit_text(content,
                                     reply_markup=keyboards.back_to_main_keyboard())