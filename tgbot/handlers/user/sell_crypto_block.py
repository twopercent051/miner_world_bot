from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, ADMIN_GROUP
from tgbot.handlers.user.inline import UserSellCryptoInline
from tgbot.misc.states import UserFSM
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import TicketsDAO
from tgbot.services.get_price_api import get_usd_rub, get_coin_currency

router = Router()


async def one_coin_price(coin_title: str) -> float:
    coins = await RedisConnector.get_coins_list()
    rouble_course = await get_usd_rub()
    price = None
    for coin in coins:
        if coin["title"] == coin_title:
            if coin["type"] == "manual":
                price = coin["sell_price"]
            else:
                api_price = await get_coin_currency(coin=coin["title"])
                price = round((api_price / rouble_course * (1 - 0.01 * coin["sell_price"])), 2)
    return price


async def one_coin_wallet(coin_title: str) -> str:
    coins = await RedisConnector.get_coins_list()
    for coin in coins:
        if coin["title"] == coin_title:
            try:
                wallet = coin["wallet"]
            except KeyError:
                wallet = ""
            return wallet


@router.callback_query(F.data == "get_course")
async def get_course(callback: CallbackQuery):
    coins = await RedisConnector.get_coins_list()
    text = ["Установленные курсы валют:"]
    rouble_course = await get_usd_rub()
    for coin in coins:
        if coin["type"] == "manual":
            price = coin["sell_price"]
        else:
            api_price = await get_coin_currency(coin=coin["title"])
            price = round((api_price / rouble_course * (1 - 0.01 * coin["sell_price"])), 2)
        text.append(f"Цена продажи <b>{coin['title']}</b>: {price} ₽")
    kb = UserSellCryptoInline.home_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "operation:sell")
async def sell_crypto(callback: CallbackQuery):
    coins = await RedisConnector.get_coins_list()
    text = "Выберите валюту, которую хотите продать"
    kb = UserSellCryptoInline.sell_coins_kb(coins=coins)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "sell")
async def sell_crypto(callback: CallbackQuery, state: FSMContext):
    coin_title = callback.data.split(":")[1]
    coin_price = await one_coin_price(coin_title=coin_title)
    text = f"Мы покупаем <i>{coin_title}</i> по цене <i>{coin_price} ₽</i> Укажите количество <i>{coin_title}</i>, " \
           f"которое " \
           f"хотите обменять. Вводить можно как через запятую, так и через точку. Мы меняем на сумму, не большую " \
           f"эквивалента $1000\n\nВНИМАНИЕ! Цена продажи может быть скорректирована по рыночному курсу на момент " \
           f"окончательной подачи заявки!"
    kb = UserSellCryptoInline.home_kb()
    await state.update_data(coin_title=coin_title)
    await state.set_state(UserFSM.sell_quantity)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.sell_quantity)
async def sell_crypto(message: Message, state: FSMContext):
    try:
        quantity = float(message.text.replace(",", "."))
    except ValueError:
        text = "Введите целое или дробное число (разделитель точка либо запятая)"
        kb = UserSellCryptoInline.home_kb()
        await message.answer(text, reply_markup=kb)
        return
    state_data = await state.get_data()
    coin_title = state_data["coin_title"]
    coin_price = await one_coin_price(coin_title=coin_title)
    text = f"Вы продаёте <i>{quantity} {coin_title}</i> на общую сумму <i>{quantity * coin_price} ₽</i> Подтвердите " \
           f"заявку, и в ближайшее время с Вами свяжется наш сотрудник"
    kb = UserSellCryptoInline.sell_accept_kb()
    await state.set_state(UserFSM.home)
    await state.update_data(quantity=quantity)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "sell_accept")
async def sell_crypto(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    coin_title = state_data["coin_title"]
    quantity = state_data["quantity"]
    coin_price = await one_coin_price(coin_title=coin_title)
    wallet = await one_coin_wallet(coin_title=coin_title)
    username = f"@{callback.from_user.username}" if callback.from_user.username else ""
    user_text = [
        f"<b>Валюта:</b> <i>{coin_title}</i>",
        f"<b>Количество:</b> <i>{quantity}</i>",
        f"<b>Цена:</b> <i>{coin_price} ₽</i>",
        f"<b>Сумма:</b> <i>{quantity * coin_price} ₽</i>",
        f"<b>Кошелек для перевода:</b> <i>{wallet} ₽</i>\n",
        "Спасибо за заявку. В ближайшее время Вам напишет наш сотрудник для уточнения реквизитов"
    ]
    user_kb = UserSellCryptoInline.home_kb()
    new_ticket_id = await TicketsDAO.create(
        user_id=str(callback.from_user.id),
        username=username,
        coin=coin_title,
        quantity=quantity,
        price=coin_price,
    )
    admin_text = [
        "⚠️ НОВАЯ ЗАЯВКА",
        "Вы получили заявку на покупку",
        f"<b>Валюта:</b> <i>{coin_title}</i>",
        f"<b>Количество:</b> <i>{quantity}</i>",
        f"<b>Цена:</b> <i>{coin_price} ₽</i>",
        f"<b>Сумма:</b> <i>{quantity * coin_price} ₽</i>",
        f"<b>Username клиента:</b> <i>{username}</i>"
    ]
    admin_kb = UserSellCryptoInline.finish_ticket_kb(user_id=callback.from_user.id, ticket_id=new_ticket_id)
    await callback.message.answer("\n".join(user_text), reply_markup=user_kb)
    await bot.send_message(chat_id=ADMIN_GROUP, text="\n".join(admin_text), reply_markup=admin_kb)
    await bot.answer_callback_query(callback.id)



