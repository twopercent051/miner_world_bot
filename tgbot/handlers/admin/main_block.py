from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, ADMIN_GROUP
from .filters import AdminFilter
from tgbot.misc.states import AdminFSM
from .inline import AdminMainBlockInline

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


async def main_menu_msg(user_id: str | int, state: FSMContext):
    text = "Главное меню"
    kb = AdminMainBlockInline.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)
    await state.set_state(AdminFSM.home)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await main_menu_msg(user_id=ADMIN_GROUP, state=state)


@router.callback_query(F.data == "home")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await main_menu_msg(user_id=ADMIN_GROUP, state=state)
    await bot.answer_callback_query(callback.id)
