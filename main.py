import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Render kapanmasın diye port dinleyen dummy server
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

# Admin ve Veri Yapıları
ADMIN_ID = 8862145897
kullanici_puanlari = {}
kullanicilar = set()
oyun_durumu = {}

# Bilgi Yarışması Soruları
SORULAR = [
    {"soru": "Türkiye'nin başkenti neresidir?", "siklar": ["İstanbul", "Ankara", "İzmir", "Bursa"], "cevap": "Ankara"},
    {"soru": "Hangi gezegen 'Kızıl Gezegen' olarak bilinir?", "siklar": ["Venüs", "Mars", "Jüpiter", "Satürn"], "cevap": "Mars"},
    {"soru": "Dünyanın en büyük okyanusu hangisidir?", "siklar": ["Atlas", "Hint", "Büyük Okyanus (Pasifik)", "Arktik"], "cevap": "Büyük Okyanus (Pasifik)"},
    {"soru": "İstiklal Marşı'mızın şairi kimdir?", "siklar": ["Mehmet Akif Ersoy", "Ziya Gökalp", "Namık Kemal", "Yahya Kemal"], "cevap": "Mehmet Akif Ersoy"}
]

def puan_ekle(user_id, miktar):
    kullanici_puanlari[user_id] = kullanici_puanlari.get(user_id, 0) + miktar

def ana_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Taş - Kağıt - Makas", callback_data='oyun_tkm'), InlineKeyboardButton("🔢 Sayı Tahmin (1-10)", callback_data='oyun_sayi')],
        [InlineKeyboardButton("🪙 Yazı - Tura", callback_data='oyun_yt'), InlineKeyboardButton("🧠 Bilgi Yarışması", callback_data='oyun_bilgi')],
        [InlineKeyboardButton("🏆 Profilim & Puanım", callback_data='profil'), InlineKeyboardButton("🏠 Anasayfa", callback_data='anasayfa')]
    ])

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    kullanicilar.add(user_id)
    kullanici_adi = update.effective_user.first_name
    
    await update.message.reply_text(
        f"👋 Merhaba {kullanici_adi}!\n\nBotun tüm oyunları ve özellikleri aktif. Aşağıdaki menüden dilediğini seçebilirsin:",
        reply_markup=ana_menu_keyboard()
    )

# Buton İşlemleri
async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    kullanicilar.add(user_id)

    if query.data == 'anasayfa':
        await query.message.reply_text("🏠 Anasayfa Menüsü:", reply_markup=ana_menu_keyboard())

    elif query.data == 'profil':
        puan = kullanici_puanlari.get(user_id, 0)
        await query.message.reply_text(f"👤 **Profil Bilgilerin**\n\n⭐ Toplam Puanın: **{puan} XP**\n\nOyunları kazanarak puanını artırabilirsin!", reply_markup=ana_menu_keyboard())

    # Taş Kağıt Makas
    elif query.data == 'oyun_tkm':
        tkm_keyboard = InlineKeyboardMarkup([[ 
            InlineKeyboardButton("🪨 Taş", callback_data='tkm_tas'),
            InlineKeyboardButton("📄 Kağıt", callback_data='tkm_kagit'),
            InlineKeyboardButton("✂️ Makas", callback_data='tkm_makas')
        ]])
        await query.message.reply_text("Hamleni seç:", reply_markup=tkm_keyboard)

    elif query.data.startswith('tkm_'):
        kullanici_hamle = query.data.split('_')[1]
        bot_hamle = random.choice(['tas', 'kagit', 'makas'])
        emoji_map = {'tas': '🪨 Taş', 'kagit': '📄 Kağıt', 'makas': '✂️ Makas'}
        
        if kullanici_hamle == bot_hamle:
            sonuc = "Berabere! 🤝"
        elif (kullanici_hamle == 'tas' and bot_hamle == 'makas') or \
             (kullanici_hamle == 'kagit' and bot_hamle == 'tas') or \
             (kullanici_hamle == 'makas' and bot_hamle == 'kagit'):
            sonuc = "Tebrikler, sen kazandın! (+10 XP) 🎉"
            puan_ekle(user_id, 10)
        else:
            sonuc = "Ben kazandım! 🤖"

        await query.message.reply_text(f"Senin hamlen: {emoji_map[kullanici_hamle]}\nBenim hamlem: {emoji_map[bot_hamle]}\n\n👉 **{sonuc}**", reply_markup=ana_menu_keyboard())

    # Sayı Tahmin
    elif query.data == 'oyun_sayi':
        oyun_durumu[user_id] = {'tip': 'sayi', 'hedef': random.randint(1, 10)}
        await query.message.reply_text("1 ile 10 arasında bir sayı tuttum! Tahminini yaz bakalım:")

    # Yazı Tura
    elif query.data == 'oyun_yt':
        yt_keyboard = InlineKeyboardMarkup([[ 
            InlineKeyboardButton("🪙 Yazı", callback_data='yt_Yazı'),
            InlineKeyboardButton("👑 Tura", callback_data='yt_Tura')
        ]])
        await query.message.reply_text("Yazı mı Tura mı?", reply_markup=yt_keyboard)

    elif query.data.startswith('yt_'):
        secim = query.data.split('_')[1]
        gelen = random.choice(["Yazı", "Tura"])
        if secim == gelen:
            puan_ekle(user_id, 5)
            await query.message.reply_text(f"🪙 Parayı attım... **{gelen}** geldi!\n\n🎉 Doğru tahmin! (+5 XP)", reply_markup=ana_menu_keyboard())
        else:
            await query.message.reply_text(f"🪙 Parayı attım... **{gelen}** geldi!\n\n😅 Maalesef bilemedin.", reply_markup=ana_menu_keyboard())

    # Bilgi Yarışması
    elif query.data == 'oyun_bilgi':
        soru_obj = random.choice(SORULAR)
        oyun_durumu[user_id] = {'tip': 'bilgi', 'cevap': soru_obj['cevap']}
        
        secenekler = soru_obj['siklar'].copy()
        random.shuffle(secenekler)
        
        butonlar = [[InlineKeyboardButton(sec, callback_data=f"bilgi_{sec}")] for sec in secenekler]
        await query.message.reply_text(f"❓ **Soru:** {soru_obj['soru']}", reply_markup=InlineKeyboardMarkup(butonlar))

    elif query.data.startswith('bilgi_'):
        secilen = query.data.split('_')[1]
        durum = oyun_durumu.get(user_id)
        
        if durum and durum.get('tip') == 'bilgi':
            dogru = durum['cevap']
            if secilen == dogru:
                puan_ekle(user_id, 15)
                await query.message.reply_text(f"🎉 **Doğru Cevap!** Tebrikler (+15 XP)", reply_markup=ana_menu_keyboard())
            else:
                await query.message.reply_text(f"❌ **Yanlış!** Doğru cevap: **{dogru}** olmalıydı.", reply_markup=ana_menu_keyboard())
            del oyun_durumu[user_id]

# Mesaj Dinleyici & Sayı Tahmin Oyunu
async def mesaj_yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    kullanicilar.add(user_id)
    metin = update.message.text.strip().lower()

    if user_id in oyun_durumu and oyun_durumu[user_id].get('tip') == 'sayi':
        if metin.isdigit():
            tahmin = int(metin)
            hedef = oyun_durumu[user_id]['hedef']
            
            if tahmin == hedef:
                puan_ekle(user_id, 10)
                await update.message.reply_text(f"🎉 BİNGÖR! Doğru tahmin! Tuttuğum sayı {hedef} idi. (+10 XP)", reply_markup=ana_menu_keyboard())
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
        await update.message.reply_text("Mesajını aldım! Menüyü açmak için /start yazabilirsin.")

# Admin Duyuru Komutu (/duyuru Mesajınız)
async def duyuru_gonder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bu komutu sadece bot yöneticisi kullanabilir.")
        return

    mesaj = " ".join(context.args)
    if not mesaj:
        await update.message.reply_text("Kullanımı: `/duyuru Göndermek İstediğiniz Mesaj`")
        return

    basarili = 0
    for uid in kullanicilar:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **YÖNETİCİ DUYURUSU**\n\n{mesaj}")
            basarili += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Duyuru toplam **{basarili}** kullanıcıya ulaştırıldı.")

if __name__ == '__main__':
    t = threading.Thread(target=run_dummy_server)
    t.daemon = True
    t.start()

    TOKEN = "8856132052:AAHSIUBsi4IaA-tul1LWBCtU2hBM0iqt7vI"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru_gonder))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_yanitla))

    print("Dev bot yayında...")
    app.run_polling(drop_pending_updates=True)
