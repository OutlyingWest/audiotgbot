from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.dispatcher import FSMContext

from tgbot.states.states import SoundStates
from tgbot.misc import commands
from tgbot.handlers.users.manage import logic
from tgbot.data.database.handler import SQLiteHandler


async def user_start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    print(user_id)
    print(first_name)
    await message.reply("Hello, user!")
    # Creation of a database connection to add usr name and tg-id
    sql_handler = SQLiteHandler(message)
    # Insert user data to table "users"
    sql_handler.insert_to_exiting_table('users', telegram_id=user_id, first_user_name=first_name)
    await SoundStates.get_format.set()


async def choose_format(message: Message, state: FSMContext):
    await message.reply(f"You chose the format: {message.text}")
    async with state.proxy() as sound_data:
        sound_data['format'] = message.text.lstrip('/')

    await SoundStates.get_sound.set()


async def get_audio(message: Message, state: FSMContext):
    """ If user upload a sound file"""

    audio_file = await message.audio.get_file()
    audio_id = message.audio.file_id
    # TODO try to no get the format
    chosen_format = await logic.converse(message, audio_file, audio_id, state)
    await message.reply(f"It's an audio!\nIt will conversed to format: {chosen_format}")
    await SoundStates.get_format.set()


async def get_voice(message: Message, state: FSMContext):
    """ If user upload a voice message"""

    voice_file = await message.voice.get_file()
    voice_id = message.voice.file_id
    sound_format = await logic.converse(message, voice_file, voice_id, state)
    await message.reply(f"It's a voice!\nIt will conversed to format: {sound_format}")
    await SoundStates.get_format.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state=None)
    dp.register_message_handler(choose_format, commands=commands.formats, state=SoundStates.get_format)
    dp.register_message_handler(get_audio, state=SoundStates.get_sound, content_types=ContentTypes.AUDIO)
    dp.register_message_handler(get_voice, state=SoundStates.get_sound, content_types=ContentTypes.VOICE)
