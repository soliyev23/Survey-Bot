import aiosqlite
import pandas as pd
import matplotlib.pyplot as plt
from questions import QUESTIONS

DB = "survey.db"

async def total_users():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]

async def answers_by_question(q_number: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT answer, COUNT(*) 
            FROM answers 
            WHERE question = ?
            GROUP BY answer
        """, (q_number,))
        return await cur.fetchall()

async def get_detailed_statistics():
    """Get statistics with percentages for all questions"""
    total = await total_users()
    
    if total == 0:
        return "Hali surveydan o'tgan foydalanuvchi yo'q."
    
    stats_text = f"📊 Umumiy Statistika\n"
    stats_text += f"{'='*34}\n"
    stats_text += f"Jami ishtirokchilar: {total} ta\n"
    stats_text += f"{'='*34}\n\n"
    
    for q_num, (q_text, options) in enumerate(QUESTIONS, 1):
        # Remove question number from text for cleaner display
        question_text = q_text.split(". ", 1)[1] if ". " in q_text else q_text
        stats_text += f"Savol {q_num}: {question_text}\n"
        
        data = await answers_by_question(q_num)
        
        # Create a dictionary of answers with their counts
        answer_counts = {answer: count for answer, count in data}
        
        # Show all possible options
        for option in options:
            count = answer_counts.get(option, 0)
            percentage = (count / total) * 100
            stats_text += f"  • {option}: {count} ({percentage:.1f}%)\n"
        
        stats_text += "\n"
    
    return stats_text

async def export_csv():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT u.telegram_id, u.first_name, u.last_name, 
                   a.question, a.answer
            FROM users u
            JOIN answers a ON u.telegram_id = a.telegram_id
        """)
        rows = await cur.fetchall()
        columns = ["telegram_id", "first_name", "last_name", "question", "answer"]
        df = pd.DataFrame(rows, columns=columns)

    file = "files/survey_results.csv"
    df.to_csv(file, index=False)
    return file

async def export_excel():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT u.telegram_id, u.first_name, u.last_name, 
                   a.question, a.answer
            FROM users u
            JOIN answers a ON u.telegram_id = a.telegram_id
        """)
        rows = await cur.fetchall()
        columns = ["telegram_id", "first_name", "last_name", "question", "answer"]
        df = pd.DataFrame(rows, columns=columns)

    file = "files/survey_results.xlsx"
    df.to_excel(file, index=False)
    return file


async def build_chart(q_number: int):
    """Diagramma chiz - barcha javoblarni ko'rsatadi, hatto 0% bo'lsa ham"""
    from questions import QUESTIONS
    
    # Savolning barcha javoblarini olish
    q_text, options = QUESTIONS[q_number - 1]
    
    # Ma'lumotlarni olish
    data = await answers_by_question(q_number)
    answer_counts = {answer: count for answer, count in data}
    
    # Barcha javoblarni ro'yxat bilan chiqarish (0 ham kiradi)
    labels = options
    values = [answer_counts.get(option, 0) for option in options]
    
    # Jami javoblar sonini hisoblash
    total = sum(values)
    
    # Diagramma turini tanlash - javoblar soniga qarab
    num_answers = len(options)
    
    # To'q ranglar - Dark2 sxemasi
    dark_colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02', '#a6761d', '#666666']
    
    plt.figure(figsize=(10, 6))
    
    if num_answers == 2:
        # Pie chart uchun 2 ta javob
        colors = dark_colors[:len(labels)]
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title(f"Savol {q_number}: {q_text.split('. ', 1)[1] if '. ' in q_text else q_text}")
        
    elif num_answers <= 5:
        # Bar chart
        colors = dark_colors[:len(labels)]
        plt.bar(labels, values, color=colors)
        plt.title(f"Savol {q_number}: {q_text.split('. ', 1)[1] if '. ' in q_text else q_text}")
        plt.ylabel("Javoblar soni")
        plt.xticks(rotation=10, ha='right')
        
    else:
        # Horizontal bar chart 5+ javoblar uchun
        colors = dark_colors[:len(labels)]
        plt.barh(labels, values, color=colors)
        plt.title(f"Savol {q_number}: {q_text.split('. ', 1)[1] if '. ' in q_text else q_text}")
        plt.xlabel("Javoblar soni")
    
    # Percentni qo'shish
    percentages = [f"{(v/total*100):.1f}%" if total > 0 else "0%" for v in values]
    
    plt.tight_layout()
    
    file = f"diagrams/chart_q{q_number}.png"
    plt.savefig(file, dpi=100, bbox_inches='tight')
    plt.close()
    return file
