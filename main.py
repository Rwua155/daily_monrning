from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  weather1 = res['data']['list'][1]
  dqtqd =  str(math.floor(weather['low']))+'℃'
  dqtqg = str(math.floor(weather['high']))+'℃'
  mrtqd = str(math.floor(weather1['low']))+'℃'
  mrtqg =str(math.floor(weather1['high']))+'℃'
  return weather['weather'], dqtqd,dqtqg,weather['date'],weather1['weather'], mrtqd,mrtqg,weather1['date']
def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, dqd,dqg,lastTime,wea1, mqd,mqg,lastTime1 = get_weather()
# data = {"weather":{"value":wea},"temperature":{"value":temperature},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
data = {"weather":{"value":wea,"color":get_random_color()},"dqd":{"value":dqd,"color":get_random_color()},"dqg":{"value":dqg,"color":get_random_color()},"lastTime":{"value":lastTime,"color":get_random_color()},
        "weather1":{"value":wea1,"color":get_random_color()},"mqd":{"value":mqd,"color":get_random_color()},"mqg":{"value":mqg,"color":get_random_color()},"lastTime1":{"value":lastTime1,"color":get_random_color()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
