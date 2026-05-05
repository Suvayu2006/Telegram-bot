import asyncio
import logging
import os
import glob
from typing import Final
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(level=logging.INFO)

TOKEN: Final = '8154854350:AAE5IH4svWa9_964SI9fPqbK0R8YSNJEPkY'
BOT_USERNAME: Final = '@Xylomutronixbot'

os.makedirs('downloads', exist_ok=True)

# ─── Commands ────────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🎵 Hello! I am Xylomutronix!\n\n'
        'Commands:\n'
        '/start - Start the bot\n'
        '/help - Help\n'
        '/song <name> - Search and get any song\n\n'
        'Example: /song Shape of You'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🎵 How to use:\n\n'
        'Type /song followed by the song name\n'
        'Example: /song Believer\n'
        'Example: /song Tum Hi Ho\n'
        'Example: /song Blinding Lights\n\n'
        'I will find and send any song in the world! 🌍'
    )

# ─── Song Command ─────────────────────────────────────────────
async def song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get song name from command: /song Shape of You
    if not context.args:
        await update.message.reply_text(
            '❌ Please provide a song name!\n'
            'Example: /song Shape of You'
        )
        return

    song_name = ' '.join(context.args)
    await download_and_send(update, song_name)


# ─── Core Download Function ───────────────────────────────────
async def download_and_send(update: Update, song_name: str):
    msg = await update.message.reply_text(f'🔍 Searching for: *{song_name}*...', parse_mode='Markdown')

    ydl_opts = {
        'format': 'bestaudio[filesize<50M]/bestaudio/best',
        'outtmpl': f'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'noplaylist': True,
    }

    try:
        loop = asyncio.get_event_loop()

        def do_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_name, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                return info

        info = await loop.run_in_executor(None, do_download)

        title    = info.get('title', song_name)
        duration = info.get('duration', 0)
        uploader = info.get('uploader', 'Unknown Artist')
        ext      = info.get('ext', 'mp3')

        # Find downloaded file
        files = glob.glob(f'downloads/{title[:50]}*.{ext}')
        if not files:
            files = glob.glob(f'downloads/*.{ext}')

        if not files:
            await msg.edit_text('❌ Could not find the audio file after download.')
            return

        filepath = files[0]
        file_size = os.path.getsize(filepath)

        # Telegram limit is 50MB
        if file_size > 50 * 1024 * 1024:
            await msg.edit_text(
                f'⚠️ "{title}" is too large to send.\n'
                f'Try searching for a shorter version!'
            )
            os.remove(filepath)
            return

        await msg.edit_text(f'✅ Found! Sending *{title}*...', parse_mode='Markdown')

        with open(filepath, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=title,
                performer=uploader,
                duration=duration,
                caption=f'🎵 {title}\n👤 {uploader}'
            )

        os.remove(filepath)
        await msg.delete()

    except Exception as e:
        logging.error(f'Song error: {e}')
        await msg.edit_text(
            f'❌ Sorry! Could not find *"{song_name}"*.\n\n'
            f'Tips:\n'
            f'• Check spelling\n'
            f'• Add artist name: /song Levitating Dua Lipa\n'
            f'• Try English name if regional song',
            parse_mode='Markdown'
        )
        # Cleanup any partial downloads
        for f in glob.glob('downloads/*'):
            try:
                os.remove(f)
            except:
                pass


# ─── Chat Response Logic ──────────────────────────────────────
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hi There!'
    if 'how are you' in processed:
        return 'I am fine. How was your day today?'
    if 'fine' in processed:
        return 'Great!!! I will play some songs for you!!!'
    if 'i love musics' in processed or 'i love songs' in processed:
        return (
            'Music is a different world of humans where love, sadness, '
            'loneliness — everything is there. It is another heart of the '
            'human body that sometimes beats according to human feelings.'
        )
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
bot_app.add_handler(CommandHandler('song', song_command))      # 🎵 New!
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
    return '🎵 Xylomutronix Bot is running!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)
