"""每天早上给她发一条微信模板消息：深圳天气 + 赣州大余天气 + 在一起第 N 天 + 一句情话。

运行方式：
    python main.py            # 真实发送
    python main.py --dry-run  # 只打印将要发送的内容，不调用微信接口

对应模板内容（测试号）：
    早安呀
    深圳  {{weather.DATA}}
    赣州大余  {{weather1.DATA}}
    和吴世婷在一起的第 {{days.DATA}} 天
    {{words.DATA}}

环境变量（GitHub Secrets 注入）：
    APP_ID / APP_SECRET / TEMPLATE_ID / USER_ID   微信公众号测试号
    START_DATE   在一起的起始日，默认 2026-06-06（当天记为第 1 天）
"""
import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import date, datetime

import requests
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("morning")

# ---------------------------------------------------------------- 配置
def env(name, default=""):
    """读环境变量；未配置或值为空串时回退到默认值。

    注意：GitHub Actions 里如果 Secrets 没配，${{ secrets.X }} 会注入空字符串，
    此时 os.environ.get(name, default) 拿到的是 "" 而不是 default，所以必须这样兜一层。
    """
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if default:
        log.warning("环境变量 %s 未配置，使用代码内默认值", name)
    return default


APP_ID = env("APP_ID", "wx6a015110f0bb2145")
APP_SECRET = env("APP_SECRET", "0598dca7b68a709e2699d4abf39b0307")
TEMPLATE_ID = env("TEMPLATE_ID", "pnLf8O1UEMxnqsCj0PGf6g3HhMp5IrDEORo8zYVWddQ")
USER_ID = env("USER_ID", "o90D15m499vdYkJrvn1uZVSTV6Y4")

# 在一起的第一天（模板里是「和吴世婷在一起的第 X 天」，所以 6 月 6 日算第 1 天）
START_DATE = env("START_DATE", "2026-06-06")

# 和风天气 free key：两个域名都试（老账号 devapi，新账号 api）
QWEATHER_KEY = env("QWEATHER_KEY", "41f149042b9e41a0ae2320cdcdb16458")
QWEATHER_HOSTS = ("devapi.qweather.com", "api.qweather.com")

# 两个城市的 location id：深圳、赣州大余
CITIES = (
    ("深圳", "101280601"),
    ("赣州大余", "101240705"),
)

TIMEOUT = 10
RETRIES = 3

_session = requests.Session()


# ---------------------------------------------------------------- 工具
def get_json(url, retries=RETRIES):
    """带超时和重试的 GET，全部失败返回 None（不让单个接口拖垮整个任务）。"""
    for attempt in range(1, retries + 1):
        try:
            resp = _session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            log.warning("第 %d/%d 次请求失败: %s -> %s", attempt, retries, url, exc)
            if attempt < retries:
                time.sleep(2)
    return None


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# ---------------------------------------------------------------- 天气
def get_weather(location, city_name):
    """返回某个城市今天的天气文本，例如「晴  23° ~ 29°」。"""
    path = f"/v7/weather/3d?location={location}&key={QWEATHER_KEY}"
    for host in QWEATHER_HOSTS:
        data = get_json(f"https://{host}{path}")
        if not data or data.get("code") != "200":
            log.warning("和风天气 %s 不可用(%s): %s", host, city_name, data)
            continue
        today = data["daily"][0]
        return f'{today["textDay"]}  {today["tempMin"]}° ~ {today["tempMax"]}°'

    log.error("%s 天气获取失败", city_name)
    return "天气获取失败"


# ---------------------------------------------------------------- 情话
def get_words():
    data = get_json("https://api.shadiao.pro/chp")
    text = (data or {}).get("data", {}).get("text")
    if not text:
        log.warning("情话接口不可用，使用兜底文案")
        return "今天也要开开心心的，我在想你"

    # 模板消息的字段值不支持换行，多行情话会被挤成一行，这里统一压平
    return " ".join(text.split())


# ---------------------------------------------------------------- 在一起的天数
def get_together_days():
    """在一起第几天，起始日当天算第 1 天。"""
    start = None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            start = datetime.strptime(START_DATE, fmt)
            break
        except ValueError:
            continue
    if not start:
        log.error("START_DATE 格式无法解析: %r，期望 2026-06-06", START_DATE)
        return None
    return (date.today() - start.date()).days + 1


# ---------------------------------------------------------------- 发送
def build_payload():
    days = get_together_days()
    return {
        "weather": {"value": get_weather(CITIES[0][1], CITIES[0][0]), "color": get_random_color()},
        "weather1": {"value": get_weather(CITIES[1][1], CITIES[1][0]), "color": get_random_color()},
        "days": {"value": str(days) if days else "—", "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()},
    }


def send(payload):
    client = WeChatClient(APP_ID, APP_SECRET)
    for attempt in range(1, RETRIES + 1):
        try:
            return WeChatMessage(client).send_template(USER_ID, TEMPLATE_ID, payload)
        except Exception as exc:
            log.warning("第 %d/%d 次发送失败: %s", attempt, RETRIES, exc)
            if attempt < RETRIES:
                time.sleep(3)
    return None


def main():
    parser = argparse.ArgumentParser(description="发送每日早安模板消息")
    parser.add_argument("--dry-run", action="store_true", help="只打印内容，不实际发送")
    args = parser.parse_args()

    payload = build_payload()

    # 按模板版式渲染一遍，方便肉眼确认（模板骨架里的换行在这里还原）
    log.info(
        "消息预览:\n早安呀\n%s  %s\n%s  %s\n和吴世婷在一起的第 %s 天\n%s",
        CITIES[0][0],
        payload["weather"]["value"],
        CITIES[1][0],
        payload["weather1"]["value"],
        payload["days"]["value"],
        payload["words"]["value"],
    )

    if args.dry_run:
        log.info("dry-run 结束，未发送。原始 data:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not all([APP_ID, APP_SECRET, TEMPLATE_ID, USER_ID]):
        log.error("缺少 APP_ID / APP_SECRET / TEMPLATE_ID / USER_ID，"
                  "请在仓库 Settings > Secrets and variables > Actions 中配置")
        return 1

    res = send(payload)
    if res is None:
        log.error("消息发送失败，已重试 %d 次", RETRIES)
        return 1

    log.info("微信返回: %s", res)
    errcode = res.get("errcode", 0) if isinstance(res, dict) else 0
    if errcode != 0:
        log.error("微信返回错误码 %s: %s", errcode, res.get("errmsg"))
        return 1

    log.info("发送成功 msgid=%s", res.get("msgid"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
