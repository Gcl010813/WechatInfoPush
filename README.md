首先你需要申请一个微信公众号测试号 链接：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

注册账号后页面显示 appID，appsecret, 测试号二维码，模板消息接口

让接收推送消息的微信扫描测试号二维码并关注后，右侧显示微信昵称和微信号

新增测试模板，模板标题即为推送消息第一行显示的文字，模板内容可根据自己需要来自定义，自动生成模板ID

打开和风天气开发平台 链接：https://dev.qweather.com/docs/api/

注册账号后登录，在左侧应用管理里面创建应用，选择免费开发版-->Web Api 后，页面显示KEY

在此链接里面查询当地对应的的 location_ID 编号 链接：https://github.com/qwd/LocationList/blob/master/China-City-List-latest.csv

打开PersonInfo.txt文件，替换其中的app_id(appID)，app_secret(appsecret)，template_id(模板ID),user(公众平台显示的微信号)，weather_key(KEY),location(Location_ID)，生日/在一起的日子
