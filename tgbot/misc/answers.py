import os
from tgbot.config import FilePaths


def get_answer(answer='entry') -> str:
    """Get answer file name from data/answers directory
    Keyword argument:
        answer - name of answer file
    Returns value:
        answer_string - string contains bot answer
    """
    # os.path.abspath(__file__)
    answer_with_path = os.path.join(FilePaths.answers_path, answer + '.txt')
    with open(answer_with_path, mode='r', encoding='utf-8') as answr:
        answer_string = answr.read()
    return answer_string
