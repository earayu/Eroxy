# Eroxy

帮助我建立IP池、不断抓取、时时更新

基于正则表达式解析页面



```python
from Eroxy import ProxyFarmer
from Eroxy import ProxyPatrol


if __name__ == '__main__':
    # 添加一个目标网站
    famer = ProxyFarmer('http://www.xicidaili.com/')
    # 根据页面自己撰写正则表达式, 传入解析IP和port的规则
    famer.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=<td>)\d{2,5}(?=</td>)')

    # 存入数据库
    famer2 = ProxyFarmer('another url')
    famer2.rules("ip regex", 'port regex')

    famer.hibernate()
    famer2.hibernate()

    # 检验IP可用性和延迟
    ProxyPatrol.loop()

```

由于松耦合的设计, 抓取IP和port、校验代理可用性、持久化、代理验证方法等都可以替换成新的实现


```python
famer2 = ProxyFarmer('another url')
famer2.rules("ip regex", 'port regex')
# ProxyFarmer使用requests库抓取页面, 所以requests支持的功能, 它也行噢
famer2.headers = ...
famer2.cookies = ...

# IPJudger.py
实现ProxyJudger接口的函数可以作为校验IP用
不过一般来说默认提供的HTTPJudger已经够用了

# proxy: 传入代理IP和端口, 如 62.219.95.13:8080
# timeout:超时时间   https:默认False时使用http协议,否则使用https协议
# verify:verify为空时,默认检测IP的网站为httpbin.org/ip. verify可以接受一个网址来覆盖IPJudger的默认行为
# 需要注意的是，网址前不要带协议(直接使用如'www.google.com'形式。)
def HTTPJudger(proxy, timeout=10, https=False, verify=None)
```
