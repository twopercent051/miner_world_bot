from typing import Literal

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router

from create_bot import bot
from .filters import AdminFilter
from tgbot.misc.states import AdminFSM
from tgbot.models.redis_connector import RedisConnector
from .inline import AdminEditionBlockInline

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


def get_coin_value(coin: dict, key: Literal["sell_price", "wallet"]) -> int | str:
    try:
        return coin[key]
    except KeyError:
        if key == "wallet":
            return ""
        else:
            return 0


async def row_parser(message: Message, key: Literal["sell_price", "wallet"], state: FSMContext) -> dict:
    rows = message.text.split("\n")
    for row in rows:
        try:
            coin = row.split("|")[0].strip()
            value = row.split("|")[1].strip()
            if key != "wallet":
                value = float(value.replace(",", "."))
            data = {"title": coin, key: value}
        except ValueError:
            return
        if data:
            await RedisConnector.update_coins_list(data)
    text = "Данные обновлены"
    await message.answer(text)
    coins = await RedisConnector.get_coins_list()
    text = []
    for coin in coins:
        price = get_coin_value(coin=coin, key=key)
        row = f"{coin['title']} | {price}"
        text.append(row)
    kb = AdminEditionBlockInline.home_kb()
    await state.set_state(AdminFSM.home)
    await message.answer("\n".join(text), reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "edit")
async def edition_block(callback: CallbackQuery, state: FSMContext):
    clb_data = callback.data.split(":")[1]
    if clb_data == "coins":
        text = "Что редактируем?"
        kb = AdminEditionBlockInline.edition_menu_kb()
    elif clb_data == "price":
        text = "Текущий курс, по которому вы <u>покупаете</u> валюту у клиентов. Для USDT указана цена в рублях за " \
               "покупку, для остальных монет указано отклонение от рыночной цены в процентах 👇. Скопируйте одну или " \
               "несколько строк, замените значения и отправьте сообщение обратно боту"
        await callback.message.answer(text)
        coins = await RedisConnector.get_coins_list()
        text = []
        for coin in coins:
            price = get_coin_value(coin=coin, key="sell_price")
            row = f"{coin['title']} | {price}"
            text.append(row)
        text = "\n".join(text)
        kb = AdminEditionBlockInline.home_kb()
        await state.set_state(AdminFSM.get_price)
    elif clb_data == "wallet":
        text = "Текущие номера кошельков, на которые вы получаете переводы. Скопируйте одну или " \
               "несколько строк, замените значения и отправьте сообщение обратно боту"
        await callback.message.answer(text)
        coins = await RedisConnector.get_coins_list()
        text = []
        for coin in coins:
            wallet = get_coin_value(coin=coin, key="wallet")
            row = f"{coin['title']} | {wallet}"
            text.append(row)
        text = "\n".join(text)
        kb = AdminEditionBlockInline.home_kb()
        await state.set_state(AdminFSM.get_wallet)
    else:
        return
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.get_price)
async def get_price(message: Message, state: FSMContext):
    await row_parser(message=message, key="sell_price", state=state)


@router.message(F.text, AdminFSM.get_wallet)
async def get_wallet(message: Message, state: FSMContext):
    await row_parser(message=message, key="wallet", state=state)
