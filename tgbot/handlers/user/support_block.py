from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, ADMIN_GROUP
from tgbot.handlers.user.inline import UserSellCryptoInline
from tgbot.misc.states import UserFSM

router = Router()


@router.callback_query(F.data.split(":")[0] == "connect")
@router.callback_query(F.data == "support")
async def support_block(callback: CallbackQuery, state: FSMContext):
    text = "Напишите текст вопроса" if callback.data == "support" else "Введите текст"
    kb = UserSellCryptoInline.home_kb()
    await state.set_state(UserFSM.support)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.support)
async def support_block(message: Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    user_text = "Сообщение отправлено"
    user_kb = UserSellCryptoInline.home_kb()
    admin_text = f"⚠️ СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ {username}:\n{message.text}"
    admin_kb = UserSellCryptoInline.connect_user_kb(user_id=message.from_user.id)
    await state.set_state(UserFSM.home)
    await message.answer(user_text, reply_markup=user_kb)
    await bot.send_message(chat_id=ADMIN_GROUP, text=admin_text, reply_markup=admin_kb)
