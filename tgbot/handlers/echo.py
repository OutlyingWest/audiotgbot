from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from tgbot.states.states import SoundStates
from aiogram.utils.markdown import hcode

from tgbot.misc import answers


async def bot_echo_without_state(message: types.Message):
    text = [
        "Для начала используйте команду /start.",
        "Ваше сообщение:",
        message.text
    ]

    await message.answer('\n'.join(text))


async def bot_echo_get_sound(message: types.Message):
    text = [
        'Ожидается аудиофайл.',
        'Содержание вашего сообщения:',
        message.text
    ]
    await message.answer('\n'.join(text))


async def bot_echo_get_format(message: types.Message):
    text = [
        f"Ожидается формат в виде {hcode('/format')}",
        'Содержание вашего сообщения:',
        message.text
    ]
    await message.answer('\n'.join(text))


async def bot_echo_rest(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        'Случилось что-то непонятное >_<',
        'Содержание вашего сообщения:',
        message.text,
        'Состояние:',
        hcode(state_name)
    ]

    await message.answer('\n'.join(text))


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo_without_state)

    dp.register_message_handler(bot_echo_get_sound, state=SoundStates.get_sound, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(bot_echo_get_format, state=SoundStates.get_format, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(bot_echo_rest, state="*", content_types=types.ContentTypes.ANY)
