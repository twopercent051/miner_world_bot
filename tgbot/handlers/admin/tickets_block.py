import os
from datetime import datetime, timedelta
from typing import Literal

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router

from create_bot import bot, ADMIN_GROUP
from .filters import AdminFilter
from tgbot.misc.states import AdminFSM
from .inline import AdminTicketsInline
from ...models.sql_connector import TicketsDAO
from ...services.xlsx_create import create_excel

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


async def file_render(status: Literal["created", "all"]):
    if status == "created":
        tickets_list = await TicketsDAO.get_many(status="created")
    else:
        tickets_list = await TicketsDAO.get_many()
    await create_excel(ticket_list=tickets_list, status_file=status)
    file = FSInputFile(path=f'{os.getcwd()}/{status}_tickets.xlsx', filename=f"{status}_tickets.xlsx")
    await bot.send_document(chat_id=ADMIN_GROUP, document=file)
    os.remove(f'{os.getcwd()}/{status}_tickets.xlsx')


@router.callback_query(F.data == "tickets")
async def tickets(callback: CallbackQuery, state: FSMContext):
    await file_render(status="created")
    await file_render(status="all")
    text = "Для получения информации по заявке введите ее номер"
    kb = AdminTicketsInline.home_kb()
    await state.set_state(AdminFSM.tickets)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.tickets)
async def tickets(message: Message):
    kb = AdminTicketsInline.home_kb()
    if message.text.isdigit():
        ticket = await TicketsDAO.get_one_or_none(id=int(message.text))
        if ticket:
            if ticket["status"] == "created":
                status = "🟩 Новая"
                kb = AdminTicketsInline.finish_ticket_kb(user_id=ticket["user_id"], ticket_id=ticket["id"])
            else:
                status = "🟥 Завершённая"
                kb = AdminTicketsInline.connect_user_kb(user_id=ticket["user_id"])
            text = [
                f"<u>ЗАЯВКА № {ticket['id']}</u>",
                f"<b>Валюта:</b> <i>{ticket['coin']}</i>",
                f"<b>Количество:</b> <i>{ticket['quantity']}</i>",
                f"<b>Цена:</b> <i>{ticket['price']} ₽</i>",
                f"<b>Сумма:</b> <i>{ticket['quantity'] * ticket['price']} ₽</i>",
                f"<b>Username клиента:</b> <i>{ticket['username']}</i>",
                f"<b>Статус:</b> <i>{status}</i>"
            ]
            text = "\n".join(text)
        else:
            text = "По вашему запросу ничего не найдено 🤷"
    else:
        text = "Введите целое число или вернитесь в главное меню"
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "finish_ticket")
async def tickets(callback: CallbackQuery):
    ticket_id = int(callback.data.split(":")[1])
    now = datetime.utcnow() + timedelta(hours=8)
    ticket = await TicketsDAO.get_one_or_none(id=ticket_id)
    text = [
        f"<u>ЗАЯВКА № {ticket['id']}</u>",
        f"<b>Валюта:</b> <i>{ticket['coin']}</i>",
        f"<b>Количество:</b> <i>{ticket['quantity']}</i>",
        f"<b>Цена:</b> <i>{ticket['price']} ₽</i>",
        f"<b>Сумма:</b> <i>{ticket['quantity'] * ticket['price']} ₽</i>",
        f"<b>Username клиента:</b> <i>{ticket['username']}</i>",
        f"<b>Статус:</b> <i>🟥 Завершённая</i>"
    ]
    text = "\n".join(text)
    await TicketsDAO.update_by_id(
        item_id=ticket_id,
        status="finished",
        finish_dtime=now
    )
    kb = AdminTicketsInline.connect_user_kb(user_id=callback.from_user.id)
    await callback.message.edit_text(reply_markup=kb, text=text)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "connect")
async def connect(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split(":")[1]
    text = "Напишите текст для ответа клиенту. Форматирование текста будет сохранено"
    kb = AdminTicketsInline.home_kb()
    await state.set_state(AdminFSM.connect)
    await state.update_data(user_id=user_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.connect)
async def connect(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data["user_id"]
    admin_text = "Сообщение отправлено"
    admin_kb = AdminTicketsInline.home_kb()
    user_kb = await AdminTicketsInline.connect_user_kb(user_id=ADMIN_GROUP)
    await bot.send_message(chat_id=user_id, text=message.html_text, reply_markup=user_kb)
    await message.answer(admin_text, reply_markup=admin_kb)

