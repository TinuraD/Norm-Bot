# Ported From William Butcher Bot
# Ported by Tinura Dinith for Norm

from pyrogram import filters
from pyrogram.types import Message

from normbot import pbot

__MODULE__ = "WebSS 📱"
__HELP__ = f"""
• /webss [link] - වෙබ්පිටුවක screenshot එකක් ගැනීම සදහා.
• මෙහිදී ඔබ link එක ලබා දීමෙදී http:// හෝ https:// නිවැරදිව ලබා දිය යුතුය.
 උදා:- `/webss https://www.google.com/`
"""


@pbot.on_message(filters.command("webss"))
async def take_ss(_, message: Message):
    try:
        if len(message.command) != 2:
            return await message.reply_text("Screenshot එකක් ලබා ගැනීමට link එකක් ලබා දෙන්න.")
        url = message.text.split(None, 1)[1]
        m = await message.reply_text("Screenshot එක ගනිමින්")
        await m.edit("උඩුගත කරමින්")
        try:
            await message.reply_photo(
                photo=f"https://webshot.amanoteam.com/print?q={url}",
                quote=False,
            )
        except TypeError:
            return await m.edit("එවැනි වෙබ්පිටුවක් නොමැත.")
        await m.delete()
    except Exception as e:
        await message.reply_text(str(e))
