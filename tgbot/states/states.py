from aiogram.dispatcher.filters.state import StatesGroup, State


class SoundStates(StatesGroup):
    get_sound = State()
    get_format = State()
