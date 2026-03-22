import os
import csv
import telebot
from telebot import types
from dotenv import load_dotenv
import db_manager
import matplotlib.pyplot as plt
import io
from datetime import datetime

#Load env variables and read the token
load_dotenv()
TOKEN = os.getenv('TG_TOKEN')
print(f"DEBUG: Loaded token ending: ...{TOKEN[-4:] if TOKEN else 'NO TOKEN'}")
#Check if it's succesful(if not, stop it)
if not TOKEN:
    raise ValueError("Oops! No TG_TOKEN in the .env file!")

bot = telebot.TeleBot(TOKEN)

klimaticket_full_price = 1300
klimaticket_monthly_price = 108.33
singleticket_price = 20.90

db_manager.init_db() #Creating the DB at start

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

@bot.message_handler(commands=['export'])
def export_to_csv(message):
    trips = db_manager.get_all_trips()

    if not trips:
        bot.reply_to(message, "📭 No data to export - database is empty.")
        return
    
    file_name = "klimaticket_export.csv"

    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Origin', 'Destination', 'Price Saved (€)'])
        writer.writerows(trips)

    with open (file_name, 'rb') as doc:
        bot.send_document(message.chat.id, doc, caption="📊 Here is your total trip log in csv format!")

    os.remove(file_name) #Cleaning

def get_current_pass_start():
    today = datetime.now()
    #Pass last day is Oktober 6
    #If it's already passed 6th of Oct then this year 6th of October is the start
    #if not still last year's 6th of Oct
    if today.month > 10 or (today.month == 10 and today.day >= 6):
        start_year = today.year
    else:
        start_year = today.year -1

    return f"{start_year}-10-06"

@bot.message_handler(commands=['stats'])
def show_stats(message):

    current_cycle_start = get_current_pass_start()
    total_res = db_manager.get_stats(current_cycle_start)
    total_saved = total_res[0] if total_res and total_res[0] else 0
    total_count = total_res[1] if total_res and total_res[1] else 0

    #Monthly data
    monthly_res = db_manager.get_monthly_stats()
    m_saved = monthly_res[0] if monthly_res and monthly_res[0] else 0
    m_count = monthly_res[1] if monthly_res and monthly_res[1] else 0

    #Progress bar
    annual_percent = min(int((total_saved / klimaticket_full_price) * 100), 100)
    annual_bar = "█" * (annual_percent // 10) + "░" * (10 - (annual_percent // 10))

    m_profit = max(0, m_saved - klimaticket_monthly_price)
    monthly_percent = min(int((m_saved / klimaticket_monthly_price) * 100), 100)
    monthly_bar = "█" * (monthly_percent // 10) + "░" * (10 - (monthly_percent // 10))

    remaining_annual = klimaticket_full_price - total_saved
    if remaining_annual > 0:
        trips_left = int(remaining_annual / singleticket_price) + 1
        annual_status = f"📉 **{remaining_annual:.2f} €** is needed and ({trips_left} is left)."
    else:
        annual_status = f"🥳 **The pass already paid off!** (+{abs(remaining_annual):.2f} €)"

    response = (
        f"📊 Klimaticket Statistics:\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📅 *This month:*\n"
        f"🚊 Number of trips: {m_count} | Saved already: {m_profit:.2f}€\n"
        f"[{monthly_bar}] {monthly_percent}%\n"
        f"_{'✅ Monthly goal achieved!' if m_saved >= klimaticket_monthly_price else 'Has not yet been paid off.'}_\n\n"
        f"💰 Total Annual Savings:\n"
        f"Total trips: {total_count}\n"
        f"[{annual_bar}] {annual_percent}%\n\n"
        f" Savings so far: *{total_saved:.2f} €* / {klimaticket_full_price} €\n"
        f"\n\n 🔄 Current pass cycle: {current_cycle_start}"
    )

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['history'])
def show_history(message):
    trips = db_manager.get_recent_trips(5)

    if not trips:
        bot.reply_to(message, "📭 There is no recorded data yet.")
        return
    
    history_text = "📜 *Last 5 trips:*\n\n"

    for trip in trips:
        #trip[0] = dátum, trip[1] = honnan, trip[2] = hova, trip[3] = ár
        date_only = trip[0].split()[0]
        history_text += f"📅 {date_only} | {trip[1]} ➡️ {trip[2]} | *{trip[3]:.2f}€*\n"
    
    bot.reply_to(message, history_text, parse_mode='Markdown')

@bot.message_handler(commands=['chart'])
def send_chart(message):
    data = db_manager.get_data_for_chart()
    
    if not data:
        bot.reply_to(message, "📭 Not enough data to create chart.")
        return

    months = [row[0] for row in data]
    savings = [row[1] for row in data]

    # --- Matplotlib varázslat ---
    plt.figure(figsize=(10, 6))
    bars = plt.bar(months, savings, color='skyblue', edgecolor='navy')
    
    # Havi bérlet ára (vízszintes vonal)
    plt.axhline(y=108.33, color='red', linestyle='--', label='Monthly Cost (108.33 €)')
    
    # Design finomhangolás
    plt.title('Monthly Klimaticket Savings', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Euro (€)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.7)

    # Értékek kiírása az oszlopok tetejére
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.0f}€', ha='center', va='bottom')

    # Kép mentése memóriába (fájl helyett)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close() # Fontos, hogy ne fogyassza a RAM-ot!

    bot.send_photo(message.chat.id, buf, caption="📊 Here is your monthly breakdown. Above the red line is pure profit!")

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