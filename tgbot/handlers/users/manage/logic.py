from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram import Bot
from tgbot.misc import commands
from pathlib import Path
from aiogram.types import File


class UserLogic:
    """ This class performs getting the bot instsnce from bot.py
        for provide possibility to use Bot class methods in handler functions
    """
    bot: Bot

    @classmethod
    def get_bot_instance(cls, bot: Bot):
        cls.bot = bot

    @classmethod
    async def _handle_input_file(cls, file: File, file_name: str):
        """ Create a directory for an audio file if it has not been created yet
            and download the audio file in this directory
        """
        path = cls.bot.get('config').sound_file_path.input_path
        Path(path).mkdir(parents=True, exist_ok=True)
        await cls.bot.download_file(file_path=file.file_path, destination=f"{path}{file_name}")

    @classmethod
    async def converse(cls, sound_file: File, sound_name: FSMContext):
        """ Execute the conversion to the chose sound format"""
        async with sound_name.proxy() as sn:
            sound_format = sn['format']
            print(sound_format)

        if sound_format != 'other':
            await cls._handle_input_file(sound_file, sound_format)
        else:
            pass

        return sound_format



    # -------------------------------------
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

    # Assemble the file name in download directory
    try:   # Check if file name exist - for audio files only
        file_name = message.audio.file_name
        sound_name = f'{sound_id}_{file_name}'
    except AttributeError:
        sound_name = f'voice_{sound_id}.ogg'

    await handle_input_file(message, sound_file, sound_name)

    return chosen_format


async def handle_conversed_file():
    sound_file = None
    return sound_file


async def save_to_db():
    pass
