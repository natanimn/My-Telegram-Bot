import os
import asyncio
import pymongo
from telebot.async_telebot import AsyncTeleBot, types, util
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.asyncio_filters import IsReplyFilter, ChatFilter
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TOKEN = os.getenv("TOKEN")
bot = AsyncTeleBot(TOKEN)


class DataBase:
    def __init__(self):
        self.db = pymongo.MongoClient(os.getenv("DATABASE"))['NatipradoBot']
        self.users = self.db['users']

    async def __is_exist(self, user_id):
        col = self.users.find_one({'id': user_id})
        if col:
            return True
        else:
            return False

    async def save(self, user_id):
        if not await self.__is_exist(user_id):
            stat = 'admin' if user_id == ADMIN_ID else 'user'
            self.users.insert_one({'id': user_id, 'status': stat})

    async def banned(self, user_id):
        find = self.users.find_one({'id': user_id})
        return find is not None and find.get('status') == 'banned'

    async def ban(self, user_id):
        if user_id != ADMIN_ID:
            self.users.update_one({'id': user_id}, {'$set': {"status": "banned"}})

    async def unban(self, user_id):
        if await self.banned(user_id):
            self.users.update_one({'id': user_id}, {'$set': {"status": "user_id"}})


db = DataBase()


@bot.message_handler(commands=['start'], chat_types=['private'])
async def start_private(msg: types.Message):
    name = msg.from_user.first_name
    await db.save(msg.from_user.id)
    await bot.send_message(msg.chat.id, '👋 <b>Hello %s welcome my bot. </b>\n\n'
                                        '<i>⬇️Write me your message here</i> and I will reply as soon '
                                        'as possible.' % util.escape(name), "HTML")


@bot.message_handler(commands=['ban'], chat_id=[ADMIN_ID], is_reply=True)
async def ban_user(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    if user_id != ADMIN_ID:
        await db.ban(user_id)
        await bot.reply_to(message, "✅ <b>ይህ ተጠቃሚ ከቦቱ ታግዷል!!</b>", parse_mode="HTML")
    else:
        await bot.reply_to(message, "❌ <b>እራስህን ማገድ አትችልም።</b>", parse_mode="HTML")


@bot.message_handler(commands=['unban'], chat_id=[ADMIN_ID], is_reply=True)
async def ban_user(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    if await db.banned(user_id):
        await db.unban(user_id)
        await bot.reply_to(message, "✅ <b>ይህ ተጠቃሚ እገዳዉ ተነስቷል!!</b>", parse_mode='HTML')
    else:
        await bot.reply_to(message, "❌ <b>ይህ ተጠቅሚ ቀድሞውንም አልታገደም!!</b>", parse_mode='HTML')


@bot.message_handler(is_reply=True, chat_id=[ADMIN_ID], content_types=util.content_type_media)
async def reply(msg: types.Message):
    user_id = msg.reply_to_message.forward_from.id
    message_id = msg.reply_to_message.forward_from_message_id
    if await db.banned(user_id):
        return await bot.reply_to(msg, "❌ You have been banned from using this bot")

    await bot.copy_message(user_id, ADMIN_ID, msg.message_id, reply_to_message_id=message_id)


@bot.message_handler(content_types=util.content_type_media)
async def forward(msg: types.Message):
    await bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)


@bot.message_handler(commands=['users'], chat_id=[ADMIN_ID])
async def users(message: types.Message):
    count = db.users.count_documents({})
    await bot.reply_to(message, "ባሁኑ ሰዓት፤ የህ ቦት %d ተጠቃሚዎች አሉት።" % count)


bot.add_custom_filter(IsReplyFilter())
bot.add_custom_filter(ChatFilter())

if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())
