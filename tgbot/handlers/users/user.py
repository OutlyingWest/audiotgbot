from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.types.message import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest

from tgbot.states.states import SoundStates
from tgbot.misc import commands, answers
from tgbot.handlers.users.handlers import sound
from tgbot.data.manage.database.handler import SQLiteHandler


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
        sound_data['id'] = str(audio_id)

    load_complete_text = answers.get_answer(message, 'message_load_complete')
    await message.reply(load_complete_text)

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

    load_complete_text = answers.get_answer(message, 'message_load_complete')
    await message.reply(load_complete_text)

    get_format_text = answers.get_answer(message, 'get_format_step')
    await message.answer(get_format_text)

    await SoundStates.get_format.set()


async def choose_format(message: Message, state: FSMContext):

    sound_format = message.text.lstrip('/')

    conversion_in_progress_text = answers.get_answer(message, 'conversion_in_progress')
    await message.answer(conversion_in_progress_text)

    async with state.proxy() as sound_data:
        audio_file = sound_data['file']
        audio_id = sound_data['id']
    output_audio = await sound.converse(message, audio_file, audio_id, sound_format)
    # Get file from InputFile object
    output_audio_file = output_audio.get_file()
    output_audio_filename = output_audio.get_filename()
    # Send file to telegram user
    chat_id = message.chat.id
    try:
        await message.bot.send_document(chat_id, (output_audio_filename, output_audio_file))
    except BadRequest:
        empty_error_text = answers.get_answer(message, 'empty_upload_error')
        await message.answer(empty_error_text)
    # Send message to return to get audio
    get_sound_text = answers.get_answer(message, 'get_sound_step')
    await message.answer(get_sound_text)
    # Set next state
    await SoundStates.get_sound.set()


async def bot_help(message: Message):
    help_text = answers.get_answer(message, 'help')
    await message.answer(help_text)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state=None)
    dp.register_message_handler(bot_help, commands=["help"], state="*", content_types=ContentTypes.TEXT)
    dp.register_message_handler(get_audio, state=SoundStates.get_sound, content_types=ContentTypes.AUDIO)
    dp.register_message_handler(get_voice, state=SoundStates.get_sound, content_types=ContentTypes.VOICE)
    dp.register_message_handler(choose_format, commands=commands.formats, state=SoundStates.get_format)

