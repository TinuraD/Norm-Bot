from pyrogram import filters
from pyrogram.types import Message

from normbot import pbot
from pyrogram.errors import RPCError

import functools

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

def get_text(message: Message) -> [None, str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@pbot.on_message(
    filters.command("send") & ~filters.edited & ~filters.bot)
@is_admin
async def send(client, message):
    if message.reply_to_message:
            reply = message.reply_to_message
            try:
                await reply.copy(message.chat.id)
            except RPCError as i:
                await message.reply(i)
                return

    else:
        args = get_text(message)
        await client.send_message(message.chat.id, text=args)

@pbot.on_message(
    filters.command("edit") & ~filters.edited & ~filters.bot)
@is_admin
async def loltime(client, message):
    lol = await message.reply("Processing please wait")
    cap = get_text(message)
    if not message.reply_to_message:
        await lol.edit("reply to any message to edit caption")
    reply = message.reply_to_message
    try:
        await reply.copy(message.chat.id,caption= cap)
        await lol.delete()
    except RPCError as i:
        await lol.edit(i)
        return
