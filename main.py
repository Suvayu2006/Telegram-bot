import asyncio
import logging
from typing import Final
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN: Final = '8154854350:AAE5IH4svWa9_964SI9fPqbK0R8YSNJEPkY'
BOT_USERNAME: Final = '@Xylomutronixbot'

# ─── Commands ────────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am Xylomutronix!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please type valid music names, otherwise I cannot help you!')

async def type_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type your music!')

# ─── Response Logic ──────────────────────────────────────────
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed:
        return 'Hi There!'
    if 'how are you' in processed:
        return 'I am fine. How was your day today?'
    if 'fine' in processed:
        return 'Great!!! I will play some songs for you!!!'
    if 'i love musics' in processed or 'i love songs' in processed:
        return ('Music is a different world of humans where love, sadness, '
                'loneliness — everything is there.')
    return 'I do not understand what you wrote. Try saying hello!'

# ─── Message Handler ─────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    await update.message.reply_text(response)

# ─── Error Handler ───────────────────────────────────────────
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# ─── Build Bot ───────────────────────────────────────────────
bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler('start', start_command))
bot_app.add_handler(CommandHandler('help', help_command))
bot_app.add_handler(CommandHandler('type', type_command))
bot_app.add_handler(MessageHandler(filters.TEXT, handle_message))
bot_app.add_error_handler(error)

# ─── Flask App ───────────────────────────────────────────────
flask_app = Flask(__name__)

@flask_app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.process_update(update))
    return 'OK'

@flask_app.route('/')
def index():
    return '🤖 Xylomutronix Bot is running!'

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000)
