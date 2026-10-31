import os
import telebot
from flask import Flask, request

# ضع التوكن الخاص ببوتك هنا أو استخدم متغيرات البيئة (Environment Variables)
TOKEN = os.environ.get('9012577606:AAGr1v1QeDpcHuJRmebM_aGFcsNH6e9pRFY
')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# رابط موقعك على Render الذي يظهر في السجلات
# مثال: https://weary-wraith.onrender.com
RENDER_URL = "https://weary-wraith.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

# إستقبال الرسائل من تيليجرام
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
    return "Bot is running smoothly!", 200

# الرد على رسالة /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! البوت يعمل الآن بنجاح على منصة Render 🚀")

# الرد على أي نص عادي
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"أهلاً بك، لقد استلمت رسالتك: {message.text}")

if __name__ == "__main__":
    # إزالة أي Webhook قديم وتعيين الرابط الجديد
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    
    # تشغيل تطبيق Flask بالمنفذ المطلوب من المنصة
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
