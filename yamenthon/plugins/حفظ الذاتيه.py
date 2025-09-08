import os
from telethon import events
from datetime import datetime
from pytz import timezone

from yamenthon import zedub
from ..core.managers import edit_or_reply
from ..helpers.utils import _format
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "الادوات"

# الحالة الافتراضية
repself = True

# شرح الأوامر
BaqirSelf_cmd = (
    "𓆩 [ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه 🧧](t.me/YamenThon) 𓆪\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد علـى صورة ذاتيـة لحفظهـا يدويـاً**\n"
)

# أمر عرض الشرح
@zedub.zed_cmd(pattern="الذاتيه")
async def cmd(event):
    await edit_or_reply(event, BaqirSelf_cmd)

# أمر الحفظ اليدوي
@zedub.zed_cmd(pattern="ذاتيه$")
async def manual_save(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة/فيديو ذاتيـة 𓆰...**")
    reply = await event.get_reply_message()
    if not reply.media:
        return await event.edit("**✘ الرسالة لا تحتوي على ميديا ذاتية**")
    file = await reply.download_media()
    await zedub.send_file(
        "me",
        file,
        caption="**⎉╎تم حفـظ الصـورة/الفيديـو الذاتيـه .. بنجـاح ☑️𓆰**"
    )
    await event.delete()

# تفعيل الحفظ التلقائي
@zedub.zed_cmd(pattern="(تفعيل الذاتيه|تفعيل الذاتية)")
async def start_self(event):
    global repself
    if repself:
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. مفعـل مسبقـاً ☑️**")
    repself = True
    await edit_or_reply(event, "**⎉╎تم تفعيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

# تعطيل الحفظ التلقائي
@zedub.zed_cmd(pattern="(تعطيل الذاتيه|تعطيل الذاتية)")
async def stop_self(event):
    global repself
    if not repself:
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. معطـل مسبقـاً ☑️**")
    repself = False
    await edit_or_reply(event, "**⎉╎تم تعطيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

# الحدث: كشف وحفظ الوسائط ذاتية التدمير (منطق Mr3rf1)
@zedub.on(events.NewMessage(func=lambda e: e.is_private and e.media))
async def auto_save(event):
    global repself
    if not repself:
        return

    # نتأكد أنها ميديا ذاتية التدمير (TTL)
    if hasattr(event.message.media, "ttl_seconds") and event.message.media.ttl_seconds:
        try:
            sender = await event.get_sender()
            caption = (
                f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه 🧧](t.me/YamenThon)\n\n"
                f"**⌔╎تم حفـظ الوسائـط الذاتيـة تلقائيـاً ☑️**\n"
                f"**⌔╎المـرسـل** {_format.mentionuser(sender.first_name , sender.id)}\n"
                f"**⌔╎التاريـخ** {datetime.now(timezone('Asia/Riyadh')).strftime('%Y/%m/%d %H:%M:%S')}"
            )
            file = await event.download_media()
            await zedub.send_file("me", file, caption=caption, parse_mode="md")
        except Exception as e:
            await zedub.send_message("me", f"⚠️ خطأ في حفظ الذاتيه: {str(e)}")


@zedub.zed_cmd(pattern="إعلان (\d*) ([\s\S]*)")
async def selfdestruct(destroy):
    rep = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = rep[1]
    ttl = int(rep[0])
    baqir = ttl * 60 #تعييـن الوقـت بالدقائـق بدلاً من الثـوانـي
    text = message + f"\n\n**- هذا الاعلان سيتم حذفه تلقـائيـاً بعـد {baqir} دقائـق ⏳**"
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, text)
    await sleep(baqir)
    await smsg.delete()


@zedub.on(events.NewMessage(incoming=True))
async def gpost(event):
    if event.is_private:
        return
    chat_id = str(event.chat_id).replace("-100", "")
    channels_set  = get_all_post(chat_id)
    if channels_set == []:
        return
    for chat in channels_set:
        if event.media:
            await event.client.send_file(int(chat), event.media, caption=event.text)
        elif not event.media:
            await zedub.send_message(int(chat), event.message)
