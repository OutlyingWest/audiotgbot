import re
import os
from pathlib import Path

from aiogram.types import Message

from tgbot.data.manage.database.handler import SQLiteHandler


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


def delete_file_by_id(file_path: str, tg_file_id: str):
    file_name_list = glob_re(file_path, regex=f".*{tg_file_id}.*", glob_mask="*")
    if file_name_list:
        file_name_with_path = file_name_list[0]
        if os.path.isfile(file_name_with_path):
            os.remove(file_name_with_path)
        else:
            print(f'File in {file_path} is not exist')


def delete_elder_user_data(num_of_elder: int, num_in_dir_for_user: int, user_id: int, message: Message):
    """Principle of work:
        Delete num_of_elder from audio dir if number of files in dir > num_in_dir_for_user
        with user id = user_id
        Arguments:
            num_of_elder - number of elder files to delete
            num_in_dir_for_user - number after exceed that for user with user_id the deletion is allowed
        """
    if num_in_dir_for_user <= num_of_elder:
        raise ValueError('num_in_dir_for_user must be over than num_of_elder')

    sql_handler = SQLiteHandler(message)
    num_lines_in_audio = sql_handler.get_num_lines_in_audio(user_id)
    # Get input file name
    audio_input_path = message.bot.get('config').file_path.audio_input_path
    # Get output file name
    audio_output_path = message.bot.get('config').file_path.audio_output_path

    if num_lines_in_audio > num_in_dir_for_user:
        while num_of_elder > 0:
            num_of_elder -= 1
            # Get elder audio id from db for user
            elder_audio_id = sql_handler.get_elder_audio_tgid(user_id)
            print(f"User's (id: {user_id}) elder audio with id: {elder_audio_id} deleted")
            # Delete elder input file for user
            delete_file_by_id(audio_input_path, elder_audio_id)
            # Delete elder output file for user
            delete_file_by_id(audio_output_path, elder_audio_id)
            # Delete line from table for user
            sql_handler.delete_from_audio_table(user_id, elder_audio_id)

