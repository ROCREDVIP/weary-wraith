import os
import telebot
from flask import Flask, request
import yt_dlp

# 1. إعدادات بوت تيليجرام وتطبيق Flask
TOKEN = os.environ.get('9012577606:AAGr1v1QeDpcHuJRmebM_aGFcsNH6e9pRFY')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

RENDER_URL = "https://weary-wraith.onrender.com"  # رابط موقعك على Render
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

# 2. إعدادات التحميل المتقدمة لتجاوز حظر يوتيوب (Sign in to confirm...)
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'extractor_args': {
        'youtube': {
            'player_client': ['mweb', 'ios'],
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# استقبال رسائل تيليجرام عبر Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid data", 403

# الصفحة الرئيسية للتأكد أن السيرفر يعمل
@app.route('/')
def index():
    return "Bot is running and ready!", 200

# أمر البدء /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الموسيقى! أرسل لي اسم الأغنية أو الرابط، وسأقوم بتحميلها لك مجاناً 🎶")

# معالجة النصوص والبحث والتحميل
@bot.message_handler(func=lambda message: True)
def download_audio(message):
    query = message.text
    sent_msg = bot.reply_to(message, "⏳ جاري البحث والتحميل، يرجى الانتظار...")
    
    try:
        # البحث والتحميل باستخدام yt_dlp
        search_query = f"ytsearch:{query}" if not query.startswith("http") else query
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)
            mp3_file = base + ".mp3"
            
        # إرسال الملف الصوتي للمستخدم
        with open(mp3_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title', 'Audio'))
            
        bot.delete_message(message.chat.id, sent_msg.message_id)
        
        # تنظيف الملفات المؤقتة من السيرفر
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل:\n`{str(e)}`", message.chat.id, sent_msg.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    # إزالة أي ربط قديم وتعيين الويب هوك الجديد
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    
    # تشغيل السيرفر بالمنفذ الخاص بمنصة Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
