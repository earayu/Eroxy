# Eroxy

帮助我建立IP池、不断抓取、时时更新

基于正则表达式解析页面



```python
#添加一个目标网站
famer = ProxyFarmer('http://www.xicidaili.com/')
#根据页面自己撰写正则表达式, 传入解析IP和port的规则
famer.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=<td>)\d{2,5}(?=</td>)')
#存入数据库
famer.hibernate()
```

由于松耦合的设计, 抓取IP和port、校验代理可用性、持久化、代理验证方法等都可以替换成新的实现
