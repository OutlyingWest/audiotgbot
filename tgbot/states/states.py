from aiogram.dispatcher.filters.state import StatesGroup, State


class SoundStates(StatesGroup):
    get_format = State()
    get_sound = State()
