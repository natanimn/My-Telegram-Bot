import os
from telebot import TeleBot, types, util, apihelper
from telebot.custom_filters import IsReplyFilter, ChatFilter
from flask import Flask, request

ADMIN_ID = os.getenv("ADMIN_ID")
apihelper.ENABLE_MIDDLEWARE = True
TOKEN = os.getenv("TOEKN")
bot = TeleBot(TOKEN, parse_mode="markdown")
app = Flask(__name__)
WEBHOOK = os.getenv("WEBHOOK")


@bot.message_handler(commands=['start'], chat_types=['private'])
def start_private(msg: types.Message):
    bot.send_message(msg.chat.id, '**Hy there**\n__I am Natanim\'s bot. Please write me your message.')


@bot.message_handler(is_reply=True, chat_id=[ADMIN_ID], content_types=util.content_type_media)
def reply(msg: types.Message):
    user_id = msg.reply_to_message.forward_from.id
    message_id = msg.reply_to_message.forward_from_message_id
    bot.copy_message(user_id, ADMIN_ID, msg.message_id, reply_to_message_id=message_id)


@bot.message_handler(content_types=util.content_type_media)
def forward(msg: types.Message):
    bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)


@app.route()
def index():
    bot.set_webhook(WEBHOOK + '/' + TOKEN)
    return "Webhook sated to %s" % WEBHOOK


@app.route('/' + TOKEN, methods=['POST'])
def get_updates():
    json_string = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])

    return "Processed update"


bot.add_custom_filter(IsReplyFilter())
bot.add_custom_filter(ChatFilter())

if __name__ == '__main__':
    app.run()
    
