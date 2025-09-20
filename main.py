import telebot
import time
import threading
from collections import defaultdict

API_TOKEN = ''

bot = telebot.TeleBot(API_TOKEN)


user_activity = defaultdict(list)
banned_users = {}

user_chat_ids = {}

# Настройки антиспама
MAX_MESSAGES = 5  # макс до бана
TIME_WINDOW = 6  # в течении скольки времени
BAN_DURATION = 6  # время на бан

def check_unbans():\
    while True:
        try:
            current_time = time.time()
            users_to_unban = []
            
            # находим пользователей, у которых истек бан
            for user_id, ban_time in list(banned_users.items()):
                if current_time - ban_time >= BAN_DURATION:
                    users_to_unban.append(user_id)
            
            # разбаниваем и отправляем уведомления
            for user_id in users_to_unban:
                if user_id in user_chat_ids:
                    try:
                        bot.send_message(user_chat_ids[user_id], "ты был разбанен по истечении своего срока")
                        print(f"USER UNBANNED: ID {user_id}")
                    except Exception as e:
                        print(f"error sending unban message to {user_id}: {e}")
                
                # очистка данных пользователя
                if user_id in banned_users:
                    del banned_users[user_id]
                if user_id in user_activity:
                    del user_activity[user_id]
                if user_id in user_chat_ids:
                    del user_chat_ids[user_id]
            
            time.sleep(5)  # проверяем каждые 5 секунд
            
        except Exception as e:
            print(f"error in check_unbans: {e}")
            time.sleep(10)

def is_user_banned(user_id): #проверка на бан
    return user_id in banned_users and time.time() - banned_users[user_id] < BAN_DURATION

def check_spam(user_id): # проверка на спам
    current_time = time.time()
    
    # убирает старые соо
    user_activity[user_id] = [t for t in user_activity[user_id] if current_time - t < TIME_WINDOW]
    
    # добавление
    user_activity[user_id].append(current_time)
    
    # проверка лимита
    return len(user_activity[user_id]) > MAX_MESSAGES

def ban_user(user_id, chat_id):
    banned_users[user_id] = time.time()
    user_chat_ids[user_id] = chat_id  # сохранение chat_id для уведомления о разбане

@bot.message_handler(commands=['start'])
def startstart(message):
    user_id = message.from_user.id
    
    if is_user_banned(user_id):
        bot.reply_to(message, "ты забанен. подожди немного")
        return
        
    bot.reply_to(message, "привет, этот бот был создан для того, чтобы меня пинговать через мою систему, телеграм часто у меня выключен и поэтому я вряд ли увижу ваше сообщение в ближайшее время, для более быстрого моего ответа вы можете написать мне сюда, этот бот пока что тестируется и потом тут будет ещё много чево для меня хз зачем тебе эта информация, чтобы передать мне сообщение в следующем сообщении напиши что-нибудь и я его увижу из под системы, удачи")

@bot.message_handler(func=lambda message: message.text.lower() == 'тест')
def send_test_response(message):
    user_id = message.from_user.id
    
    if is_user_banned(user_id):
        bot.reply_to(message, "ты забанен. подожди немного")
        return
        
    if check_spam(user_id):
        ban_user(user_id, message.chat.id)
        bot.reply_to(message, "автобан за спам на 10 минут")
        print(f"SPAM BAN: ID {user_id} UN @{message.from_user.username if message.from_user.username else 'none'} Name {message.from_user.first_name or 'None'}")
        return
    
    bot.reply_to(message, "а?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    user = message.from_user
    
    if is_user_banned(user_id):
        bot.reply_to(message, "бан.подождите немного.")
        return
    
    if check_spam(user_id):
        ban_user(user_id, message.chat.id)
        bot.reply_to(message, "автобан за спам на 10 минут")
        print(f"SPAM BAN: ID {user_id} UN @{user.username if user.username else 'none'} Name {user.first_name or 'None'}")
        return
    
    console_output = f"ID {user.id} UN @{user.username if user.username else 'none'} Name {user.first_name or 'None'}: {message.text}"
    print(console_output)
    bot.reply_to(message, f"сообщение отправлено в zsh: '{message.text}'")

unban_thread = threading.Thread(target=check_unbans, daemon=True)
unban_thread.start()

print("ожидает...")
bot.infinity_polling()