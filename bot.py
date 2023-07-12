import asyncio

from tgbot.handlers.echo import router as echo_router
from tgbot.handlers.admin.main_block import router as admin_main_block
from tgbot.handlers.admin.edition_block import router as admin_edition_block
from tgbot.handlers.admin.mailing_block import router as admin_mailing_block
from tgbot.handlers.admin.tickets_block import router as admin_tickets_block
from tgbot.handlers.admin.statistic_block import router as admin_statistic_block
from tgbot.handlers.user.main_block import router as user_main_block
from tgbot.handlers.user.sell_crypto_block import router as user_sell_crypto_block
from tgbot.misc.scheduler import scheduler_jobs
from tgbot.models.redis_connector import RedisConnector as rds

from create_bot import bot, dp, scheduler, logger, register_global_middlewares, config


admin_router = [
    admin_main_block,
    admin_edition_block,
    admin_mailing_block,
    admin_tickets_block,
    admin_statistic_block
]


user_router = [
    user_main_block,
    user_sell_crypto_block
]


async def main():
    logger.info("Starting bot")
    scheduler_jobs()
    rds.redis_start()
    dp.include_routers(
        *admin_router,
        *user_router,
        echo_router
    )

    try:
        scheduler.start()
        register_global_middlewares(dp, config)
        # await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        scheduler.shutdown(True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
