import os
from aiogram.utils.markdown import hcode


def get_answer(obj, answer='entry') -> str:
    """Get answer file name from data/answers directory
    Keyword arguments:
        :obj: aiogram Message like object to get config from it
        :answer: name of answer file
    Returns value:
        answer_string - string contains bot answer
    """
    answer_with_path = os.path.join(obj.bot.get('config').file_path.answers_path, answer + '.txt')
    with open(answer_with_path, mode='r', encoding='utf-8') as answr:
        answer_string = answr.read()
    answer_string_with_format = answer_string.format(
        first_name=obj.from_user.first_name,
        format_cmd=hcode('/format'),
        error=hcode('Error:')
    )
    return answer_string_with_format
