from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser
import random

app = Flask(__name__)
x = random.sample('1234567890', 4)
user_ID_dic = {}

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global x
    global user_ID_dic
    user_ID = event.source.user_id
    user_ID_dic[user_ID] = x
    
    y = event.message.text
    
    if (y.isdigit() == False):
        message = TextSendMessage(text= "Wrong Input!")
        line_bot_api.reply_message(event.reply_token, message)
        return 
    if (len(y) != 4):
        message = TextSendMessage(text= "Wrong Input!")
        line_bot_api.reply_message(event.reply_token, message)
        return 
    if (len(y) != len(set(y))):
        message = TextSendMessage(text= "Wrong Input!")
        line_bot_api.reply_message(event.reply_token, message)
        return 
    
    a = 0
    b = 0
    for i in range (len(y)):
        if(y[i] in user_ID_dic[user_ID]):
            if(y[i] == user_ID_dic[user_ID][i]):
                a += 1
            else:
                b += 1
    if(a == 4):
        x = random.sample('1234567890', 4)
    
    if (a == 4):
        message = [TextSendMessage(text= "%d A %d B\nCorrect!!" % (a, b)), 
                   TextSendMessage(text= "You are excellent!!")]
        line_bot_api.reply_message(event.reply_token, message)

    else:
        message = [TextSendMessage(text= "%d A %d B" % (a, b)), 
                   TextSendMessage(text= "Try again!!")]
        line_bot_api.reply_message(event.reply_token, message)
     
    user_ID_dic[user_ID] = x


if __name__ == "__main__":
    app.run()
