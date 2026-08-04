import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

oyun_durumu = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kullanici_adi = update.effective_user.first_name
    
    keyboard = [
        [InlineKeyboardButton("🎮 Taş - Kağıt - Makas", callback_data='oyun_tkm')],
        [InlineKeyboardButton("🔢 Sayı Tahmin Oyunu (1-10)", callback_data='oyun_sayi')],
        [InlineKeyboardButton("🏠 Anasayfa", callback_data='anasayfa')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Merhaba {kullanici_adi}!\n\nOynamak istediğin oyunu veya menüyü seç:",
        reply_markup=reply_markup
    )

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'oyun_tkm':
        tkm_keyboard = [
            [InlineKeyboardButton("🪨 Taş", callback_data='tkm_tas'),
             InlineKeyboardButton("📄 Kağıt", callback_data='tkm_kagit'),
             InlineKeyboardButton("✂️ Makas", callback_data='tkm_makas')]
        ]
        await query.message.reply_text("Hamleni seç:", reply_markup=InlineKeyboardMarkup(tkm_keyboard))

    elif query.data.startswith('tkm_'):
        kullanici_hamle = query.data.split('_')[1]
        bot_hamle = random.choice(['tas', 'kagit', 'makas'])
        
        emoji_map = {'tas': '🪨 Taş', 'kagit': '📄 Kağıt', 'makas': '✂️ Makas'}
        
        if kullanici_hamle == bot_hamle:
            sonuc = "Berabere! 🤝"
        elif (kullanici_hamle == 'tas' and bot_hamle == 'makas') or \
             (kullanici_hamle == 'kagit' and bot_hamle == 'tas') or \
             (kullanici_hamle == 'makas' and bot_hamle == 'kagit'):
            sonuc = "Tebrikler, sen kazandın! 🎉"
        else:
            sonuc = "Ben kazandım! 🤖"

        await query.message.reply_text(
            f"Senin hamlen: {emoji_map[kullanici_hamle]}\n"
            f"Benim hamlem: {emoji_map[bot_hamle]}\n\n"
            f"👉 **{sonuc}**"
        )

    elif query.data == 'oyun_sayi':
        hedef_sayi = random.randint(1, 10)
        oyun_durumu[user_id] = hedef_sayi
        await query.message.reply_text("1 ile 10 arasında bir sayı tuttum! Tahminini mesaj olarak yaz bakalım:")

    elif query.data == 'anasayfa':
        await query.message.reply_text("Anasayfadasın. /start yazarak menüyü tekrar açabilirsin.")

async def mesaj_yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    metin = update.message.text.strip().lower()

    if user_id in oyun_durumu:
        if metin.isdigit():
            tahmin = int(metin)
            hedef = oyun_durumu[user_id]
            
            if tahmin == hedef:
                await update.message.reply_text(f"🎉 BİNGÖR! Doğru tahmin! Tuttuğum sayı {hedef} idi.")
                del oyun_durumu[user_id]
            elif tahmin < hedef:
                await update.message.reply_text("Daha BÜYÜK bir sayı söyle! ⬆️")
            else:
                await update.message.reply_text("Daha KÜÇÜK bir sayı söyle! ⬇️")
            return
        else:
            await update.message.reply_text("Lütfen sadece bir sayı yaz!")
            return

    selamlar = ["sa", "selam", "selamün aleyküm", "selamun aleykum", "sa."]
    
    if metin in selamlar:
        await update.message.reply_text("Aleyküm selam, hoş geldin!")
    elif "nasılsın" in metin or "nasilsin" in metin:
        await update.message.reply_text("Harikayım, sen nasılsın?")
    else:
        await update.message.reply_text("Mesajını aldım! Oyun oynamak için /start yazabilirsin.")

if __name__ == '__main__':
    t = threading.Thread(target=run_dummy_server)
    t.daemon = True
    t.start()

    TOKEN = "8856132052:AAHSIUBsi4IaA-tul1LWBCtU2hBM0iqt7vI"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_yanitla))

    print("Bot yayında...")
    app.run_polling(drop_pending_updates=True)

