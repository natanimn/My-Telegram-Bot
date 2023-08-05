import os

from pyrogram import Client, filters, types

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Client("natipradobot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)


def is_reply(message: types.Message):
    return message.reply_to_message is not None


@bot.on_message(filters.private & filters.command('start'))
async def start(client, message: types.Message):
    user = message.from_user
    await message.reply_text("""<b>👋 Hello %s welcome my bot.</b>

⬇️Write me your message here and I will reply as soon as possible.
""" % user.first_name)


@bot.on_message(filters.private & filters.create(lambda c, f, m: is_reply(m) and m.from_user.id == ADMIN_ID))
async def reply(client, message: types.Message):
    reply_message = message.reply_to_message
    await message.copy(reply_message.from_user.id)


@bot.on_message(filters.private)
async def forward(client, message: types.Message):
    await message.forward(ADMIN_ID)


if __name__ == '__main__':
    bot.run()
