# 📊 Survey Telegram Bot

A Telegram bot designed to collect survey responses, analyze results, and visualize data.

## 🚀 Features

* Collect user responses through Telegram chat
* Store and manage survey data
* Generate statistics for each question
* Create visual charts (diagrams)
* Export results in **CSV** and **Excel** formats
* Admin panel for full control

---

## 📱 User Flow

Users interact with the bot in the following steps:

1. Enter their last name
2. Share their phone number
3. Answer survey questions

Example questions:

* “Do you think corruption exists in your institution?”
* “Have you encountered corruption in the last 1 year?”

---

## 📊 Data Visualization

The bot generates charts based on survey responses.

Examples:

* Distribution of answers per question
* Most common responses
* Sector-based corruption analysis

---

## 🛠 Admin Panel

The bot includes an admin interface with the following options:

* 📊 Overall statistics
* 📈 Chart by question
* 📥 Download CSV
* 📥 Download Excel
* ➕ Add admin
* ➖ Remove admin

---

## ⚙️ Tech Stack

* Python (aiogram or pyTelegramBotAPI)
* Pandas (data processing)
* Matplotlib / Seaborn (charts)
* SQLite or PostgreSQL (database)

---

## 📦 Installation

```bash
git clone https://github.com/your-repo/survey-bot.git
cd survey-bot
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_id
```

### Run the bot

```bash
python bot.py
```

---

## 📁 Export Formats

The bot supports exporting results in:

* CSV (`.csv`)
* Excel (`.xlsx`)

---

## 📌 Summary

This bot helps you:

* Automate survey collection
* Analyze responses efficiently
* Visualize data in real-time
* Manage everything through an admin panel

---

## 🤝 Contribution

Feel free to fork the project and submit pull requests.

---

## 📄 License

This project is open-source and available under the MIT License.
