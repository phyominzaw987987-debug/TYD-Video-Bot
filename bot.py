
import os
import asyncio
import tempfile
import logging
from pathlib import Path

import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ ❤️\n\nVideo Link ပို့ပေးပါ။ Download လုပ်ပေးပါမယ်။"
    )

def download_video(url, folder):
    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(Path(folder) / "video.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 49 * 1024 * 1024,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    files = list(Path(folder).glob("video.*"))
    if not files:
        raise Exception("Video file not found")

    return str(files[0])

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith(("https://", "http://")):
        await update.message.reply_text("မှန်ကန်တဲ့ Video Link ပို့ပေးပါ။")
        return

    msg = await update.message.reply_text("⏳ Video Download လုပ်နေပါတယ်...")

    try:
        with tempfile.TemporaryDirectory() as folder:
            file_path = await asyncio.to_thread(
                download_video, url, folder
            )

            if os.path.getsize(file_path) > 49 * 1024 * 1024:
                raise Exception("Video ဖိုင်ကြီးလွန်းနေပါတယ်။")

            with open(file_path, "rb") as video:
                await update.message.reply_video(
                    video=video,
                    caption="✅ Download အောင်မြင်ပါပြီ ❤️"
                )

        await msg.delete()

    except Exception as e:
        logging.exception("Download failed")
        await msg.edit_text(
            "❌ Video Download မအောင်မြင်ပါ။\n"
            "အခြား Link တစ်ခုနဲ့ စမ်းကြည့်ပါ။"
        )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable မရှိပါ")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
