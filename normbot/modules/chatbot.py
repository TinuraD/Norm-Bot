import requests, functools
from normbot import pbot
from pyrogram import filters
from normbot.utils.sql.chatbot import is_chatbot_indb, addchatbot, rmchatbot
from googletrans import Translator

tr = Translator()
BOT_ID = "1976629825"

def is_admin(func):
    @functools.wraps(func)
    async def oops(client,message):
        is_admin = False
        try:
            user = await message.chat.get_member(message.from_user.id)
            admin_strings = ("creator", "administrator")
            if user.status not in admin_strings:
                is_admin = False
            else:
                is_admin = True

        except ValueError:
            is_admin = True
        if is_admin:
            await func(client,message)
        else:
            await message.reply("Only Admins can execute this command!")
    return oops

@pbot.on_message(filters.command("chatbot"))
@is_admin
async def chatbot_toggle(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Use /chatbot with on or off")
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "on":
        addchatbot(str(chat_id))
        await message.reply_text("Chat bot enabled.")
    elif status == "off":
        rmchatbot(str(chat_id))
        await message.reply_text("Chat bot disabled.")
    else:
        await message.reply_text("Use /chatbot with on or off")

@pbot.on_message(
    filters.text 
    & filters.reply 
    & ~filters.private 
    & ~filters.edited 
    & ~filters.bot 
    & ~filters.channel 
    & ~filters.forwarded,
    group=4)
async def chatbot(_, message):
    chat_id = message.chat.id
    if not (is_chatbot_indb(str(message.chat_id))):
        return
    if not message.reply_to_message.from_user.id in BOT_ID:
        return
    if message.text[0] == "/":
        return
    await pbot.send_chat_action(message.chat.id, "typing")
    lang = tr.translate(message.text).src
    trtoen = (message.text if lang=="en" else tr.translate(message.text, dest="en").text).replace(" ", "%20")
    text = trtoen.replace(" ", "%20") if len(message.text) < 2 else trtoen
    affiliateplus = requests.get(f"https://api.affiliateplus.xyz/api/chatbot?message={text}&botname=Bolt%20Backer&ownername=Tinura%20Dinith&user=1")
    textmsg = (affiliateplus.json()["message"])
    msg = tr.translate(textmsg, src='en', dest=lang)
    await message.reply_text(msg.text)

__name__ = "Chat Bot 🤖"
__help__ = """
• /chatbot `[on/off]` - To turn on and off chatbot
Chat bot support many languages like English, Sinhala, Tamil etc. When you replying to any message send by Bolt chat bot will work.
"""
