from collections import defaultdict
import sqlite3
import logging


handler_logger = logging.getLogger(__name__)


class SQLiteHandler:
    def __init__(self, obj=None, database_name=None, tables=None, timeout=5):
        """Class provide connection and methods to interact
        with sqlite3 database which uses to store:
            - users telegram id
            - file id of users uploaded files
        Also this class provide ability to interact to your own
        databases. In this case you must enter the name of your
        database, and names of your tables which will be created
        with connection object instance
        """
        if obj:
            database_name, tables = self.get_config(obj)
        elif not database_name or not tables:
            raise ValueError('Input "database_name" and "tables" args if you have not obj with bot instance')
        self.tables = tables
        self.conn = sqlite3.connect(database_name, timeout=timeout)
        self.cur = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()

    async def exists_table(self, name: str):
        """Returns bool - answer the table exist or not"""
        query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
        return self.conn.execute(query, (name,)).fetchone() is not None

    @staticmethod
    def get_config(obj):
        """Load config from .env file through bot instance
        getting by obj.bot or bot
        """
        try:
            config = obj.bot.get('config')
            database_name = config.sqlite_db.database
            tables = config.sqlite_db.tables
            return database_name, tables
        except AttributeError:
            try:
                config = obj.get('config')
                database_name = config.sqlite_db.database
                tables = config.sqlite_db.tables
                return database_name, tables
            except AttributeError:
                handler_logger.info("get_config method can't to get bot instance")

    def create_tables(self, tables=None):
        if not tables:
            users_table, audio_table, *other_tables = self.tables
            if other_tables:
                raise ValueError(f'other_tables: {other_tables} have found! This behaviour have not realised yet!')

            self.cur.execute("""CREATE TABLE IF NOT EXISTS {}(
                tg_id INT NOT NULL PRIMARY KEY,
                first_name TEXT NOT NULL);""".format(users_table))
            self.conn.commit()

            self.cur.execute("""CREATE TABLE IF NOT EXISTS {}(
                tg_id TEXT NOT NULL PRIMARY KEY,
                tg_user_id INT NOT NULL,
                FOREIGN KEY (tg_user_id) REFERENCES users(tg_id));""".format(audio_table))
            self.conn.commit()

    def insert_to_exiting_table(self, table_name, **kwargs):
        """This method provide the ability to insert one line of data
        to users table if it contains in the list self.tables
        Parameter names for "users" table: telegram_id: int=..., first_user_name: str=...
        Parameter names for "audio" table: telegram_file_id: str=..., tg_user_id: int=...
        """
        if table_name in self.tables:
            if table_name == 'users':
                if 'telegram_id' in kwargs.keys() and 'first_user_name' in kwargs.keys():
                    telegram_id = kwargs['telegram_id']
                    first_user_name = kwargs['first_user_name']
                    try:
                        self.cur.execute("""INSERT INTO users(tg_id, first_name)
                        VALUES (?, ?);""", (telegram_id, first_user_name))
                    except sqlite3.IntegrityError:
                        handler_logger.info(f'User - id: {telegram_id}, name: {first_user_name} already exists')
                else:
                    raise ValueError('''Wrong parameter names for users table.
                    Right: telegram_id: int=..., first_user_name: str=...''')

            elif table_name == 'audio':
                if 'telegram_file_id' in kwargs.keys() and 'tg_user_id' in kwargs.keys():
                    telegram_file_id = kwargs['telegram_file_id']
                    tg_user_id = kwargs['tg_user_id']
                    try:
                        self.cur.execute("""INSERT INTO audio(tg_id, tg_user_id)
                        VALUES (?, ?);""", (telegram_file_id, tg_user_id))
                    except sqlite3.IntegrityError:
                        handler_logger.info(f'File - id: {telegram_file_id}, for user(id): {tg_user_id} already exists')
                else:
                    raise ValueError('''Wrong parameter names for users table.
                    Right: telegram_file_id: str=..., tg_user_id: int=...''')
            else:
                raise ValueError('Tables exclude users and audio is not maintain yet')

            self.conn.commit()

    def get_users_data(self):
        """This method provide the ability to get all data
        about users and put it into the dictionary which returns
        by this method
        example of return value:
        defaultdict(<class 'list'>, {(1, 'Alex'): ['asdfasaHLUHJHLHLJhljh'], ...}
        where {(tg_user_id, 'first_name'): ['tg_file_id_1', 'tg_file_id_2', ...]) ...}
        """
        select_query = self.cur.execute(
        """
        SELECT users.tg_id AS tg_id,
        users.first_name,
        audio.tg_id
        FROM users JOIN audio
        ON users.tg_id = audio.tg_user_id;
        """)
        users_data = select_query.fetchall()

        users_dict = defaultdict(list)
        for *user_alias, file_id in users_data:
            users_dict[tuple(user_alias)].append(file_id)

        return users_dict

    def get_user_data(self, user_id):
        """This method provide the ability to get one line of data
        from users table. Returns defaultdict
        """
        select_query = self.cur.execute(
        """
        SELECT users.tg_id,
        users.first_name,
        audio.tg_id
        FROM users
        JOIN audio
        ON users.tg_id = audio.tg_user_id
        WHERE users.tg_id = ?;
        """, (user_id,))
        user_data_list = select_query.fetchall()

        user_dict = defaultdict(list)
        for *user_alias, file_id in user_data_list:
            user_dict[tuple(user_alias)].append(file_id)

        return user_dict

    def get_from_exciting_table(self, table_name, **kwargs):
        """This method provide the ability to get one line of data
        from users table if it contains in the list self.tables
        """
        pass

    def delete_from_exciting_table(self, table_name):
        """This method provide the ability to delete one string
        from exciting table
        """

        pass

    def close_connection(self):
        self.conn.close()


def test():
    pass


if __name__ == "__main__":
    test()
