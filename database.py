import aiosqlite

DB_NAME = "survey.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'user'
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            question INTEGER,
            answer TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            telegram_id INTEGER,
            comment TEXT
        )
        """)
        await db.commit()
