import re
from pathlib import Path


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


def delete_elder_user_files(num_of_elder: int, num_in_dir_for_user: int, user_id):
    """Principle of work:
        Delete num_of_elder from audio dir if number of files in dir > num_in_dir_for_user
        with user id = user_id
        Arguments:
            num_of_elder - number of elder files to delete
            num_in_dir_for_user - number after exceed that for user with user_id the deletion is allowed
        """
    pass
