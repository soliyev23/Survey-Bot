from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def admin_menu(owner=False):
    buttons = [
        [KeyboardButton(text="📊 Umumiy statistika")],
        [KeyboardButton(text="📈 Savol bo'yicha diagramma")],
        [KeyboardButton(text="📥 CSV yuklash")],
        [KeyboardButton(text="📥 Excel yuklash")]
    ]
    if owner:
        buttons.append([KeyboardButton(text="➕ Admin qo'shish")])
        buttons.append([KeyboardButton(text="➖ Admin o'chirish")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

def questions_menu():
    buttons = []
    for i in range(1, 11):
        buttons.append([KeyboardButton(text=f"Savol {i}")])
    buttons.append([KeyboardButton(text="Ortga")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )