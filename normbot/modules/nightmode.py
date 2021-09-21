import os

from normbot.utils.sql.night_mode_sql import add_nightmode, rmnightmode, get_all_chat_id, is_nightmode_indb
from telethon.tl.types import ChatBannedRights
from apscheduler.schedulers.asyncio import AsyncIOScheduler 
from telethon import functions
from normbot.events import register
from normbot import OWNER_ID
from normbot import telethn as tbot
from telethon import *
from telethon import Button, custom, events

hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatAdminRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)

from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True

async def can_change_info(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )

@register(pattern="^/(nightmode|Nightmode|NightMode) ?(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    input = event.pattern_match.group(2)
    if not event.sender_id == OWNER_ID:
        if not await is_register_admin(event.input_chat, event.sender_id):
           await event.reply("මේ command එක දෙන්න පුලුවන් ඇඩ්මින්ලට් විතරයි.")
           return
        else:
          if not can_change_info:
            await event.reply("You are missing the following rights to use this command:CanChangeinfo")
            return
    if not input:
        if is_nightmode_indb(str(event.chat_id)):
                await event.reply(
                    "දැන් ඉදන් Night Mode එක වැඩ කරන්න පටන් ගත්තා"
                )
                return
        await event.reply(
            "Night Mode එක භාවිතා කිරීම නවත්වන ලදී."
        )
        return
    if "on" in input:
        if event.is_group:
            if is_nightmode_indb(str(event.chat_id)):
                    await event.reply(
                        "Night Mode කලින් ඉදන් ඔන් කරලා තියෙන්නේ."
                    )
                    return
            add_nightmode(str(event.chat_id))
            await event.reply("NightMode එක ඔන් කරා.")
    if "off" in input:
        if event.is_group:
            if not is_nightmode_indb(str(event.chat_id)):
                    await event.reply(
                        "Night Mode කලින් ඉදන් ඕෆ් කරලා තියෙන්නේ."
                    )
                    return
        rmnightmode(str(event.chat_id))
        await event.reply("NightMode එක Disable කරා.")
    if not "off" in input and not "on" in input:
        await event.reply("On හරි Off දෙන්න")
        return


async def job_close():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await tbot.send_message(
              int(pro.chat_id), "මධ්‍යම රාත්‍රී 12:00 යි , දැනට කාටවත් message කරන්න බෑ, ආයේ උදේ 6.00 ඉදන් පුලුවන්."
            )
            await tbot(
            functions.messages.EditChatDefaultBannedRightsRequest(
                peer=int(pro.chat_id), banned_rights=hehes
            )
            )
        except Exception as e:
            logger.info(f"Unable To Close Group {chat} - {e}")

#Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()

async def job_open():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await tbot.send_message(
              int(pro.chat_id), "උදේ 6.00 , ඔන්න දැන් ආයේ මැසේජ් දාන්න පුළුවන්."
            )
            await tbot(
            functions.messages.EditChatDefaultBannedRightsRequest(
                peer=int(pro.chat_id), banned_rights=openhehe
            )
        )
        except Exception as e:
            logger.info(f"Unable To Open Group {pro.chat_id} - {e}")

# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=5, minute=58)
scheduler.start()


__help__ = """
 • /nightmode on/off
Group එකේ ඉන්න අයට මධ්‍යම රාත්‍රී 12.00 සිට පෙරවරු 6.00 තෙක් message දන්න බැරි වෙන එක තමා මේකෙන් වෙන්නේ.
"""

__mod_name__ = "Night Mode 🌃"
