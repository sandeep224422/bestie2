from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from RishuMusic import app
from config import BOT_USERNAME
from RishuMusic.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """
**⌾ ᴡᴇʟᴄᴏᴍᴇ ғᴏʀ 𝗭𝗲‌𝗳𝗿𝗼‌𝗻 ‌🔥 ʀᴇᴘᴏ
 
● ɪғ ʏᴏᴜ ᴡᴀɴᴛ ʙᴇsᴛɪᴇ ꭙ ᴍᴜsɪᴄ ♡゙゙

● ʙᴏᴛ ʀᴇᴘᴏ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʀᴇᴘᴏ ● **
"""




@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("✙ ᴀᴅᴅ ᴍᴇ ✙", url=f"https://t.me/{BESTIE_X_MUSIC_BOT}?startgroup=true")
        ],
        [
          InlineKeyboardButton("• ʜᴇʟᴘ •", url="https://t.me/crush_hu_tera"),
          InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="https://t.me/crush_hu_tera"),
          ],
               [
                InlineKeyboardButton("• ɴᴇᴛᴡᴏʀᴋ •", url=f"https://t.me/crush_hu_tera"),
],
[
InlineKeyboardButton("• ʀᴇᴘᴏ •", url=f"https://github.com"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://files.catbox.moe/qu0hhu.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
