import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from normbot import DRAGONS, dispatcher
from normbot.modules.disable import DisableAbleCommandHandler
from normbot.functions.alternate import send_message
from normbot.functions.chat_status import (
    ADMIN_CACHE,
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
)
from normbot.functions.extraction import extract_user, extract_user_and_text
from normbot.modules.log_channel import loggable


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and not user.id in DRAGONS
    ):
        message.reply_text("එය කිරීමට ඔබට අවශ්ය අයිතිවාසිකම් නොමැත!")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "ඔබ පරිශීලකයෙකු හෝ නිශ්චිතව දක්වා ඇති හැඳුනුම්පතක් ගැන සඳහන් කර ඇති බවක් නොපෙනේ.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "administrator" or user_member.status == "creator":
        message.reply_text("දැනටමත් adminයෙකු වන කෙනෙකු promote කිරීමට මා අදහස් කරන්නේ කෙසේද??")
        return

    if user_id == bot.id:
        message.reply_text("මට මාවම promote කරන්න බැහැ!මා වෙනුවෙන් එය කිරීමට admin එකක් ලබා ගන්න.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("කණ්ඩායමේ නොමැති කෙනෙකු මට promote කළ නොහැක.")
        else:
            message.reply_text("promote කිරීමේදී දෝෂයක් ඇතිවිය.")
        return

    bot.sendMessage(
        chat.id,
        f"Sucessfully promoted <b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "ඔබ පරිශීලකයෙකු හෝ නිශ්චිතව දක්වා ඇති හැඳුනුම්පතක් ගැන සඳහන් කර ඇති බවක් නොපෙනේ.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text("මෙම පුද්ගලයා චැට් නිර්මාණය කළේ, මම ඒවා කපන්නේ කෙසේද?")
        return

    if not user_member.status == "administrator":
        message.reply_text("මම promote නොකළ අය ඉවත් කළ නොහැක!")
        return

    if user_id == bot.id:
        message.reply_text("මට මාවම හිතාගන්නවත් බැහැ!මා වෙනුවෙන් එය කිරීමට adminයෙක් ලබා ගන්න.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )

        bot.sendMessage(
            chat.id,
            f"Sucessfully demoted <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "මට කිරීමට නොහැකි විය.මම admin නොවිය හැකිය, නැතහොත් admin තත්ත්වය තවත් අයෙකු විසින් පත් කරන ලදී"
            " පරිශීලකයා, එබැවින් මට ඔවුන් මත ක්රියා කළ නොහැක!"
        )
        return


@run_async
@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("Admins cache refreshed!")


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "ඔබ පරිශීලකයෙකු හෝ නිශ්චිතව දක්වා ඇති හැඳුනුම්පතක් ගැන සඳහන් කර ඇති බවක් නොපෙනේ."
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "මෙම පුද්ගලයා චැට් නිර්මාණය කළේ, මම ඔහු වෙනුවෙන් අභිරුචි මාතෘකාව සැකසිය හැක්කේ කෙසේද??"
        )
        return

    if not user_member.status == "administrator":
        message.reply_text(
            "admin නොවන අය සඳහා මාතෘකාව සැකසිය නොහැක!\nඅභිරුචි මාතෘකාව සැකසීමට පළමුව ඒවා promote කරන්න!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I මගේම මාතෘකාව මා විසින්ම සැකසිය නොහැක!මා වෙනුවෙන් එය කිරීමට මා admin බවට පත් කළ තැනැත්තා ලබා ගන්න."
        )
        return

    if not title:
        message.reply_text("හිස් මාතෘකාව සැකසීම කිසිවක් නොකරයි!")
        return

    if len(title) > 16:
        message.reply_text(
            "මාතෘකාව දිග අක්ෂර 16 කට වඩා දිගු වේ.\nඑය අක්ෂර 16 ක් කරන්න."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text("මා promote නොකළ adminයින් සඳහා මට අභිරුචි මාතෘකාව සැකසිය නොහැක!")
        return

    bot.sendMessage(
        chat.id,
        f"Sucessfully set title for <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() == "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#PINNED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNPINNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@run_async
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "මට ආරාධනා සබැඳිය සඳහා ප්රවේශය නොමැති අතර, මගේ අවසරයන් වෙනස් කිරීමට උත්සාහ කරන්න!"
            )
    else:
        update.effective_message.reply_text(
            "මට ඔබට ලබා දිය හැක්කේ සුපිරි group සහ නාලිකා සඳහා වන සබැඳි, සමාවන්න!"
        )


@run_async
@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "මෙම විධානය ක්රියාත්මක වන්නේ group වල පමණි.")
        return

    update.effective_chat
    chat_id = update.effective_chat.id
    update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            "කණ්ඩායම් adminයින් ලබා ගැනීම...", parse_mode=ParseMode.HTML
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "කණ්ඩායම් adminයින් ලබා ගැනීම...", quote=False, parse_mode=ParseMode.HTML
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "Admins in <b>{}</b>:".format(html.escape(update.effective_chat.title))

    bot_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ මකා දැමූ ගිණුම"
        else:
            name = "{}".format(
                mention_html(
                    user.id, html.escape(user.first_name + " " + (user.last_name or ""))
                )
            )

        if user.is_bot:
            bot_admin_list.append(name)
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 👑 Creator:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🔱 Admins:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id, html.escape(user.first_name + " " + (user.last_name or ""))
                )
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0], html.escape(admin_group)
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group in custom_admin_list:
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in custom_admin_list[admin_group]:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    text += "\n🤖 Bots:"
    for each_bot in bot_admin_list:
        text += "\n<code> • </code>{}".format(each_bot)

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
 • /admins - list of admins in the chat

*Adminලට විතරයි:*
 • /pin - නිකන්ම reply කරපු message එක  pin කරන්න .`'loud'` හෝ `'notify'` දැම්මොත් අගට pin කරා කියලා notfication එකක් group එකේ දානවා.
 • /unpin - unpins කරන්න message.
 • /invitelink - Invite link එක ගන්න.
 • /promote - Reply කරන කෙනාව admin කරන්න.
 • /demote - Reply කරන කෙනාගේ admin අයින් කරන්න.
 • /title <title here> - Bot ගෙන් promote කරපු කෙනාගෙ admin title එකක් දෙන්න/වෙනස් කරන්න.
 • /admincache - Admins list එක refresh කරන්න.
 • /zombies - scan and clean zombies
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=Filters.group
)

dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admin 🎖"
__command_list__ = [
    "adminlist",
    "admins",
    "invitelink",
    "promote",
    "demote",
    "admincache",
]
__handlers__ = [
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
