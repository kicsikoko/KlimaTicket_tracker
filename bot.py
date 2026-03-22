import os
import telebot
from telebot import types
from dotenv import load_dotenv
import db_manager

#Load env variables and read the token
load_dotenv()
TOKEN = os.getenv('TG_TOKEN')
print(f"DEBUG: Betöltött token vége: ...{TOKEN[-4:] if TOKEN else 'NINCS TOKEN'}")
#Check if it's succesful(if not, stop it)
if not TOKEN:
    raise ValueError("Oops! No TG_TOKEN in the .env file!")

bot = telebot.TeleBot(TOKEN)

db_manager.init_db() #Creating the DB at start

@bot.message_handler(commands=['start'])
def send_welcome(message):
    #Creating Buttons
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Wien -> Linz')
    itembtn2 = types.KeyboardButton('Linz -> Wien')
    itembtn3 = types.KeyboardButton('🔙 Undo last trip')
    markup.add(itembtn1, itembtn2, itembtn3)

    bot.reply_to(message, "Which route should be registered?", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def show_stats(message):
    result = db_manager.get_stats()

    #result[0] az összeg (SUM), result[1] a darabszám (COUNT)
    total_saved = result[0] if result[0] else 0
    trip_count = result[1] if result[1] else 0

    response = (
        f"📊 Klimaticket Statistics:\n\n"
        f"🚊 Number of trips: {trip_count}\n"
        f"💰 Total Savings: {total_saved:.2f} €\n"
        
    )

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Wien -> Linz':
        price = db_manager.get_price('Wien->Linz')
        db_manager.log_trip('Wien', 'Linz', price) 
        bot.reply_to(message, f"✅ Added: Wien -> Linz (Spared: {price}€)")
    elif message.text == 'Linz -> Wien':
        price = db_manager.get_price('Linz->Wien')
        db_manager.log_trip('Linz', 'Wien', price)
        bot.reply_to(message, f"✅ Added: Wien -> Linz (Spared: {price}€)")
    elif message.text == '🔙 Undone':
        db_manager.delete_last_trip()
        bot.reply_to(message, "🗑️ Last one deleted!")

#bot.polling()
if __name__ == "__main__":
    print("Bot has started...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Error Occured: {e}")