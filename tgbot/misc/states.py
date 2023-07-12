from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    get_price = State()
    get_wallet = State()
    mailing = State()
    tickets = State()
    connect = State()


class UserFSM(StatesGroup):
    home = State()
    sell_quantity = State()
    support = State()
