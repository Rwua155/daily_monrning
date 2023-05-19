# from datetime import date, datetime
# import math
# from wechatpy import WeChatClient
# from wechatpy.client.api import WeChatMessage, WeChatTemplate
# import requests
# import os
# import random

# today = datetime.now()
# start_date = os.environ['START_DATE']
# city = os.environ['CITY']
# birthday = os.environ['BIRTHDAY']

# app_id = os.environ["APP_ID"]
# app_secret = os.environ["APP_SECRET"]

# user_id = os.environ["USER_ID"]
# template_id = os.environ["TEMPLATE_ID"]


# def get_weather():
#     url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city="+city
#     res = requests.get(url).json()

#     code = res['code']
#     if code == 0:
#         toDayWeather = res['data']['list'][0]
#         toMorrowWeather = res['data']['list'][1]
#         datq = toDayWeather['weather']
#         mrtq = toMorrowWeather['weather']
#         dqtqd = str(math.floor(toDayWeather['low']))+'℃'
#         dqtqg = str(math.floor(toDayWeather['high']))+'℃'
#         mrtqd = str(math.floor(toMorrowWeather['low']))+'℃'
#         mrtqg = str(math.floor(toMorrowWeather['high']))+'℃'

#     else:
#         url = "https://restapi.amap.com/v3/weather/weatherInfo?key=26111970b11fc6e5141d2de555e40f36&city=440300&extensions=all&output=JSON"
#         res = requests.get(url).json()
#         toDayWeather = res['forecasts'][0]['casts'][0]
#         toMorrowWeather = res['forecasts'][0]['casts'][1]
#         datq = toDayWeather['dayweather']
#         mrtq = toMorrowWeather['dayweather']
#         dqtqd = str(toDayWeather['nighttemp'])+'℃'
#         dqtqg = str(toDayWeather['daytemp'])+'℃'
#         mrtqd = str(toMorrowWeather['nighttemp'])+'℃'
#         mrtqg = str(toMorrowWeather['daytemp'])+'℃'

#     fh = '深圳' + ' 今日天气:  '+datq + '  ' + dqtqd + ' ~ ' + dqtqg
#     mr = '深圳' + ' 明日天气:  '+mrtq + '  ' + mrtqd + ' ~ ' + mrtqg
#     return fh, mr, datq, mrtq


# def get_count():
#     delta = today - datetime.strptime(start_date, "%Y-%m-%d")
#     return delta.days


# def get_birthday():
#     next = datetime.strptime(str(date.today().year) +
#                              "-" + birthday, "%Y-%m-%d")
#     if next < datetime.now():
#         next = next.replace(year=next.year + 1)
#     return (next - today).days


# def get_words():
#     words = requests.get("https://api.shadiao.pro/chp")
#     if words.status_code != 200:
#         return get_words()
#     return words.json()['data']['text']


# def get_random_color():
#     return "#%06x" % random.randint(0, 0xFFFFFF)


# client = WeChatClient(app_id, app_secret)

# wm = WeChatMessage(client)
# wea, wea1, lastTime, lastTime1 = get_weather()
# data = {"weather": {"value": wea, "color": get_random_color()}, "lastTime": {"value": lastTime, "color": get_random_color()},
#         "weather1": {"value": wea1, "color": get_random_color()}, "lastTime1": {"value": lastTime1, "color": get_random_color()}, "words": {"value": get_words(), "color": get_random_color()}}


# res = wm.send_template(user_id, template_id, data)
# print(res)









from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random


def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city='深圳'"
    res = requests.get(url).json()

    code = res['code']
    if code == 0:
        toDayWeather = res['data']['list'][0]
        toMorrowWeather = res['data']['list'][1]
        datq = toDayWeather['weather']
        mrtq = toMorrowWeather['weather']
        dqtqd = str(math.floor(toDayWeather['low']))+'℃'
        dqtqg = str(math.floor(toDayWeather['high']))+'℃'
        mrtqd = str(math.floor(toMorrowWeather['low']))+'℃'
        mrtqg = str(math.floor(toMorrowWeather['high']))+'℃'

    else:
        url = "https://restapi.amap.com/v3/weather/weatherInfo?key=26111970b11fc6e5141d2de555e40f36&city=440300&extensions=all&output=JSON"
        res = requests.get(url).json()
        toDayWeather = res['forecasts'][0]['casts'][0]
        toMorrowWeather = res['forecasts'][0]['casts'][1]
        datq = toDayWeather['dayweather']
        mrtq = toMorrowWeather['dayweather']
        dqtqd = str(toDayWeather['nighttemp'])+'°'
        dqtqg = str(toDayWeather['daytemp'])+'°'
        mrtqd = str(toMorrowWeather['nighttemp'])+'°'
        mrtqg = str(toMorrowWeather['daytemp'])+'°'

    fh = datq + '  ' + dqtqd + ' ~ ' + dqtqg
    mr = mrtq + '  ' + mrtqd + ' ~ ' + mrtqg
    return fh, mr, datq, mrtq


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient("wx6a015110f0bb2145", "0598dca7b68a709e2699d4abf39b0307")

wm = WeChatMessage(client)
wea, wea1, lastTime, lastTime1 = get_weather()
data = {"weather": {"value": wea, "color": get_random_color()},
        "weather1": {"value": wea1, "color": get_random_color()}, "words": {"value": get_words(), "color": get_random_color()}}


res = wm.send_template("o90D15m499vdYkJrvn1uZVSTV6Y4", "8oyGgkQn9fsV22mu_5Aw4OPYenluhy2N3ya725xG5Wg", data)
print(data)
print(res)
