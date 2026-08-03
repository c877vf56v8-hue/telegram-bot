from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Merhaba {user_name}! Ben senin botunum, nasıl yardımcı olabilirim?")

async def mesaj_yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gelen_mesaj = update.message.text.lower()

    if "sa" in gelen_mesaj or "selam" in gelen_mesaj:
        await update.message.reply_text(f"Aleyküm selam {update.effective_user.first_name}, hoş geldin!")
    elif "nasılsın" in gelen_mesaj:
        await update.message.reply_text("İyiyim, teşekkürler! Sen nasılsın?")
    elif "neredesin" in gelen_mesaj or "nerdesin" in gelen_mesaj:
        await update.message.reply_text("Bulutların üzerindeyim ☁️")
    else:
        await update.message.reply_text("Bu söylediğini henüz anlayamıyorum!")

if __name__ == '__main__':
    TOKEN = "8856132052:AAHSIUBsi4IaA-tul1LWBCtU2hBM0iqt7vI"
    
    request = HTTPXRequest(connect_timeout=20.0, read_timeout=20.0)
    app = ApplicationBuilder().token(TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_yanitla))

    print("Bot sunucuda çalışıyor...")
    aapp.run_polling(drop_pending_updates=True)

