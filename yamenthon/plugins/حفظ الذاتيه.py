# سورس يمنثون - حفظ الرسائل الذاتية
import os
from telethon import events
from .. import zedub
from ..core.managers import edit_or_reply

plugin_category = "الادوات"
download_path = "downloads/"

if not os.path.exists(download_path):
    os.makedirs(download_path)

@zedub.on(events.NewMessage(pattern="ذاتيه$"))
async def save_self_destruct_media(event):
    "⎉ لحفظ الوسائط الذاتية الاختفاء"
    reply = await event.get_reply_message()
    if not reply:
        return await edit_or_reply(event, "⎉╎قم بالرد على الوسائط الذاتية لحفظها ❌")

    if not reply.media:
        return await edit_or_reply(event, "⎉╎الرسالة لا تحتوي على وسائط ❌")

    status = await edit_or_reply(event, "⎉╎جاري حفظ الوسائط الذاتية ...")

    try:
        # تنزيل الوسائط أولاً
        file_path = await event.client.download_media(reply, file=download_path)

        if not file_path:
            return await status.edit("⎉╎لم أستطع حفظ الوسائط (قد تكون محمية أو غير مدعومة) ❌")

        # رفعها للرسائل المحفوظة (Saved Messages)
        await zedub.send_file(
            "me",
            file_path,
            caption=f"**⎉╎تم حفـظ الوسائط الذاتية .. بنجـاح ☑️𓆰**",
            force_document=True  # مهم: حتى لا يتلف الملف أو يضغط
        )

        await status.edit("⎉╎تم حفـظ الوسائط وإرسالها للمحفوظات ☑️")

    except Exception as e:
        await status.edit(f"⎉╎حدث خطأ أثناء الحفظ:\n`{str(e)}`")
