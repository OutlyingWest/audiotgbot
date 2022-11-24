from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes


async def user_start(message: Message):
    await message.reply("Hello, user!")


async def get_audio(message: Message):
    await message.reply("It's an audio!")


async def get_voice(message: Message):
    await message.reply("It's a voice!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(get_audio, content_types=ContentTypes.AUDIO)
    dp.register_message_handler(get_voice, content_types=ContentTypes.VOICE)
