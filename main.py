import os
from flask import Flask
from threading import Thread
import telebot

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and responding!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# توكن البوت الخاص بك
API_TOKEN = "9012577606:AAGr1v1QedPchUjRmebM_aGFcsNH6e9pRFY"
bot = telebot.TeleBot(API_TOKEN)

# أمر البداية للتأكد من تفاعل البوت معك فوراً
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! البوت يعمل الآن ويتفاعل معك بنجاح 🚀\nأرسل لي أي كلمة للتجربة.")

# استقبال أي رسالة نصية والرد عليها فوراً لتأكيد الاستجابة
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"لقد استقبلت رسالتك: {message.text} ✅")

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()
