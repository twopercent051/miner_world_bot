import asyncio
import json
from datetime import datetime, timedelta

from tgbot.models.sql_connector import UsersDAO, TicketsDAO


def file_parser(file_name: str) -> dict:
    with open(file_name) as file:
        return json.load(file)


async def users():
    data = file_parser("users_202307140344.json")["users"]
    count = 0
    for user in data:
        username = f"@{user['nickname']}" if user['nickname'] else ""
        reg_date = datetime.fromtimestamp(user["reg_date"]) + timedelta(hours=8)
        await UsersDAO.create(
            user_id=user["user_id"],
            username=username,
            reg_dtime=reg_date
        )
        count += 1
        print(f"{count} / {len(data)}")


async def tickets():
    data = file_parser("offers_202307140344.json")["offers"]
    count = 0
    for ticket in data:
        users_list = file_parser("users_202307140344.json")["users"]
        username = ""
        for user in users_list:
            if user["user_id"] == ticket["user_id"]:
                username = f"@{user['nickname']}" if user['nickname'] else ""
                break
        reg_dtime = datetime.fromtimestamp(ticket["datetime"]) + timedelta(hours=8)
        status = "created" if ticket["is_completed"] == "False" else "finished"

        await TicketsDAO.create(
            user_id=ticket["user_id"],
            username=username,
            reg_dtime=reg_dtime,
            operation=ticket["operation"],
            coin=ticket["coin"],
            quantity=ticket["quantity"],
            price=ticket["price"],
            status=status,
            finish_dtime=reg_dtime
        )
        count += 1
        print(f"{count} / {len(data)}")


asyncio.run(tickets())
