from __future__ import unicode_literals
# import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser

import random

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

x = random.sample('1234567890', 4)
user_id_dic = {}


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        print(body, signature)
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global x
    global user_id_dic
    user_id = event.source.user_id
    user_id_dic[user_id] = x

    y = event.message.text
    if not y.isdigit():
        message = TextSendMessage(text="Wrong Input!")
        line_bot_api.reply_message(event.reply_token, message)
        return
    if len(y) != 4:
        message = TextSendMessage(text="Wrong Input!")
        line_bot_api.reply_message(event.reply_token, message)
        return
    if len(y) != len(set(y)):
        message = TextSendMessage(text="Wrong Input!")
        line_bot_api.reply_message(event.reply_token, message)
        return

    a = 0
    b = 0
    for i in range(len(y)):
        if y[i] in user_id_dic[user_id]:
            if y[i] == user_id_dic[user_id][i]:
                a += 1
            else:
                b += 1
    if a == 4:
        x = random.sample('1234567890', 4)

    if a == 4:
        message = [TextSendMessage(text="%d A %d B\nCorrect!!" % (a, b)),
                   TextSendMessage(text="You are excellent!!")]
        line_bot_api.reply_message(event.reply_token, message)

    else:
        message = [TextSendMessage(text="%d A %d B" % (a, b)),
                   TextSendMessage(text="Try again!!")]
        line_bot_api.reply_message(event.reply_token, message)

    user_id_dic[user_id] = x


if __name__ == "__main__":
    app.run()
