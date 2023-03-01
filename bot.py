from asyncio import run

from aiogram import Bot, Dispatcher

from settings import settings
from main_handler import router

async def main():
	bot = Bot(settings.TELEGRAM_TOKEN)
	dp = Dispatcher()

	dp.include_router(router)
	
	print("BOT WORKS")
	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)


if __name__ == '__main__':
	try:
		run(main())

	except KeyboardInterrupt:
		print("\n@GoodBye :)")