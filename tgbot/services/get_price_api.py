import aiohttp
import json


async def get_usd_rub() -> float:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.cbr-xml-daily.ru/latest.js') as resp:
            response = await resp.read()
        data = json.loads(response)
    return data['rates']['USD']


async def get_coin_currency(coin: str) -> float:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api1.binance.com/api/v3/ticker/price?symbol={coin}USDT') as resp:
            response = await resp.read()
        data = json.loads(response)['price']
    return float(data)
