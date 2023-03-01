import os
from typing import Union
from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, ContentType as CT
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

from state import VideoState
from settings import settings
from round_video import RoundVideo

router = Router()


# Функция для создания inline кнопок
def inline_keyboard(items: Union[dict, list], row = 1) -> InlineKeyboardMarkup:
	row_num: int = 0
	key_num: int = 0
	key_len: int = len(items.keys())
	buttons: list = []
	ram: list = []

	for it in items:
		text = it
		value = items[it]

		button = InlineKeyboardButton(
				text=text,
				callback_data=value
			)
		
		if row is not None:
			ram.append(button)
			row_num += 1
			if row_num >= row or key_num+1 >= key_len:
				buttons.append(ram)
				ram = []
				row_num = 0
		
		else:
			buttons.append([button])

		key_num += 1

	return InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)


def get_size(file_path, unit='mb'):
	file_size = os.path.getsize(file_path)
	exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
	if unit not in exponents_map:
		raise ValueError("Must select from \
		['bytes', 'kb', 'mb', 'gb']")
	else:
		size = file_size / 1024 ** exponents_map[unit]
		return round(size, 3)



@router.message(Command(commands=["start"]))
async def cmd_send_welcome(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	keyboard = inline_keyboard({"Создать видео": "new_video"})

	await message.answer("Выберите интересующий вас раздел", reply_markup=keyboard)


@router.callback_query(StateFilter(None))
async def check_sub(callback: CallbackQuery, bot: Bot, state: FSMContext):
	if callback.data == "new_video":
		await state.set_state(VideoState.get_video)
		await callback.message.edit_text("Пришлите мне видео файл (размером не более 20 МБ)")



@router.message(StateFilter(VideoState.get_video))
async def get_video(message: Message, bot: Bot, state: FSMContext):
	try:
		file_id = message.video.file_id
		message = await message.answer("Получения видео ...")

		file = await bot.get_file(file_id)
		keyboard = inline_keyboard({"Получить видео": "get_round_video", "Добавить свою маску": "custum_mask"})

		await bot.download_file(file.file_path, f"{settings.BASE_DIR}/video_cache/cache_video_tg.mp4") 
		await state.set_state(VideoState.select_mask)
		await message.edit_text("Выберите желаемый результат", reply_markup=keyboard)

	except Exception as e:
		print(e)
		await message.edit_text("Размер файла более 20 МБ, Пришлите мне другой файл")


@router.callback_query(StateFilter(VideoState.select_mask))
async def select_mask_p(callback: CallbackQuery, bot: Bot, state: FSMContext):
	if callback.data == "get_round_video":
		start_time = datetime.now()
		await callback.message.edit_text("Процесс создания видео запущен, после создания видео бот пришлёт вам его")

		RoundVideo(False, '').round_video('video_cache/cache_video_tg.mp4')
		video = FSInputFile( f"{settings.BASE_DIR}/result_videos/video_au.mp4")
		f_size = get_size(f"{settings.BASE_DIR}/result_videos/video_au.mp4")

		if f_size <= 17:await bot.send_video_note(callback.message.chat.id, video)
		else:await bot.send_video(callback.message.chat.id, video)
		
		print(datetime.now() - start_time)

	elif callback.data == "custum_mask":
		await callback.message.edit_text("Пришлите мне маску для видео")
		await state.set_state(VideoState.get_custum_mask) 


@router.message(StateFilter(VideoState.get_custum_mask), F.content_type.in_([CT.PHOTO]))
async def create_custum_mask(message: Message, bot: Bot, state: FSMContext):
	await message.answer("Процесс создания видео запущен, после создания видео бот пришлёт вам его")

	try:
		file_id = message.photo[-1].file_id
		file = await bot.get_file(file_id)
		await bot.download_file(file.file_path, f"{settings.BASE_DIR}/video_cache/custum_mask.jpg") 

		RoundVideo(True, f"{settings.BASE_DIR}/video_cache/custum_mask.jpg"
			).round_video('video_cache/cache_video_tg.mp4'
		)

		video = FSInputFile( f"{settings.BASE_DIR}/result_videos/video_au.mp4")
		f_size = get_size(f"{settings.BASE_DIR}/result_videos/video_au.mp4")

		if f_size <= 17:await bot.send_video_note(message.chat.id, video)
		else:await bot.send_video(message.chat.id, video)

	except Exception as e:
		print(e)
		await message.answer("Размер файла слишком велик для видео заметки")
