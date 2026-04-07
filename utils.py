import aiosqlite
from config import OWNER_ID

DB = "survey.db"

async def get_role(telegram_id: int):
    if telegram_id == OWNER_ID:
        return "owner"

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT role FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cur.fetchone()

    if row:
        return row[0]
    return "user"
