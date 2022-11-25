from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.dispatcher import FSMContext
from tgbot.states.states import SoundStates
from tgbot.misc import commands


async def user_start(message: Message):
    await message.reply("Hello, user!")
    await SoundStates.get_format.set()


async def choose_format(message: Message, state: FSMContext):
    await message.reply(f"You chose the format: {message.text}")
    async with state.proxy() as sound_data:
        sound_data['format'] = message.text.lstrip('/')
    await SoundStates.get_sound.set()


async def get_audio(message: Message, state: FSMContext):
    """ If user upload a sound file"""
    await message.reply("It's an audio!")


async def get_voice(message: Message, state: FSMContext):
    """ If user upload a voice message"""
    async with state.proxy() as sound_data:
        sound_format = sound_data['format']
    await message.reply(f"It's a voice!\nIt will conversed in format: {sound_format}")
    await SoundStates.get_format.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state=None)
    dp.register_message_handler(choose_format, commands=commands.formats, state=SoundStates.get_format)
    dp.register_message_handler(get_audio, state=SoundStates.get_sound, content_types=ContentTypes.AUDIO)
    dp.register_message_handler(get_voice, state=SoundStates.get_sound, content_types=ContentTypes.VOICE)
