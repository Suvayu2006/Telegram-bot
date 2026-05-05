import asyncio
from telegram import Bot

TOKEN = '8154854350:AAE5IH4svWa9_964SI9fPqbK0R8YSNJEPkYE'
# Replace with your actual Render URL after deploying
WEBHOOK_URL = 'https://your-app-name.onrender.com'

async def set_webhook():
    bot = Bot(token=TOKEN)
    await bot.initialize()
    result = await bot.set_webhook(url=f'{WEBHOOK_URL}/{TOKEN}')
    if result:
        print(f'✅ Webhook set successfully!')
    else:
        print('❌ Failed to set webhook')

asyncio.run(set_webhook())
