# Contains settings and environment variables
from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str

@dataclass
class SQLiteDbConfig:
    database: str
    tables: list[str]

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool

@dataclass
class FilePaths:
    input_path: str
    output_path: str


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    sqlite_db: SQLiteDbConfig
    sound_file_path: FilePaths
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        sqlite_db=SQLiteDbConfig(
            database=env.str('SQLITE_DB_NAME'),
            tables=env.list('SQLITE_DB_TABLES')
        ),
        sound_file_path=FilePaths(
            input_path=env.str('INPUT_AUDIO_FILES_PATH'),
            output_path=env.str('OUTPUT_AUDIO_FILES_PATH')
        ),
        misc=Miscellaneous(),
    )
