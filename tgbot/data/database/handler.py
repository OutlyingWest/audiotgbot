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
        with connection object instance"""
        if obj:
            database_name, tables = self.get_config(obj)
        elif not database_name or not tables:
            raise ValueError('Input "database_name" and "tables" args if you have not obj with bot instance')

        self.tables = tables
        self.conn = sqlite3.connect(database_name, timeout=timeout)
        self.cur = self.conn.cursor()

    async def exists_table(self, name: str):
        """Returns bool - answer the table exist or not"""
        query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
        return self.conn.execute(query, (name,)).fetchone() is not None

    @staticmethod
    def get_config(obj):
        """Load config from .env file through bot instance
            getting by obj.bot or bot"""
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
        self.conn.execute("PRAGMA foreign_keys = 1")
        if not tables:
            users_table, audio_table, *other_tables = self.tables
            if other_tables:
                raise ValueError(f'other_tables: {other_tables} have found! This behaviour have not realised yet!')

            self.cur.execute("""CREATE TABLE IF NOT EXISTS {}(
                tg_id INT NOT NULL PRIMARY KEY,
                first_name TEXT NOT NULL);""".format(users_table))
            self.conn.commit()

            self.cur.execute("""CREATE TABLE IF NOT EXISTS {}(
            tg_user_id INT NOT NULL PRIMARY KEY,
            tg_id TEXT NOT NULL,
            FOREIGN KEY (tg_user_id) REFERENCES users(tg_id));""".format(audio_table))
            self.conn.commit()

    def insert_to_exiting_table(self, table_name):
        """This method provide the ability to insert one line of data
        to exiting table from the list self.tables"""
        pass

    def get_from_exiting_table(self, table_name):
        """This method provide the ability to get one line of data
        from exiting table of list self.tables"""

    def close_connection(self):
        self.conn.close()


