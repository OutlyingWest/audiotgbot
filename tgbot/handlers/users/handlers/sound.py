import asyncio
import logging
import os
import re
from collections import defaultdict
from aiogram.types import Message
from pathlib import Path
from aiogram.types import File
from aiogram.types.input_file import InputFile
from pydub import AudioSegment

from tgbot.data.database.handler import SQLiteHandler

logic_logger = logging.getLogger(__name__)


async def converse(message: Message, sound_file: File, sound_id: str, chosen_format: str):
    """ Execute the conversion to the chose sound format
    Return value:
        output_file - converted file
    """

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
    output_file = None
    if download_tasks_done:
        is_conv_done = handle_conversion(message, user_id, sound_id, chosen_format, bitrate="128k")
        output_file = handle_output_file(message)
    else:
        await message.reply('Something went wrong on file downloading!')

    if not is_conv_done:
        output_file = None

    return output_file


def glob_re(path, regex="", glob_mask="**/*", inverse=False):
    """Find for files by regex
    Parameters:
        path - path to directory to start finding
        regex - regular expression for find
        glob_mask="**/*" - find recursive by default,
                       find i current directory use "*"
        inverse - bool if True - find items include regex,
                      if False - find items exclude regex
        Returns:
            res - file name
    """
    p = Path(path)
    if inverse:
        res = [str(f) for f in p.glob(glob_mask) if not re.search(regex, str(f))]
    else:
        res = [str(f) for f in p.glob(glob_mask) if re.search(regex, str(f))]
    return res


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
    path = message.bot.get('config').file_path.audio_input_path
    Path(path).mkdir(parents=True, exist_ok=True)
    file = await message.bot.download_file(file_path=file.file_path, destination=f"{path}{file_name}")

    return file is not None


def handle_output_file(message: Message):
    """Take converted audio from upload directory
    Return value:
        converted_audio - InputFile object
    """
    user_id = message.from_user.id
    sql_handler = SQLiteHandler(message)
    user_data_dict: defaultdict = sql_handler.get_user_data(user_id)
    sql_handler.close_connection()

    # Get file id for current user if he exists
    if user_data_dict:
        # Get user key
        user_key = list(user_data_dict.keys())[0]
        file_ids = user_data_dict[user_key]
        file_id = file_ids[-1]
        # Get file
        audio_output_path = message.bot.get('config').file_path.audio_output_path
        file_name_list = glob_re(audio_output_path, regex=f".*{file_id}.*", glob_mask="*")
        file_name_with_path = file_name_list[0]
        # Send file to telegram user
        if file_name_with_path:
            file_format = file_name_with_path.split('.')[1]
            converted_audio = InputFile(file_name_with_path, filename=f'converted_audio.{file_format}')
            # converted_audio_file = converted_audio.get_file()
        else:
            converted_audio = None
            logic_logger.info(f"File with name {file_name_with_path} is not found")

        return converted_audio


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
    # Get paths from config
    download_path: str = message.bot.get('config').file_path.audio_input_path
    upload_path = message.bot.get('config').file_path.audio_output_path

    user_found = False
    for user, tg_file_ids in users_data_dict.items():
        user_tg_id, _ = user
        for tg_file_id in tg_file_ids:
            if user_tg_id == user_id and tg_file_id == file_id:
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
                    sound_name_str_no_format = sound_name_str.split('.')[0]
                    # Conversion and export to upload directory
                    # TODO: alac, aac formats is not work raise CouldntEncodeError pydub.exceptions.CouldntEncodeError
                    sound.export(f'{upload_path}{sound_name_str_no_format}.{chosen_format}',
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
