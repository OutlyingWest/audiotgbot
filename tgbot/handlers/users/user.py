import aiogram.types.message
from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.types.message import ParseMode
from aiogram.dispatcher import FSMContext

from tgbot.states.states import SoundStates
from tgbot.misc import commands, answers
from tgbot.handlers.users.handlers import sound
from tgbot.data.database.handler import SQLiteHandler


async def user_start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    entry_answer_text = answers.get_answer(message, 'entry')
    await message.reply(entry_answer_text, parse_mode=ParseMode.HTML)

    get_sound_text = answers.get_answer(message, 'get_sound_step')
    await message.answer(get_sound_text)

    # Creation of a database connection to add usr name and tg-id
    sql_handler = SQLiteHandler(message)
    # Insert user data to table "users"
    sql_handler.insert_to_exiting_table('users', telegram_id=user_id, first_user_name=first_name)
    await SoundStates.get_sound.set()


async def get_audio(message: Message, state: FSMContext):
    """ If user upload a sound file"""
    audio_file = await message.audio.get_file()
    audio_id = message.audio.file_id
    async with state.proxy() as sound_data:
        sound_data['file'] = audio_file
        sound_data['id'] = audio_id
    await message.reply("Ваш аудиофайл успешно загружен!")
    get_format_text = answers.get_answer(message, 'get_format_step')
    await message.answer(get_format_text)
    await SoundStates.get_format.set()


async def get_voice(message: Message, state: FSMContext):
    """ If user upload a voice message"""

    voice_file = await message.voice.get_file()
    voice_id = message.voice.file_id
    async with state.proxy() as sound_data:
        sound_data['file'] = voice_file
        sound_data['id'] = voice_id
    await message.reply("Ваше аудиоcообщение успешно загружено!")
    get_format_text = answers.get_answer(message, 'get_format_step')
    await message.answer(get_format_text)
    await SoundStates.get_format.set()


async def choose_format(message: Message, state: FSMContext):
    sound_format = message.text.lstrip('/')
    async with state.proxy() as sound_data:
        audio_file = sound_data['file']
        audio_id = sound_data['id']
    output_audio = await sound.converse(message, audio_file, audio_id, sound_format)
    # Get file from InputFile object
    output_audio_file = output_audio.get_file()
    output_audio_filename = output_audio.get_filename()
    # Send file to telegram user
    chat_id = message.chat.id
    await message.bot.send_document(chat_id, (output_audio_filename, output_audio_file))
    await SoundStates.get_sound.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state=None)
    dp.register_message_handler(get_audio, state=SoundStates.get_sound, content_types=ContentTypes.AUDIO)
    dp.register_message_handler(get_voice, state=SoundStates.get_sound, content_types=ContentTypes.VOICE)
    dp.register_message_handler(choose_format, commands=commands.formats, state=SoundStates.get_format)

