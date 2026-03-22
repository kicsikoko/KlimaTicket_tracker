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

klimaticket_full_price = 1300
klimaticket_monthly_price = 108.33
singleticket_price = 20.90

db_manager.init_db() #Creating the DB at start

@bot.message_handler(commands=['start'])
def send_welcome(message):
    #Creating Buttons
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Wien -> Linz')
    itembtn2 = types.KeyboardButton('Linz -> Wien')
    itembtn3 = types.KeyboardButton('🔙 Undo last trip')
    itembtn4 = types.KeyboardButton('📜 History')
    itembnt5 = types.KeyboardButton('➕ Other (Custom)')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembnt5)

    bot.reply_to(message, "Which route should be registered?", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def show_stats(message):

    #Total data
    total_res = db_manager.get_stats()
    total_saved = total_res[0] if total_res and total_res[0] else 0
    total_count = total_res[1] if total_res and total_res[1] else 0

    #Monthly data
    monthly_res = db_manager.get_monthly_stats()
    m_saved = monthly_res[0] if monthly_res and monthly_res[0] else 0
    m_count = monthly_res[1] if monthly_res and monthly_res[1] else 0

    #Progress bar
    percent = min(int((m_saved / klimaticket_full_price) * 100), 100)
    bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))

    remaining_annual = klimaticket_full_price - total_saved
    if remaining_annual > 0:
        trips_left = int(remaining_annual / singleticket_price) + 1
        annual_status = f"📉 **{remaining_annual:.2f} €** is needed and ({trips_left} is left)."
    else:
        annual_status = f"🥳 **A bérlet visszahozta az árát!** (+{abs(remaining_annual):.2f} €)"

    response = (
        f"📊 Klimaticket Statistics:\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📅 *This month:*\n"
        f"🚊 Number of trips: {m_count} | Saved already: {m_saved:.2f}€\n"
        f"[{bar}] {percent}%\n"
        f"_{'✅ Monthly goal achieved!' if m_saved >= klimaticket_monthly_price else 'Has not yet been paid off.'}_\n\n"
        f"💰 Total Annual Savings:"
        f"Total trips: {total_count}\n"
        f" Savings so far: *{total_saved:.2f} €*\n"
    )

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['history'])
def show_history(message):
    trips = db_manager.get_recent_trips(5)

    if not trips:
        bot.reply_to(message, "📭 Még nincsenek rögzített utazásaid.")
        return
    
    history_text = "📜 *Legutóbbi 5 utazásod:*\n\n"

    for trip in trips:
        #trip[0] = dátum, trip[1] = honnan, trip[2] = hova, trip[3] = ár
        date_only = trip[0].split()[0]
        history_text += f"📅 {date_only} | {trip[1]} ➡️ {trip[2]} | *{trip[3]:.2f}€*\n"
    
    bot.reply_to(message, history_text, parse_mode='Markdown')

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
    elif message.text == '🔙 Undo last trip':
        db_manager.delete_last_trip()
        bot.reply_to(message, "🗑️ Last one deleted!")
    elif message.text == '📜 History':
        show_history(message)
    elif message.text == '➕ Other (Custom)':
        ask_from(message)

if __name__ == "__main__":
    print("Bot has started...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Error Occured: {e}")

# 1. Ask 'From where'
def ask_from(message):
    msg = bot.send_message(message.chat.id, "📍 Departure?")
    bot.register_next_step_handler(msg, ask_to)

# 2. Ask 'To where'
def ask_to(message):
    origin = message.text
    msg = bot.send_message(message.chat.id, f"🏁 All right, {origin} -> arrival?")
    bot.register_next_step_handler(msg, ask_price, origin)

# 3. Ask about price
def ask_price(message, origin):
    destination = message.text
    msg = bot.send_message(message.chat.id, f"💰 How much would it be {origin} between {destination}?")
    bot.register_next_step_handler(msg, save_other_trip, origin, destination)

# 4. Save to database
def save_other_trip(message, origin, destination):
    try:
        price = float(message.text.replace(',', '.')) #Handle comma and dot
        db_manager.log_trip(origin, destination, price)
        bot.send_message(message.chat.id, f"✅ Sucessfully added: {origin} -> {destination} ({price} €)")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Error! Please only number for price value. Retry 'Other' button!")