from telethon.tl.types import InputMediaDice

from normbot.events import register


@register(pattern="^/dice(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    r = await event.reply(file=InputMediaDice(""))
    input_int = int(input_str)
    if input_int > 6:
        await event.reply("1-6 තෙක් අංක විතරක් පාවිච්චි කරන්න.")
    
    else:
        try:
            required_number = input_int
            while r.media.value != required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice(""))
        except BaseException:
            pass


@register(pattern="^/dart(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    r = await event.reply(file=InputMediaDice("🎯"))
    input_int = int(input_str)
    if input_int > 6:
        await event.reply("1-6 තෙක් අංක විතරක් පාවිච්චි කරන්න.")
    
    else:
        try:
            required_number = input_int
            while r.media.value != required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice("🎯"))
        except BaseException:
            pass


@register(pattern="^/ball(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    r = await event.reply(file=InputMediaDice("🏀"))
    input_int = int(input_str)
    if input_int > 5:
        await event.reply("1-6 තෙක් අංක විතරක් පාවිච්චි කරන්න.")
    
    else:
        try:
            required_number = input_int
            while r.media.value != required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice("🏀"))
        except BaseException:
            pass

@register(pattern="^/goll(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    r = await event.reply(file=InputMediaDice("🎳"))
    input_int = int(input_str)
    if input_int > 5:
        await event.reply("1-6 තෙක් අංක විතරක් පාවිච්චි කරන්න.")
    
    else:
        try:
            required_number = input_int
            while r.media.value != required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice("🎳"))
        except BaseException:
            pass   
        
@register(pattern="^/football(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    r = await event.reply(file=InputMediaDice("⚽️"))
    input_int = int(input_str)
    if input_int > 5:
        await event.reply("1-6 තෙක් අංක විතරක් පාවිච්චි කරන්න.")
    
    else:
        try:
            required_number = input_int
            while r.media.value != required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice("⚽️"))
        except BaseException:
            pass         
        
__help__ = """
 *Telegram වල වලින් කරන වැඩක්. කරලම බලන්න.*
  • /dice හෝ /dice < 1-6 තෙක් ඕනෑම අගයක් >
  • /ball හෝ /ball < 1-6 තෙක් ඕනෑම අගයක් >
  • /dart හෝ /dart < 1-6 තෙක් ඕනෑම අගයක් >
  • /goll
  • /football
 මෙතනදි අගයන් දාන විට වෙනත් අගයන් දැමීමෙන් ගැටළු ඇති වෙන්න පුළුවන්.
"""

__mod_name__ = "Games 🎲"
