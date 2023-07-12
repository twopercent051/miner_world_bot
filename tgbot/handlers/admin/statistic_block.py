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
from ...models.sql_connector import TicketsDAO, UsersDAO
from ...services.xlsx_create import create_excel

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.callback_query(F.data == "statistic")
async def statistic(callback: CallbackQuery):
    text = []
    for i in [1, 7, 30]:
        start_date = datetime.utcnow() + timedelta(hours=8) - timedelta(days=i)
        created_tickets = await TicketsDAO.get_many_by_date(start_date=start_date, status="created")
        finished_tickets = await TicketsDAO.get_many_by_date(start_date=start_date, status="finished")
        users = await UsersDAO.get_many_by_date(start_date=start_date)
        text_list = [
            f"<u>Данные за {i} дней:</u>",
            f'Зарегистрировались {len(users)} новых пользователей',
            f'Получили {created_tickets["count"] + finished_tickets["count"]} заявок на продажу'
            f' {created_tickets["sum"] + finished_tickets["sum"]} ₽',
            f'Завершили {finished_tickets["count"]} заявок на продажу {finished_tickets["sum"]} ₽\n',
        ]
        text.extend(text_list)
    kb = AdminTicketsInline.home_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)

