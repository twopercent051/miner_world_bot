from openpyxl import Workbook
from openpyxl.styles import Font
import os


async def create_excel(ticket_list: list, status_file: str):
    wb = Workbook()
    ws = wb.active
    ws.append(
        (
            'Номер',
            'ID пользователя',
            'Username пользователя',
            'Дата-время регистрации',
            "Тип операции",
            "Валюта",
            "Количество",
            "Цена",
            "Сумма",
            "Статус",
            "Дата-время завершения",
        )
    )
    ft = Font(bold=True)
    for row in ws['A1:T1']:
        for cell in row:
            cell.font = ft

    for ticket in ticket_list:
        reg_dtime = ticket["reg_dtime"].strftime("%d.%m.%Y %H:%M")
        username = "---" if ticket["username"] == "" else ticket["username"]
        operation = "Продажа" if ticket["operation"] == "sell" else "Покупка"
        status = "Создано" if ticket["status"] == "created" else "Завершено"
        finished_dtime = ticket["finish_dtime"].strftime("%d.%m.%Y %H:%M") if ticket["finish_dtime"] else "---"
        ws.append(
            (
                ticket['id'],
                ticket["user_id"],
                username,
                reg_dtime,
                operation,
                ticket["coin"],
                ticket["quantity"],
                ticket["price"],
                ticket["quantity"] * ticket["price"],
                status,
                finished_dtime
            )
        )

    wb.save(f'{os.getcwd()}/{status_file}_tickets.xlsx')
