import asyncio
import glob
import os

from . import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _zedutils
from . import BOTLOG, BOTLOG_CHATID, mention

plugin_category = "الادوات"

# قاموس التحويل من الاسماء المبسطة إلى الوقتات الفعلية
var_yamenthon = {
    "البوت": "TG_BOT_TOKEN",
}

config = "./config.py"
var_checker = [
    "APP_ID",
    "PM_LOGGER_GROUP_ID",
    "PRIVATE_CHANNEL_BOT_API_ID",
    "PRIVATE_GROUP_BOT_API_ID",
]
exts = ["jpg", "png", "webp", "webm", "m4a", "mp4", "mp3", "tgs"]


# قاموس الأوقات بالعربي
tz_map = {
    "اليمن": "Asia/Aden",
    "العراق": "Asia/Baghdad",
    "السعودية": "Asia/Riyadh",
    "مصر": "Africa/Cairo",
    "الجزائر": "Africa/Algiers",
    "تونس": "Africa/Tunis",
    "المغرب": "Africa/Casablanca",
    "تركيا": "Europe/Istanbul",
}


@zedub.zed_cmd(
    pattern="ضع وقت(?: |$)([\\s\\S]*)",
    command=("وقت", plugin_category),
    info={
        "header": "لتغيير المنطقة الزمنية من داخل تيليجرام.",
        "usage": [
            "{tr}ضع وقت اليمن",
            "{tr}ضع وقت العراق",
        ],
    },
)
async def variable(event):
    if not os.path.exists(config):
        return await edit_delete(
            event,
            "**- عـذراً .. لايـوجـد هنـالك ملـف كـونفـج 📁🖇**\n\n"
            "**- هـذه الاوامـر خـاصـة فقـط بالمنصبيـن ع السيـرفـر 📟💡**"
        )

    user_input = event.pattern_match.group(1).strip()
    if not user_input:
        return await edit_or_reply(event, "**⌔∮** `.ضع وقت <اسم الدولة>`")

    cat = await edit_or_reply(event, "**⌔∮ جـارِ إعـداد المنطقـة الزمنية ...**")

    # إذا المستخدم كتب دولة بالعربي
    if user_input in tz_map:
        value = f'"{tz_map[user_input]}"'
    else:
        # إذا كتب منطقة زمنية جاهزة
        value = f'"{user_input}"'

    variable = "TZ"

    with open(config, "r") as f:
        configs = f.readlines()

    string = ""
    match = False
    for i in configs:
        if i.strip().startswith(f"{variable} "):
            string += f'{variable} = {value}\n'
            match = True
        else:
            string += i

    if not match:
        string += f'{variable} = {value}\n'

    with open(config, "w") as f1:
        f1.write(string)

    await cat.edit(
        f"**- تم تغيـير المنطقة الزمنية إلى :** `{value}` ✅\n\n"
        "**- يتم الان اعـادة تشغيـل بـوت يمن ثون ...**\n**يستغـرق الامر 5-8 دقيقـه ▬▭ ...**"
    )

    await event.client.reload(cat)
