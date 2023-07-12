import redis
import json

from create_bot import config, logger


default_coins = [
    {
        "title": "BTC",
        "type": "auto",
    },
    {
        "title": "USDT",
        "type": "manual",
    },
    {
        "title": "LTC",
        "type": "auto",
    },
    {
        "title": "DOGE",
        "type": "auto",
    },
]


class RedisConnector:
    r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)

    @classmethod
    def redis_start(cls):
        response = cls.r.get("coins")
        if not response:
            cls.r.set("coins", json.dumps(default_coins))
            logger.info("Coins created")
        logger.info('Redis connected OKK')

    @classmethod
    async def update_coins_list(cls, coin_data: dict):
        coins = await cls.get_coins_list()
        result = []
        for coin in coins:
            if coin["title"] == coin_data["title"]:
                for k in coin_data.keys():
                    coin[k] = coin_data[k]
            result.append(coin)
        cls.r.set('coins', json.dumps(result))

    @classmethod
    async def get_coins_list(cls) -> list:
        response = cls.r.get('coins').decode('utf=8')
        coins = json.loads(response)
        return coins
