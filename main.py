import ccxt
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
import os

# Dəstəklənən intervallar
interval_map = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d"
}

# MEXC birjası
exchange = ccxt.mexc()

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
        timestamps = [datetime.datetime.fromtimestamp(c[0] / 1000) for c in ohlcv]
        closes = [c[4] for c in ohlcv]

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, closes, marker='o')
        plt.title(f"{symbol} ({interval}) - MEXC")
        plt.xlabel("Vaxt")
        plt.ylabel("Qiymət (USDT)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()

        await update.message.reply_photo(photo=open("chart.png", "rb"))

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {str(e)}")

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("zz", zz_handler))
    print("Bot başladı...")
    app.run_polling()
