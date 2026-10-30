import os
import telebot
from yt_dlp import YoutubeDL

# ضع توكن البوت الخاص بك هنا بين علامتي التنصيص
API_TOKEN = "ضع_التوكن_هنا"
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الموسيقى! أرسل لي اسم الأغنية أو الرابط 🎵. وسأقوم بتحميلها لك مجاناً.")

@bot.message_handler(func=lambda message: True)
def download_and_send_audio(message):
    query = message.text
    chat_id = message.chat.id

    # إرسال رسالة جاري البحث
    status_msg = bot.send_message(chat_id, "🔍 جاري البحث والتحميل، انتظر لحظة...")

    try:
        # إعدادات تحميل الصوت وتحويله إلى MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'default_search': 'ytsearch',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            filename = ydl.prepare_filename(info)
            audio_file = filename.rsplit(".", 1)[0] + ".mp3"

        # إرسال الملف الصوتي إلى المستخدم
        with open(audio_file, 'rb') as audio:
            bot.send_audio(chat_id, audio)

        # حذف الملف من السيرفر لتوفير المساحة
        os.remove(audio_file)
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}", chat_id, status_msg.message_id)

if __name__ == '__main__':
    bot.infinity_polling()
