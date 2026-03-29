from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = "8734767776:AAEV8vn5P8xpGqe_YOte2ztvDySu5F-ylaE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo bray 😄 Ayunda sudah hidup")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "kompos" in text:
        response = "Kompos itu pupuk organik 🌱"
    else:
        response = "Ayunda dengerin bray 😄"

    await update.message.reply_text(response)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("Bot siap 🚀")
app.run_polling()
