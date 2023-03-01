from aiogram.fsm.state import State, StatesGroup


class VideoState(StatesGroup):
	get_video = State()
	select_mask = State()
	get_custum_mask = State()
