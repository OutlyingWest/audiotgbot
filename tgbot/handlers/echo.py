from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode


async def bot_echo_without_state(message: types.Message):
    text = [
        "Для начала используйте команду /start.",
        "Ваше сообщение:",
        message.text
    ]

    await message.answer('\n'.join(text))


async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    print('state_name:', state_name)
    if state_name == 'get_sound':
        text = [
            'Ожидается аудиофайл.',
            'Содержание вашего сообщения:',
            message.text
        ]

    elif state_name == 'get_format':
        text = [
            f'Ожидается формат в виде {hcode("/format")}',
            'Содержание вашего сообщения:',
            message.text
        ]

    else:
        text = [
            'Случилось что-то непонятное >_<',
            'Содержание вашего сообщения:',
            message.text
        ]
        print(text)

    await message.answer('\n'.join(text))


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo_without_state)
    dp.register_message_handler(bot_echo_all, state="*", content_types=types.ContentTypes.ANY)
