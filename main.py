import os
import telebot
from yt_dlp import YoutubeDL

# ضع رمز التوكن الخاص بك هنا بين العلامتين
API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎵 أهلاً بك في بوت الموسيقى! أرسل لي اسم الأغنية أو الرابط وسأقوم بتحميلها لك مجاناً.")

@bot.message_handler(func=lambda message: True)
def download_and_send_audio(message):
    query = message.text
    chat_id = message.chat.id
    
    # إرسال رسالة جاري البحث
    status_msg = bot.send_message(chat_id, "🔍 جاري البحث والتحميل، انتظر لحظة...")
    
    # إعدادات تحميل الصوت فقط وتحويله إلى MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch',
        'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # البحث والتحميل
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            title = video_info.get('title', 'audio')
            
            # العثور على الملف المحمل في المجلد
            filename = None
            for file in os.listdir('downloads'):
                if file.startswith(str(chat_id)):
                    filename = os.path.join('downloads', file)
                    break
            
            if filename and os.path.exists(filename):
                # إرسال الملف الصوتي للمستخدم
                with open(filename, 'rb') as audio:
                    bot.send_audio(chat_id, audio, caption=f"🎵 {title}")
                # حذف الملف بعد الإرسال لتوفير المساحة
                os.remove(filename)
                bot.delete_message(chat_id, status_msg.message_id)
            else:
                bot.edit_message_text("❌ عذراً، تعذر تحويل الملف الصوتي.", chat_id, status_msg.message_id)
                
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ حدث خطأ أثناء محاولة البحث أو التحميل. تأكد من الاسم أو الرابط.", chat_id, status_msg.message_id)

if name == 'main':
    # إنشاء مجلد التحميلات إذا لم يكن موجوداً
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    print("البوت يعمل الآن بنجاح...")
    bot.infinity_polling()
