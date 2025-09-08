import os
import shutil
from asyncio import sleep
from telethon import events

from . import zedub
from ..core.logger import logging
from ..helpers.utils import _format
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.echo_sql import (
    addecho,
    get_all_echos,
    get_echos,
    is_echo,
    remove_all_echos,
    remove_echo,
    remove_echos,
)
from ..sql_helper.autopost_sql import get_all_post
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)
zedself = True

POSC = gvarstatus("Z_POSC") or "(مم|ذاتية|ذاتيه|جلب الوقتيه)"

ZelzalSelf_cmd = (
    "𓆩 [ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - حفـظ الذاتيـه 🧧](t.me/YamenThon) 𓆪\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**سوف يقوم حسابك بحفظ الذاتيه تلقائياً في حافظة حسابك عندما يرسل لك اي شخص ميديـا ذاتيـه**\n\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد ؏ــلى صـوره ذاتيـه لحفظهـا في حال كان امر الحفظ التلقائي معطـل**\n\n\n"
    "**⪼** `.اعلان`\n"
    "**الامـر + الوقت بالدقائق + الرسـاله**\n"
    "**امـر مفيـد لجماعـة التمويـل لـ عمـل إعـلان مـؤقت بالقنـوات**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙔𝘼𝙈](t.me/YamenThon) 𓆪"
)

@zedub.zed_cmd(pattern="الذاتيه")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalSelf_cmd)

# حفظ ذاتي يدوي
@zedub.zed_cmd(pattern=f"{POSC}(?: |$)(.*)")
async def oho(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر 𓆰...**")
    reply = await event.get_reply_message()
    file = await reply.download_media()
    if not file:
        return await event.edit("**⎉╎لم أستطع حفظ الوسائط (قد تكون محمية أو غير مدعومة) ❌**")
    await zedub.send_file(
        "me",
        file,
        caption=f"**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️𓆰**",
    )
    await event.delete()

# تفعيل الحفظ التلقائي
@zedub.zed_cmd(pattern="(تفعيل الذاتيه|تفعيل الذاتية)")
async def start_datea(event):
    global zedself
    if zedself:
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. مفعـله مسبقـاً ☑️**")
    zedself = True
    await edit_or_reply(event, "**⎉╎تم تفعيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

# تعطيل الحفظ التلقائي
@zedub.zed_cmd(pattern="(تعطيل الذاتيه|تعطيل الذاتية)")
async def stop_datea(event):
    global zedself
    if zedself:
        zedself = False
        return await edit_or_reply(event, "**⎉╎تم تعطيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")
    await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. معطلـه مسبقـاً ☑️**")

# الحفظ التلقائي عند استقبال ميديا
@zedub.on(events.NewMessage(func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread))
async def sddm(event):
    global zedself
    if event.sender_id == zedub.uid:
        return
    if zedself:
        sender = await event.get_sender()
        file = await event.download_media()
        if not file:
            return  # تجاهل إذا فشل التحميل
        await zedub.send_file(
            "me",
            file,
            caption=f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - حفـظ الذاتيـه 🧧](t.me/YamenThon) .\n\n"
            f"⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
            f"**⌔╎مࢪحبـاً عـزيـزي المـالك 🫂\n"
            f"⌔╎ تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️** ❝\n"
            f"**⌔╎المـرسـل** {_format.mentionuser(sender.first_name , sender.id)} .",
        )

# اعلان مؤقت
@zedub.zed_cmd(pattern="اعلان (\d*) ([\s\S]*)")
async def selfdestruct(destroy):
    zed = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = zed[1]
    ttl = int(zed[0])
    seconds = ttl * 60
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, message)
    await sleep(seconds)
    await smsg.delete()

@zedub.zed_cmd(pattern="إعلان (\d*) ([\s\S]*)")
async def selfdestruct_alt(destroy):
    zed = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = zed[1]
    ttl = int(zed[0])
    seconds = ttl * 60
    text = message + f"\n\n**- هذا الاعلان سيتم حذفه تلقـائيـاً بعـد {ttl} دقائـق ⏳**"
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, text)
    await sleep(seconds)
    await smsg.delete()

# اعادة نشر تلقائية
@zedub.on(events.NewMessage(incoming=True))
async def gpost(event):
    if event.is_private:
        return
    chat_id = str(event.chat_id).replace("-100", "")
    channels_set = get_all_post(chat_id)
    if not channels_set:
        return
    for chat in channels_set:
        if event.media:
            await event.client.send_file(int(chat), event.media, caption=event.text)
        else:
            await zedub.send_message(int(chat), event.message)
