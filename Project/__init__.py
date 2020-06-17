from flask import Flask, request, abort
import requests
import json
import sys
from Project.Config import *
from uncleengineer import thaistock
from googlefinance import getQuotes
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor Sensor#1
# GPIO.setup(13, GPIO.IN)         #Read output from PIR motion sensor Sensor#2
GPIO.setup(3, GPIO.OUT)         #LED output pin Sensor#1 For Open Door
GPIO.setup(5, GPIO.OUT)         #LED output pin Sensor#2 For Close Door
app = Flask(__name__)


def GET_BTC_PRICE():
    data = requests.get('https://bx.in.th/api/')
    BTC_PRICE = data.text.split('BTC')[1].split('last_price":')[1].split(',"volume_24hours')[0]
    return BTC_PRICE




@app.route('/webhook', methods=['POST','GET'])
def webhook():
    GPIO.output(5, 0)  #Turn ON LED Ready
    GPIO.output(3, 0)  #Turn OFF LED
    if request.method == 'POST':
        payload = request.json
        print(payload)
        # print(payload)
        Reply_token = payload['events'][0]['replyToken']
        print(Reply_token)
        
        
        
        # command = message[:4]
        
        # ReplyMessage(Reply_token,stock,Channel_access_token)
        if payload['events'][0]['message']['type'] == 'text' :
            message = payload['events'][0]['message']['text']
            print(message)
            print(len(message))
            stock = message[5:]
            print(stock)
            if 'หุ้น' in message :
                ITD = thaistock(stock)
                print(ITD)
                print('================')
                # StockData(ITD)
                print('================')
                Reply_messasge = 'ราคาหุ้น ' + stock + ' ขณะนี้ : {}'.format(ITD)
                print(Reply_messasge)
                ReplyMessage(Reply_token,Reply_messasge,Channel_access_token)
            elif 'เปิดประตู' in message :
                GPIO.output(3, 1)  #Turn ON LED
                GPIO.output(5, 0)  #Turn ON LED Wait
                time.sleep(10)
                GPIO.output(5, 0)  #Turn ON LED Ready
                GPIO.output(3, 0)  #Turn OFF LED
                ReplyMessage(Reply_token,"เปิดประตูแล้วครับ",Channel_access_token)
            elif 'ปิดประตู' in message :
                GPIO.output(3, 0)  #Turn ON LED
                GPIO.output(5, 1)  #Turn ON LED Wait
                time.sleep(10)
                GPIO.output(5, 0)  #Turn ON LED Ready
                GPIO.output(3, 0)  #Turn OFF LED
                ReplyMessage(Reply_token,"ปิดประตูแล้วครับ",Channel_access_token)
            else:
                ReplyMessage(Reply_token,"ผมยังไม่เข้าใจคำสั่งครับ",Channel_access_token)
        elif payload['events'][0]['message']['type'] == 'audio' :
            msgtype = payload['events'][0]['message']['type']
            print(msgtype)
            print("ผมยังไม่เข้าใจคำสั่งครับ")
            ReplyMessage(Reply_token,"ผมยังไม่เข้าใจคำสั่งครับ",Channel_access_token)
        # elif "btc" in message :
        #     Reply_messasge = 'ราคา BITCOIN ขณะนี้ : {}'.format(GET_BTC_PRICE())
        #     ReplyMessage(Reply_token,Reply_messasge,Channel_access_token)


        return payload, 200

    elif request.method == 'GET' :
        return 'this is method GET!!!' , 200

    else:
        abort(400)

@app.route('/')
def hello():
    return 'hello world book',200

def StockData(code):
    try:
        symbol = code
        print(json.dumps(getQuotes('SET:' + symbol), indent=2))
        print()
    except:
        print("Error:", sys.exc_info()[0])
        print("Description:", sys.exc_info()[1])

def ReplyMessage(Reply_token, TextMessage, Line_Acees_Token):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(Line_Acees_Token) ##ที่ยาวๆ
    print(Authorization)
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':Authorization
    }

    data = {
        "replyToken":Reply_token,
        "messages":[{
            "type":"text",
            "text":TextMessage
        }]
    }

    data = json.dumps(data) ## dump dict >> Json Object
    r = requests.post(LINE_API, headers=headers, data=data) 
    return 200