import os
from flask import Flask
from threading import Thread
import telebot
from yt_dlp import YoutubeDL

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# توكن البوت الخاص بك
API_TOKEN = "9012577606:AAGr1v1QedPchUjRmebM_aGFcsNH6e9pRFY"
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الموسيقى! 🎵\nأرسل اسم الأغنية أو الرابط للتحميل مباشرة.")

@bot.message_handler(func=lambda message: True)
def download_and_send_audio(message):
    query = message.text
    chat_id = message.chat.id
    
    status_msg = bot.send_message(chat_id, "🔍 جاري البحث والتحميل، انتظر لحظة 🎧...")
    
    audio_file = None
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'default_search': 'ytsearch',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'extractor_args': {'youtube': {'player_client': ['web', 'ios', 'android']}},
            'geo_bypass': True,
            'nocheckcertificate': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]

            filename = ydl.prepare_filename(info)
            audio_file = filename.rsplit(".", 1)[0] + ".mp3"

        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_audio(chat_id, audio)
            bot.delete_message(chat_id, status_msg.message_id)
        else:
            raise Exception("فشل في معالجة الملف الصوتي.")

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل:\n{str(e)}", chat_id, status_msg.message_id)

    finally:
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass


    if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

