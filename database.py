import sqlite3, aiosqlite
from datetime import datetime
from aiogram.types import User as AIOgramUser
from dataclasses import dataclass


""" Dataclasses """ 
# They just store data taken from the SQLite

@dataclass
class DBUser:
    user_id: int
    username: str | None
    active_dialog: str | None


@dataclass
class DBMessage:
    user_id: int
    dialog_id: int
    role: str
    content: str
    theme: str
    time: str | datetime


@dataclass
class DBDialog:
    dialog_id: int
    user_id: int
    started_at: str | datetime
    ended_at: str | datetime | None

    
""" Main Class """
# It contains all the methods to work with SQLite

class Database:
    def __init__(self, db_file: str, context_window: int):
        self.file = db_file
        self.context_window = context_window

        self.db = sqlite3.connect(self.file)
        self.update_tables()
        self.db.close()
        

    def update_tables(self):
        self.db.execute(("""
            -- Создание таблицы users
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER UNIQUE PRIMARY KEY,
                username TEXT,
                active_dialog INTEGER UNIQUE
            );
            """))
        self.db.execute(("""
            -- Создание таблицы dialogs
            CREATE TABLE IF NOT EXISTS dialogs (
                dialog_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            """))
        self.db.execute(("""
            -- Создание таблицы messages
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                dialog_id INTEGER NOT NULL,
                role TEXT,
                content TEXT,
                theme TEXT,
                time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dialog_id) REFERENCES dialogs(dialog_id)
            );
            """))
        self.db.commit()


    async def update_user(self, user: AIOgramUser) -> None:
        async with aiosqlite.connect(self.file) as conn:
            result = await conn.execute_fetchall(
                f"SELECT * FROM users WHERE user_id = {user.id};")
            if not result:
                await conn.execute(
                    ("INSERT INTO users (user_id, username) VALUES"
                    f"({user.id},\"{user.username if user.username else 'NULL'}\");"))
                await conn.commit()
            else:
                await conn.execute(
                    (f"UPDATE users SET username = \"{user.username if user.username else 'NULL'}\""
                    f"WHERE user_id = {user.id};"))
                await conn.commit()

    
    async def get_active_dialog(self, user: AIOgramUser) -> int | None:
        async with aiosqlite.connect(self.file) as conn:
            dialog_id = (await conn.execute_fetchall(
                f"SELECT active_dialog FROM users WHERE user_id = {user.id};"))
            if len(dialog_id) > 0:
                return dialog_id[0][0]
            else:
                return None

            
    async def new_dialog(self, user: AIOgramUser) -> None:
        async with aiosqlite.connect(self.file) as conn:
            await conn.execute(
                f"UPDATE dialogs SET ended_at = \"{str(datetime.now())}\" WHERE user_id = {user.id}")
            await conn.execute(
                f"INSERT INTO dialogs (user_id) VALUES ({user.id})")
            last_id: int = (await conn.execute_fetchall("SELECT MAX(dialog_id) FROM dialogs;"))[0][0]
            await conn.execute(
                f"UPDATE users SET active_dialog={last_id} WHERE user_id={user.id};")
            await conn.commit()


    async def add_message(self, user: AIOgramUser, role: str, content: str, theme: str) -> None:
        content = content.replace('"', '\\"').replace("'", "\\'").replace("`", "\\`")
        theme = theme.replace('"', '\\"').replace("'", "\\'").replace("`", "\\`")
        async with aiosqlite.connect(self.file) as conn:
            dialog_id: int = (await conn.execute_fetchall(
                f"SELECT active_dialog FROM users WHERE user_id = {user.id};"))[0][0]
            await conn.execute(
                ("INSERT INTO messages (dialog_id, role, content, theme) "
                f"VALUES ({dialog_id}, '{role}', ?, ?);"), [content, theme])
            await conn.commit()
        

    async def get_context(self, user: AIOgramUser) -> list[DBMessage]:
        async with aiosqlite.connect(self.file) as conn:
            dialog_id: int = (await conn.execute_fetchall(
                f"SELECT active_dialog FROM users WHERE user_id = {user.id};"))[0][0]
            messages: list = await conn.execute_fetchall(
                ("SELECT * FROM messages "
                f"WHERE dialog_id={dialog_id} ORDER BY message_id DESC LIMIT {self.context_window};"))
        return [DBMessage(*x) for x in messages[::-1]]

    
    async def count_messages(self, user: AIOgramUser) -> int:
        async with aiosqlite.connect(self.file) as conn:
            dialog_id: int = (await conn.execute_fetchall(
                f"SELECT active_dialog FROM users WHERE user_id = {user.id};"))[0][0]
            try:
                count: int = (await conn.execute_fetchall(
                    f"SELECT COUNT(message_id) FROM messages WHERE dialog_id = {dialog_id}"))[0][0]
            except Exception as e:
                print(e)
                count = 0
        return count
        