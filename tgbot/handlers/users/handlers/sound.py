import asyncio
import logging
import os
import re
from collections import defaultdict
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from tgbot.misc import commands
from pathlib import Path
from aiogram.types import File
from pydub import AudioSegment

from tgbot.data.database.handler import SQLiteHandler

logic_logger = logging.getLogger(__name__)


async def add_file_for_current_user(message: Message, user_id, file_id):
    """This function gets the user id and input a file id for addition in database
        if amount of files more than <some num>, the elder files for current user
        will be deleted from server file system and database
        """
    sql_handler = SQLiteHandler(message)
    sql_handler.insert_to_exiting_table('audio', telegram_file_id=file_id, tg_user_id=user_id)
    sql_handler.close_connection()


async def handle_input_file(message: Message, file: File, file_name: str) -> bool:
    """ Create a directory for an audio file if it has not been created yet
        and download the audio file in this directory
        """
    path = message.bot.get('config').sound_file_path.input_path
    Path(path).mkdir(parents=True, exist_ok=True)
    file = await message.bot.download_file(file_path=file.file_path, destination=f"{path}{file_name}")

    return file is not None


async def converse(message: Message, sound_file: File, sound_id, sound_info: FSMContext):
    """ Execute the conversion to the chose sound format"""
    async with sound_info.proxy() as si:
        chosen_format = si['format']

    user_id = message.from_user.id
    # Assemble the file name in download directory
    try:   # Check if file name exist - for audio files only
        file_name = message.audio.file_name
        sound_name = f'{sound_id}_{file_name}'
    except AttributeError:
        sound_name = f'voice_{sound_id}.ogg'

    download_tasks = [asyncio.create_task(add_file_for_current_user(message, user_id, sound_id)),
                      asyncio.create_task(handle_input_file(message, sound_file, sound_name)), ]
    download_tasks_done, _ = await asyncio.wait(download_tasks, return_when=asyncio.ALL_COMPLETED)
    is_conv_done = False
    if download_tasks_done:
        is_conv_done = handle_conversion(message, user_id, sound_id, chosen_format, bitrate="128k")
    else:
        await message.reply('Something went wrong on file downloading!')

    if not is_conv_done:
        chosen_format = None
    return chosen_format


def handle_conversion(message: Message, user_id, file_id: str, chosen_format="mp3", bitrate="128k"):
    """ Perform the conversion of audio file. For this function finds file
        name in download directory and converse it. After that take file
        to the upload directory.
        Note 1: Download and upload directory defines in config .env file
        :return: file format defined by user if conversion is done,
                 None if it is not.
        """
    is_conv_done: bool
    is_file_name_correct = False
    sql_handler = SQLiteHandler(message)
    users_data_dict: defaultdict = sql_handler.get_users_data()
    user_found = False
    for user, tg_file_ids in users_data_dict.items():
        user_tg_id, _ = user
        for tg_file_id in tg_file_ids:
            if user_tg_id == user_id and tg_file_id == file_id:
                # Get paths from config
                download_path: str = message.bot.get('config').sound_file_path.input_path
                upload_path = message.bot.get('config').sound_file_path.output_path
                # Find sound name in audio directory
                sound_names = [file_name for file_name in os.listdir(download_path)]
                sound_name = [sound_name
                              for sound_name
                              in sound_names
                              if re.search(pattern=f'.*{tg_file_id}.*', string=sound_name)]
                sound_name_str = ''
                if len(sound_name) == 1:
                    sound_name_str = str(sound_name)
                    sound_name_str = sound_name_str.strip("[]'")
                    is_file_name_correct = True
                try:
                    # Creation of audio file instance to converse
                    sound = AudioSegment.from_file(download_path + sound_name_str)
                    # Strip a file format
                    sound_name_str_no_fmt = sound_name_str.split('.')[0]
                    # Conversion and export to upload directory
                    sound.export(f'{upload_path}{sound_name_str_no_fmt}.{chosen_format}',
                                 format=chosen_format,
                                 bitrate=bitrate)
                    user_found = True
                except ValueError:
                    logic_logger.info("Conversion failed")
                break
        if user_found:
            break
    else:
        logic_logger.info("Program can not find the user or file")

    return is_file_name_correct


def delete_elder_files_for_current_user():
    pass
