import datetime
import os
import vars

session_time = None


def new_session() -> None:
    global session_time
    session_time = datetime.datetime.now()
    os.makedirs(get_session_folder(), exist_ok=True)


def get_session_folder() -> str:
    dir_name = session_time.strftime("%Y-%m-%d %H-%M")
    return os.path.join(vars.RESULTS_DIR, dir_name)


def get_session_path(*path_args) -> str:
    return os.path.join(get_session_folder(), *path_args)


new_session()