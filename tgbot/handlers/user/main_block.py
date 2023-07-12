from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot
from tgbot.handlers.user.inline import UserMainBlockInline
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import UsersDAO

router = Router()


async def main_menu(user_id: int | str):
    text = "Здравствуйте! Это официальный бот Miner World по обмену криптовалют.\nВ этом боте вы можете продать USDT, " \
           "BTC.\nНа обмен принимаются заявки до 1000$.\nСпособ оплаты: СБП\nВ случае возникновения проблем нажмите " \
           "кнопку «поддержка»."
    kb = UserMainBlockInline.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.message(Command('start'))
async def user_start(message: Message, state: FSMContext):
    user = await UsersDAO.get_one_or_none(user_id=str(message.from_user.id))
    if not user:
        username = f"@{message.from_user.username}" if message.from_user.username else ""
        await UsersDAO.create(user_id=str(message.from_user.id), username=username)
    await state.set_state(UserFSM.home)
    await main_menu(user_id=message.from_user.id)


@router.callback_query(F.data == "home")
async def user_start(callback: CallbackQuery, state: FSMContext):
    await main_menu(user_id=callback.from_user.id)
    await state.set_state(UserFSM.home)
    await bot.answer_callback_query(callback.id)
