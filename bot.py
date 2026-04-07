import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, OWNER_ID, ADMIN_IDS
from database import init_db
from states import SurveyState, AdminState
from questions import QUESTIONS
import aiosqlite

from utils import get_role
from keyboards import admin_menu, questions_menu
from stats import total_users, export_csv, build_chart, get_detailed_statistics, export_excel
from aiogram.types import FSInputFile


bot = Bot(BOT_TOKEN)
dp = Dispatcher()

DB = "survey.db"

# ---------------- START ----------------
@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)

    # OWNER bo'lsa
    if role == "owner":
        await state.clear()
        await message.answer(
            "Owner panelga xush kelibsiz.\n"
            "Davom etish uchun /owner buyrug'ini bosing."
        )
        return

    # ADMIN bo'lsa
    if role == "admin":
        await state.clear()
        await message.answer(
            "Admin panelga xush kelibsiz.\n"
            "Davom etish uchun /admin buyrug'ini bosing."
        )
        return

    # Oddiy user bo'lsa — tekshiramiz
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT 1 FROM users WHERE telegram_id = ?",
            (message.from_user.id,)
        )
        exists = await cur.fetchone()

    if exists:
        await message.answer("Siz allaqachon so‘rovnomadan o‘tgansiz.")
        return

    await message.answer(
        "Assalomu alaykum!\n\n"
        "Korrupsiyaga qarshi so‘rovnomaga xush kelibsiz.\n"
        "Ishtirokingiz maxfiy saqlanadi."
    )
    await message.answer("Ismingizni kiriting:")
    await state.set_state(SurveyState.first_name)


@dp.message(F.text == "/owner")
async def owner_panel(message: Message):
    role = await get_role(message.from_user.id)

    if role != "owner":
        await message.answer("Sizda owner huquqi yo'q.")
        return

    await message.answer(
        "Owner panel:",
        reply_markup=admin_menu(owner=True)
    )

@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    role = await get_role(message.from_user.id)

    if role not in ["admin", "owner"]:
        await message.answer("Sizda admin huquqi yo'q.")
        return

    await message.answer(
        "Admin panel:",
        reply_markup=admin_menu(owner=(role == "owner"))
    )

@dp.message(F.text == "📊 Umumiy statistika")
async def stats_total(message: Message):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        return

    stats = await get_detailed_statistics()
    await message.answer(stats)

@dp.message(F.text == "📥 CSV yuklash")
async def csv_download(message: Message):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        return

    file = await export_csv()
    await message.answer_document(FSInputFile(file))

@dp.message(F.text == "📥 Excel yuklash")
async def excel_download(message: Message):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        return
    
    file = await export_excel()
    await message.answer_document(FSInputFile(file))

@dp.message(F.text == "📈 Diagramma")
async def chart(message: Message):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        return

    file = await build_chart(1)
    await message.answer_photo(FSInputFile(file))

@dp.message(F.text == "➕ Admin qo'shish")
async def add_admin(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role != "owner":
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    await message.answer("Admin qilinadigan Telegram ID ni yuboring:")
    await state.set_state(AdminState.waiting_for_admin_id)

@dp.message(AdminState.waiting_for_admin_id, F.text.regexp(r"^\d+$"))
async def save_admin(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role != "owner":
        await state.clear()
        return

    admin_id = int(message.text)
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET role='admin' WHERE telegram_id=?",
            (admin_id,)
        )
        await db.commit()

    await message.answer("Admin muvaffaqiyatli qo'shildi.")
    await state.clear()

@dp.message(F.text == "➖ Admin o'chirish")
async def remove_admin(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role != "owner":
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    await message.answer("O'chiriladigan admin Telegram ID ni yuboring:")
    await state.set_state(AdminState.waiting_for_remove_admin_id)

@dp.message(AdminState.waiting_for_remove_admin_id, F.text.regexp(r"^\d+$"))
async def delete_admin(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role != "owner":
        await state.clear()
        return

    admin_id = int(message.text)
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET role='user' WHERE telegram_id=?",
            (admin_id,)
        )
        await db.commit()

    await message.answer("Admin muvaffaqiyatli o'chirildi.")
    await state.clear()

@dp.message(F.text == "📈 Savol bo'yicha diagramma")
async def choose_question(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        return

    await message.answer(
        "Qaysi savol bo'yicha diagramma kerak?",
        reply_markup=questions_menu()
    )
    await state.set_state(AdminState.waiting_for_question_number)

@dp.message(AdminState.waiting_for_question_number, F.text.regexp(r"^Savol (10|[1-9])$"))
async def send_chart_by_question(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        await state.clear()
        return

    q_number = int(message.text.split()[1])
    file = await build_chart(q_number)
    await message.answer_photo(FSInputFile(file))

@dp.message(AdminState.waiting_for_question_number, F.text == "Ortga")
async def back_to_admin_menu(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if role not in ["admin", "owner"]:
        await state.clear()
        return

    await message.answer(
        "Admin panel:",
        reply_markup=admin_menu(owner=(role == "owner"))
    )
    await state.clear()

# ---------------- USER INFO ----------------
@dp.message(SurveyState.first_name)
async def first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(SurveyState.last_name)

@dp.message(SurveyState.last_name)
async def last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=kb)
    await state.set_state(SurveyState.phone)

@dp.message(SurveyState.phone)
async def phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()

    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO users (telegram_id, username, first_name, last_name, phone)
        VALUES (?, ?, ?, ?, ?)
        """, (
            message.from_user.id,
            message.from_user.username,
            data["first_name"],
            data["last_name"],
            phone
        ))
        await db.commit()

    await state.update_data(q_index=0)
    await ask_question(message, state)

# ---------------- QUESTIONS ----------------
async def ask_question(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data["q_index"]

    q_text, options = QUESTIONS[idx]
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=o)] for o in options],
        resize_keyboard=True
    )
    await message.answer(q_text, reply_markup=kb)
    await state.set_state(SurveyState.question)

@dp.message(SurveyState.question)
async def handle_question(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data["q_index"]

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO answers (telegram_id, question, answer) VALUES (?, ?, ?)",
            (message.from_user.id, idx + 1, message.text)
        )
        await db.commit()

    idx += 1
    if idx >= len(QUESTIONS):
        await message.answer(
            "Qo‘shimcha fikr va takliflaringiz bo‘lsa yozing (ixtiyoriy):",
            reply_markup=ReplyKeyboardMarkup(keyboard=[], remove_keyboard=True)
        )
        await state.set_state(SurveyState.extra_comment)
    else:
        await state.update_data(q_index=idx)
        await ask_question(message, state)

# ---------------- EXTRA COMMENT ----------------
@dp.message(SurveyState.extra_comment)
async def extra_comment(message: Message, state: FSMContext):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO comments (telegram_id, comment) VALUES (?, ?)",
            (message.from_user.id, message.text)
        )
        await db.commit()

    await message.answer(
        "So‘rovnomada ishtirok etganingiz uchun rahmat!\n"
        "Fikringiz biz uchun muhim."
    )
    await state.clear()

# ---------------- RUN ----------------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())