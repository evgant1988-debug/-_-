cat > ~/Desktop/bot.py << 'EOF'
import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Переменная TOKEN не задана!")

logging.basicConfig(level=logging.INFO)

def search_vacancies(query, area=0):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "area": area,
        "per_page": 5,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для поиска вакансий.\n"
        "Введи команду /search <запрос>, например:\n"
        "/search python\n"
        "/search java разработчик"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❌ Укажи запрос, например: /search python")
        return

    await update.message.reply_text(f"🔍 Ищу '{query}'...")
    vacancies = search_vacancies(query)

    if not vacancies:
        await update.message.reply_text("😕 Ничего не найдено. Попробуй другой запрос.")
        return

    for v in vacancies[:5]:
        title = v.get("name", "Без названия")
        company = v.get("employer", {}).get("name", "Неизвестная компания")
        salary = v.get("salary")
        if salary:
            sal_str = f"от {salary.get('from')} {salary.get('currency')}" if salary.get('from') else "з/п не указана"
        else:
            sal_str = "з/п не указана"
        url = v.get("alternate_url", "#")

        msg = f"<b>{title}</b>\n🏢 {company}\n💰 {sal_str}\n🔗 <a href='{url}'>Перейти</a>"
        await update.message.reply_text(msg, parse_mode="HTML")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    print("✅ Бот запущен и слушает сообщения...")
    app.run_polling()

if __name__ == "__main__":
    main()
EOF
