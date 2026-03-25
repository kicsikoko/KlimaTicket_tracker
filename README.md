# 🚆 KlimaTicket ROI Tracker Bot

A Python-based Telegram bot designed to track public transport journeys and calculate the Return on Investment (ROI) for the Austrian **Klimaticket**. 

This bot allows users to seamlessly log their daily commutes (e.g., between Wien and Linz), track custom routes, and visualize their savings over time using dynamically generated charts.

## ✨ Features

* **Quick Logging:** One-click buttons to log frequent routes.
* **Custom Trips:** Interactive dialogue to record any origin, destination, and ticket price.
* **Data Analytics & Visualization:**
    * `📊 Stats`: Text-based monthly and annual progress bars.
    * `📈 Trend`: Matplotlib-generated linear regression and cumulative ROI forecasting.
    * `🍕 Pie Chart`: Visual distribution of the most profitable routes.
    * `📉 Chart`: Bar chart showing monthly savings against the standard monthly pass cost.
* **Data Export:** Download the entire trip history as a clean CSV file for further Data Science or ETL processing.
* **Robust Error Handling:** Built-in connection retries and clean exit handling for stable long-polling.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Bot Framework:** `pyTelegramBotAPI` (telebot)
* **Database:** `SQLite3` (via custom `db_manager.py`)
* **Data Visualization:** `matplotlib` (running in 'Agg' backend for headless server environments)
* **Environment Management:** `python-dotenv`

## 🚀 Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/KlimaTicket_tracker.git](https://github.com/yourusername/KlimaTicket_tracker.git)
cd KlimaTicket_tracker
```
Set up a virtual environment:
```bash
python -m venv venv
```
# On Windows (PowerShell):
```bash
.\venv\Scripts\Activate.ps1
```
# On Linux/Mac:
```bash
source venv/bin/activate
```
(Note for Windows users: If you encounter an Execution Policy error, run Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser in PowerShell).

3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Configure Environment Variables:
Create a .env file in the root directory and add your Telegram Bot Token:
```bash
TG_TOKEN=your_telegram_bot_token_here
```
5. Run the bot:

```bash
python bot.py
```
📱 Bot Commands
/start - Initialize the bot and show the main keyboard interface.

/stats - Display text-based ROI statistics and progress bars.

/history - Show the last 5 recorded trips.

/chart - Generate a bar chart of monthly savings.

/trend - Generate a cumulative savings trendline and break-even projection.

/piechart - Show the distribution of savings by route.

/predict - Calculate the predicted final savings for the current Klimaticket cycle.

/export - Download the SQLite database records as a CSV file.

🗄️ Database Structure
The project uses a lightweight SQLite database (klimaticket.db) initialized automatically on the first run. It stores:

id (Primary Key)

date (Timestamp)

origin (String)

destination (String)

price (Float)

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


***
