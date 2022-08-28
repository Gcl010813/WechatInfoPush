from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_access_token():
    # appId
    id = config["app_id"]
    # appSecret
    secret = config["app_secret"]
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+id+"&secret="+secret
    try:
        access_token = get(url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token

newhead = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"}


def get_weather(local, key):
    url = 'https://devapi.qweather.com/v7/weather/now?location={}&key={}'.format(local, key)
    data = get(url, headers=newhead).json()['now']

    Temp = data['temp'] + "℃"  # 温度(摄氏度)
    Text = data['text']  # 天气描述
    WindDir = data['windDir']  # 风向
    WindSpe = data['windSpeed'] + "m/s"  # 风速
    Precip = data['precip'] + "mm"  # 降雨量

    return Temp, Text, WindDir, WindSpe, Precip


def get_birthday(birthday, year, today):
    # 判断是否为农历生日
    if birthday.split('-')[0][0] == "r":
        mouth = int(birthday.split("-")[1])
        day = int(birthday.split("-")[2])
        # 获取农历生日对应的公历生日
        try:
            birthday = ZhDate(year, mouth, day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        # 按照公历今年生日的日期
        birthday_date = date(year, birthday.month, birthday.day)

    else:
        # 获取公历生日的今年对应月和日
        month = int(birthday.split("-")[1])
        day = int(birthday.split("-")[2])
        # 今年公历生日日期
        birthday_date = date(year, month, day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > birthday_date:
        # 如果是农历生日
        if birthday.split('-')[0][0] == "r":
            # 根据农历生日的月和日获取明年的公历生日的月和日
            last_birthday = ZhDate((year + 1), mouth, day).to_datetime().date()
            # 重新组合成明年的公历生日
            birth_date = date((year + 1), last_birthday.month, last_birthday.day)
        else:
            birth_date = date((year + 1), mouth, day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == birthday_date:
        birth_day = 0
    else:
        birth_date = birthday_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day


def send_message(user, access_token, temp, text, winddir, windspe, precip):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_date_list = list(map(int, config['love_date'].split('-')))
    love_date = date(love_date_list[0], love_date_list[1], love_date_list[2])
    # # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 生日提示
    Info=config['birthday']
    # 获取距离下次生日的时间
    birth_day = get_birthday(Info["birthday"], year, today)
    if birth_day == 0:
        birthday_text = "今天{}生日哟,祝{}生日快乐！".format(Info["name"], Info["name"])
    else:
        birthday_text = "距离{}的生日还有{}天".format(Info["name"], birth_day)
    data = {
        "touser": user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "data": {
            "date": {
                "value": "{}{}".format(today, week)
            },
            "local": {
                "value": "驻马店市驿城区"
            },
            "temp": {
                "value": temp
            },
            "text": {
                "value": text
            },
            "winddir": {
                "value": winddir
            },
            "windspe": {
                "value": windspe
            },
            "precip": {
                "value": precip
            },
            "love_days": {
                "value": "今天是我们在一起的第{}天".format(love_days)
            },
            "birthday": {
                "value": birthday_text
            },
        },
    }

    response = post(url, headers=newhead, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    AccessToken = get_access_token()
    # 接收的用户
    Users = config["user"]
    # 传入地区获取天气信息
    Temp, Text, WindDir, WindSpe, Precip = get_weather(config['local_code'], config['weatherapi_key'])
    # 公众号推送消息
    for User in Users:
        send_message(User, AccessToken, Temp, Text, WindDir, WindSpe, Precip)
    os.system("pause")
