import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render'ın port kontrolünü geçmek için minik web sunucusu
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

# Telegram Bot Kodları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Bot 7/24 aktif olarak çalışıyor 🚀")

async def mesaj_yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "sa" in text or "selam" in text:
        await update.message.reply_text("Aleyküm selam, hoş geldin!")
    elif "nasılsın" in text:
        await update.message.reply_text("Harikayım, sen nasılsın?")
    else:
        await update.message.reply_text("Mesajını aldım!")

if __name__ == '__main__':
    # Web sunucusunu arka planda başlat
    t = threading.Thread(target=run_dummy_server)
    t.daemon = True
    t.start()

    TOKEN = "8856132052:AAHSIUBsi4IaA-tul1LWBCtU2hBM0iqt7vI"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_yanitla))

    print("Bot sunucuda çalışıyor...")
    app.run_polling(drop_pending_updates=True)
