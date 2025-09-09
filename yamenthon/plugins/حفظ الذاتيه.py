import os
from telethon import events
from . import zedub
from ..core.logger import logging
from ..helpers.utils import _format
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)

# رسائل المساعدة
ZelzalSelf_cmd = (
    "𓆩 [ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - حفـظ الذاتيـه 🧧](t.me/YamenThon) 𓆪\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**سوف يقوم حسابك بحفظ الذاتيه تلقائيًا في حافظة حسابك عندما يرسل لك اي شخص ميديـا ذاتيـه**\n\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد علـى صـوره ذاتيـه لحفظهـا في حال كان امر الحفظ التلقائي معطـل**\n\n\n"
    "\n𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙔𝘼𝙈](t.me/YamenThon) 𓆪"
)

# الامر: .الذاتيه
@zedub.zed_cmd(pattern="الذاتيه")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalSelf_cmd)

# الامر: .ذاتيه (بالرد على صورة)
@zedub.zed_cmd(pattern="(مم|ذاتية|ذاتيه|جلب الوقتيه)(?: |$)(.*)")
async def manual_save(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر 𓆰...**")
    reply_msg = await event.get_reply_message()
    file_path = await reply_msg.download_media()
    if file_path:
        await zedub.send_file("me", file_path, caption="**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️𓆰**")
        os.remove(file_path)
    await event.delete()

# الامر: .تفعيل الذاتيه
@zedub.zed_cmd(pattern="(تفعيل الذاتيه|تفعيل الذاتية)")
async def enable_auto(event):
    if gvarstatus("SELF_SAVE"):
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيه التلقائي .. مفعّل مسبقًا ☑️**")
    addgvar("SELF_SAVE", "True")
    await edit_or_reply(event, "**⎉╎تم تفعيل حفظ الذاتيه التلقائي .. بنجـاح ☑️**")

# الامر: .تعطيل الذاتيه
@zedub.zed_cmd(pattern="(تعطيل الذاتيه|تعطيل الذاتية)")
async def disable_auto(event):
    if not gvarstatus("SELF_SAVE"):
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيه التلقائي .. معطّل مسبقًا ☑️**")
    delgvar("SELF_SAVE")
    await edit_or_reply(event, "**⎉╎تم تعطيل حفظ الذاتيه التلقائي .. بنجـاح ☑️**")

# مراقبة جميع الرسائل لالتقاط الميديا الذاتية
@zedub.on(events.NewMessage(func=lambda e: e.media and getattr(e.media, "ttl_seconds", None)))
async def auto_save(event):
    # التحقق إذا الخاصية مفعلة
    if not gvarstatus("SELF_SAVE"):
        return

    # تجاهل رسائلك انت
    if event.sender_id == zedub.uid:
        return

    try:
        sender = await event.get_sender()
        file_path = await event.download_media()
        if file_path:
            caption = (
                "[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - حفـظ الذاتيـه 🧧](t.me/YamenThon)\n\n"
                "⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
                f"**⌔╎مࢪحبـاً عـزيـزي المـالك 🫂**\n"
                f"**⌔╎تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️**\n"
                f"**⌔╎المـرسـل** {_format.mentionuser(sender.first_name, sender.id)}"
            )
            await zedub.send_file("me", file_path, caption=caption)
            os.remove(file_path)
    except Exception as e:
        LOGS.error(f"خطأ أثناء حفظ الذاتيه: {e}")
