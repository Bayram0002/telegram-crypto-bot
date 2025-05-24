import ccxt
import mplfinance as mpf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
import os
import pandas as pd

# MEXC birjası
exchange = ccxt.mexc()

interval_map = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d"
}

# /zz əmri – şam qrafiki
async def zz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("İstifadə: /zz <symbol> <interval> (məs: /zz btc 15m)")
        return

    symbol = context.args[0].upper() + "/USDT"
    interval = context.args[1]

    if interval not in interval_map:
        await update.message.reply_text("Yanlış interval! Seçimlər: 1m, 5m, 15m, 30m, 1h, 4h, 1d")
        return

    try:
        ohlcv = exchange.fetch_ohlcv(symbol, interval_map[interval], limit=50)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        mpf.plot(df, type='candle', style='charles', title=f"{symbol} ({interval}) - MEXC",
                 ylabel='Qiymət (USDT)', volume=True, savefig='chart.png')

        await update.message.reply_photo(photo=open("chart.png", "rb"))

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {str(e)}")

# /price əmri – hazırki qiyməti göstər
async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("İstifadə: /price <symbol> (məs: /price btc)")
        return

    symbol = context.args[0].upper() + "/USDT"
    try:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker["last"]
        await update.message.reply_text(f"{symbol} üçün hazırki qiymət: {price} USDT")
    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {str(e)}")

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("zz", zz_handler))
    app.add_handler(CommandHandler("price", price_handler))

    print("Bot başladı...")
    app.run_polling()
