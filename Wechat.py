from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate



#access_token相关
def get_access_token(id,secret):
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+id+"&secret="+secret
    try:
        access_token = get(url).json()['access_token']
        return access_token
    except KeyError:
        print("请检查app_id和app_secret")
        return 0


#伪装浏览器,防反爬虫技术
newhead = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"}


#天气相关
def get_weather(local, key):
    #和风天气查询网址
    url = "https://devapi.qweather.com/v7/weather/now?location="+local+"&key="+key
    #获取天气信息字典
    data = get(url, headers=newhead).json()['now']

    Temp = data['temp'] + "℃"  # 温度(摄氏度)
    Text = data['text']  # 天气描述
    WindSpe = data['windSpeed'] + "m/s"  # 风速
    
    return Temp, Text, WindSpe


def get_birthday(birthday, year, today):
    # 判断是否为农历生日
    if birthday.split('-')[0][0] == "r":
        mouth = int(birthday.split("-")[1])
        day = int(birthday.split("-")[2])
        # 获取农历生日对应的公历生日
        try:
            birthday = ZhDate(year, mouth, day).to_datetime().date()
        except TypeError:
            print("查看今年是否有农历对应的公历生日")
        # 今年公历生日日期
        birthday_date = date(year, birthday.month, birthday.day)
    else:
        # 获取公历生日的今年对应月和日
        month = int(birthday.split("-")[1])
        day = int(birthday.split("-")[2])
        # 今年公历生日日期
        birthday_date = date(year, month, day)

    # 生日已过
    if today > birthday_date:
        if birthday.split('-')[0][0] == "r":
            # 根据农历生日的月和日获取明年公历生日的月和日
            last_birthday = ZhDate((year + 1), mouth, day).to_datetime().date()
            # 重新组合成明年的公历生日
            birth_date = date((year + 1), last_birthday.month, last_birthday.day)
        else:
            birth_date = date((year + 1), mouth, day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    #生日当天
    elif today == birthday_date:
        birth_day = 0
    #生日未过
    else:
        birth_date = birthday_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day

#消息推送
def send_message(user, access_token,info):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+access_token

    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    #当前时间年/月/日 重组当前时间
    today = datetime.date(datetime(localtime().tm_year, localtime().tm_mon, localtime().tm_mday))
    #当天周几
    week = week_list[today.isoweekday() % 7]

    # 获取在一起的日子的日期格式
    love_date_list = list(map(int, info['love_date'].split('-')))
    love_date = date(love_date_list[0], love_date_list[1], love_date_list[2])
    #获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]

    #获取姓名/生日信息
    bir=info["birthday_info"]

    birth_day = get_birthday(bir['birthday'], localtime().tm_year, today)
    if birth_day == 0:
        birthday_text = "祝{}生日快乐哟~♕".format(bir["name"], bir["name"])
    else:
        birthday_text = "{}天后是{}生日哟~".format(birth_day,bir["name"])

    Temp, Text, WindSpe = get_weather(info['local_code'], info['weatherapi_key'])
    data = {
        "touser": user,
        "template_id": info["template_id"],
        "url": "http://weixin.qq.com/download",
        "data": {
            "date": {
                "value": "{} {}".format(today, week)
            },
            "local": {
                "value": "驻马店市驿城区"
            },
            "temp": {
                "value": Temp
            },
            "text": {
                "value": Text
            },
            "wind_spe": {
                "value": WindSpe
            },
            "birthday": {
                "value": birthday_text
            },
            "love_days": {
                "value": "今天是我们在一起的第{}天".format(love_days)
            },
        },
    }
    response = post(url, headers=newhead, json=data).json()
    if response["errcode"] == 0:
        print("Successful")
    else:
        print("Error")


if __name__ == "__main__":
    try:
        with open("PersonInfo.txt", encoding="utf-8") as f:
            Info = eval(f.read())
    except:
        print("PersonInfo配置文件异常")

    # 获取accessToken
    AccessToken = get_access_token(Info["app_id"],Info["app_secret"])
    # 接收的用户
    Users = Info["user"]
    # 公众号推送消息
    for User in Users:
        send_message(User, AccessToken,Info)
