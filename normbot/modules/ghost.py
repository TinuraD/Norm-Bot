from asyncio import sleep

from telethon import events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChatBannedRights

from normbot import DEMONS, DEV_USERS, DRAGONS, OWNER_ID, telethn

# =================== CONSTANT ===================

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)


UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

OFFICERS = [OWNER_ID] + DEV_USERS + DRAGONS + DEMONS

# Check if user has admin rights
async def is_administrator(user_id: int, message):
    admin = False
    async for user in telethn.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in OFFICERS:
            admin = True
            break
    return admin


@telethn.on(events.NewMessage(pattern=f"^[!/]ghost ?(.*)"))
async def ghost(event):
    """ For .ghost command, list all the ghost in a chat. """

    con = event.pattern_match.group(1).lower()
    del_u = 0
    del_status = "ඩිලීට් කරන ලද අකවුන්ට් නොමැත."

    if con != "clean":
        find_ghost = await event.respond("ඩිලීට් කරල ලද අකවුන්ට් සොයමින්")
        async for user in event.client.iter_participants(event.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f" **{del_u}** මකා දමන අකවුන්ට් එකක් හමුවුණා.\
            \nඔවුන් ඉවත් කිරීමට /ghost clean විධානය භාවිතා කරන්න."
        await find_ghost.edit(del_status)
        return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not await is_administrator(user_id=event.from_id, message=event):
        await event.respond("ඔයා ඇඩ්මින් කෙනෙක් නෙමේ.")
        return

    if not admin and not creator:
        await event.respond("මම ඇඩ්මින් කෙනෙක් නෙමේ.")
        return

    cleaning_ghost = await event.respond("ඩිලීට් කරන ලද අකවුන්ට් මකමින්....")
    del_u = 0
    del_a = 0

    async for user in event.client.iter_participants(event.chat_id):
        if user.deleted:
            try:
                await event.client(
                    EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                await cleaning_ghost.edit("මට මේ group එකේ අයව බෑන් කරන්න අවසට නෑ.")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"ඩිලීට් කරන ලද අකවුන්ට් `{del_u}` ක් මකා දමන ලදී."

    if del_a > 0:
        del_status = f"ඩිලීට් කරන ලද අකවුන්ට් `{del_u}` ක් මකා දමන ලදී. \
        \n`{del_a}` ඇඩ්මින් ලෙස තිබෙන ඩිලීට් කරපු අකවුන්ට් ඉවත් කරේ නෑ."

    await cleaning_ghost.edit(del_status)
