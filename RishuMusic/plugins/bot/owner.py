from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from RishuMusic import app
from config import BOT_USERNAME
from RishuMusic.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """
**
┌┬─────────────────⦿
│├─────────────────╮
│├ ᴛɢ ɴᴀᴍᴇ - 𝗭𝗲‌𝗳𝗿𝗼‌𝗻 ‌🔥
│├ ʀᴇᴀʟ ɴᴀᴍᴇ - 𝗭𝗲‌𝗳𝗿𝗼‌𝗻 ‌🔥
│├─────────────────╯
├┼─────────────────⦿
├┤~ @ABOUT_crush_hu_tera
├┤~ @crush_hu_tera
├┤~ @crush_hu_tera
├┼─────────────────⦿
│├─────────────────╮
│├OWNER│ @crush_hu_tera
│├─────────────────╯
└┴─────────────────⦿
**
"""




@app.on_message(filters.command("owner"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("𝗭𝗲‌𝗳𝗿𝗼‌𝗻 ‌🔥", url=f"https://t.me/crush_hu_tera")
        ],
        [
          InlineKeyboardButton("ＨＥＬＰ", url="https://t.me/crush_hu_tera"),
          InlineKeyboardButton("ＲＥＰＯ", url="https://t.me/crush_hu_tera"),
          ],
               [
                InlineKeyboardButton(" ＮＥＴＷＯＲＫ", url=f"https://t.me/crush_hu_tera"),
],
[
InlineKeyboardButton("ＯＦＦＩＣＩＡＬ ＢＯＴ", url=f"https://t.me/RJ_92_MUSIC_BOT"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://files.catbox.moe/qu0hhu.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
