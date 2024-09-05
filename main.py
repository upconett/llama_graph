import asyncio

from create_bot import bot, dp
from handling import router as handling


async def on_startup():
    buser = await bot.get_me()
    print(f'\n✅ Bot @{buser.username} online\n')

async def on_shutdown(): 
    buser = await bot.get_me()
    print(f'\n💤 Bot @{buser.username} shutting down...\n')


async def main():
    buser = await bot.get_me()
    print(f'⌛ Starting bot @{buser.username}...')

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(handling)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
