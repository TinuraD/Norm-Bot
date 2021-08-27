# Author: Fayas (https://github.com/FayasNoushad) (@FayasNoushad)

from ef_norm import dispatcher

import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters
from pyrogram.types import *

API = "https://api.abirhasan.wtf/google?query="

START_TEXT = """Hello {}
I am a google search bot.
> `I can search from google. Use me in inline.`
Made by @FayasNoushad"""

JOIN_BUTTON = [
    InlineKeyboardButton(
        text='⚙ Join Updates Channel ⚙',
        url='https://telegram.me/FayasNoushad'
    )
]


@pbot.on_message(filters.private & filters.command(["google"]))
async def start(bot, update):
    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        reply_markup=InlineKeyboardMarkup([JOIN_BUTTON]),
        disable_web_page_preview=True,
        quote=True
    )


@pbot.on_inline_query()
async def inline(bot, update):
    results = google(update.query)
    answers = []
    for result in results:
        answers.append(
            InlineQueryResultArticle(
                title=result["title"],
                description=result["description"],
                input_message_content=InputTextMessageContent(
                    message_text=result["text"],
                    disable_web_page_preview=True
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(text="Link", url=result["link"])],
                        JOIN_BUTTON
                    ]
                )
            )
        )
    await update.answer(answers)


def google(query):
    r = requests.get(API + requote_uri(query))
    informations = r.json()["results"]
    results = []
    for info in informations:
        text = f"**Title:** `{info['title']}`"
        text += f"\n**Description:** `{info['description']}`"
        text += f"\n\nMade by @FayasNoushad"
        results.append(
            {
                "title": info['title'],
                "description": info['description'],
                "text": text,
                "link": info['link']
            }
        )
    return results


__help__ = """
*Google:*
✪ Daisy can mute members who are not subscribed your channel until they subscribe
✪ When enabled I will mute unsubscribed members and show them a unmute button. When they pressed the button I will unmute them
*Setup*
1) First of all add me in the group as admin with ban users permission and in the channel as admin.
Note: Only creator of the group can setup me and i will not allow force subscribe again if not done so.
 
*Commmands*
✪ /ForceSubscribe - To get the current settings.
✪ /ForceSubscribe no/off/disable - To turn of ForceSubscribe.
✪ /ForceSubscribe {channel username} - To turn on and setup the channel.
✪ /ForceSubscribe clear - To unmute all members who muted by me.
Note: /FSub is an alias of /ForceSubscribe
 
"""
__mod_name__ = "Google"
