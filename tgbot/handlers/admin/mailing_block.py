from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router

from create_bot import bot
from .filters import AdminFilter
from tgbot.misc.states import AdminFSM
from .inline import AdminInlineKeyboard
from ...models.sql_connector import UsersDAO

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.callback_query(F.data == "mailing")
async def mailing(callback: CallbackQuery, state: FSMContext):
    text = "Введите сообщение. Оно будет сразу же отправлено всем зарегистрированным пользователям. Вы можете " \
           "использовать форматирование текста, оно будет также применено для текста"
    kb = AdminInlineKeyboard.home_kb()
    await state.set_state(AdminFSM.mailing)
    await callback.message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.mailing)
async def mailing(message: Message, state: FSMContext):
    users = await UsersDAO.get_many()
    counter = 0
    for user in users:
        try:
            await bot.send_message(chat_id=user["user_id"], text=message.html_text)
            counter += 1
        except:
            pass
    text = f"Сообщение получили {counter}/{len(users)} пользователей"
    kb = AdminInlineKeyboard.home_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)
