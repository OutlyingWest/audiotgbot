from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from tgbot.misc import commands
from pathlib import Path
from aiogram.types import File

from tgbot.data.database.handler import SQLiteHandler


async def add_file_for_current_user(message: Message, user_id, file_id):
    """This function gets the user id and input a file id for addition in database
        if amount of files more than <some num>, the elder files for current user
        will be deleted from server file system and database
        """
    sql_handler = SQLiteHandler(message)
    sql_handler.insert_to_exiting_table('audio', telegram_file_id=file_id, tg_user_id=user_id)
    sql_handler.close_connection()



async def handle_input_file(message: Message, file: File, file_name: str):
    """ Create a directory for an audio file if it has not been created yet
        and download the audio file in this directory
        """
    path = message.bot.get('config').sound_file_path.input_path
    Path(path).mkdir(parents=True, exist_ok=True)
    await message.bot.download_file(file_path=file.file_path, destination=f"{path}{file_name}")


async def converse(message: Message, sound_file: File, sound_id, sound_info: FSMContext):
    """ Execute the conversion to the chose sound format"""
    async with sound_info.proxy() as si:
        chosen_format = si['format']
        print(chosen_format)

    user_id = message.from_user.id
    # Assemble the file name in download directory
    try:   # Check if file name exist - for audio files only
        file_name = message.audio.file_name
        sound_name = f'{sound_id}_{file_name}'
    except AttributeError:
        sound_name = f'voice_{sound_id}.ogg'

    await add_file_for_current_user(message, user_id, sound_id)
    await handle_input_file(message, sound_file, sound_name)

    return chosen_format


async def handle_conversed_file():
    sound_file = None
    return sound_file


async def save_to_db():
    pass
