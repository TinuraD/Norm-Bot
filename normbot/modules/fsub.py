import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from normbot import DRAGONS as SUDO_USERS
from normbot import pbot
from normbot.utils.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f" අපේ @{channel} එකට ඔයා Join වෙලා නැති නිසා ඔයාට message දාන්න බෑ ❗ ඒ නිසා පහලින් join වෙලා 'Unmute කරන්න' කියන එක ඔබන්න.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="Admin ලා විසින් හේතු කිහිපයක් නිසා ඔයාව mute කරලා.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f" **{cb.from_user.mention} හදනවා එයාව ම mute කර ගන්න. ඒත් මම admin කෙනෙක් නෙමේ, ඒ නිසා මට ඒක කරන්න බෑ. 😢 ",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text=" ඔයා mute වෙලා නෑ 😂 මේක ඔබන්න එපා.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "අයියෝ {} 🙏 \n ඔයා අපේ එකට වෙලා නෑ. 😭 \n ඒ නිසා [අපේ Channel](https://t.me/{}) එකට join වෙලා 'මාව Unmute කරන්න' කියන එක ඔබන්න. \n \n ".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "අපේ Channel එකට join වෙන්න.",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "මාව Unmute කරන්න", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "මම admin කෙනෙක් නෙමේ, ඒ නිසා මට මේක කරන්න බෑ, මාව admin කෙනෙක් කරලා නැවත උත්සාහ කරන්න."
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f" @{channel} වල මම admin කෙනෙක් නෙමේ\nමාව admin කෙනෙක් කරලා නැවත උත්සාහ කරන්න",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("Fsub off කරා.")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "මම mute කරපු ඔක්කොම unmute කරා."
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("මම mute කරපු ඔක්කොම unmute කරා. ✅")
                except ChatAdminRequired:
                    sent_message.edit(
                        "මම admin කෙනෙක් නෙමේ, ඒ නිසා මට මේක කරන්න බෑ, මාව Users Band කරන Permisson එකත් එක්ක admin කෙනෙක් කරලා නැවත උත්සාහ කරන්න."
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"Fsub on කරා. හැමෝම අපේ [channel](https://t.me/{input_str}) එකට join වෙන්න. ✅",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"[channel](https://t.me/{input_str}) වල මම admin කෙනෙක් නෙමේ\nමාව admin කෙනෙක් කරලා නැවත උත්සාහ කරන්න",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"Channel එකේ Username එක වැරදියි ❌")
                except Exception as err:
                    message.reply_text(f"ගැටලුවක් 😭 ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Fsub කරා..**\n__ මේ [Channel](https://t.me/{sql.fs_settings(chat_id).channel})එකට__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("Fsub off කරා.")
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )


__help__ = """

*විධාන*
• /FSub - දැට ඇති තත්වය දැන ගන්න.
• /FSub no/off/disable - Fsub on,off කිරීම සදහා.
• /FSub {channel username} - හදා ගන්න විදිහ
• /FSub clear - mute කරපු හැමෝම unmute කරන්න. 
"""
__mod_name__ = " Fsub 📢 "
