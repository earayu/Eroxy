import requests
import re
from Eroxy.Proxy import Proxy
from Eroxy.IPJudger import HTTPJudger
import threading
import queue
import pymysql
from Eroxy.utils import getTime

# 各个线程过滤完IP后都存在这里，按照delay排序
que = queue.PriorityQueue()


# ip_rule和port_rule是必填项。
# TODO 缺点在于必须用正则表达式精确匹配IP和PORT。
class ProxyFarmer:
    """
    使用前先DIY一个实例出来, url和 rule是必须的
    _rule结尾的是正则表达式参数。分别匹配页面上的ip, port, 匿名性, 所在地, 协议类型
    可以设置headers和cookies, 甚至是proxies和data。以免被网站屏蔽这个爬虫
    """
    def __init__(self, url):
        self.__url = url

        self.__ip_rule = None
        self.__port_rule = None
        self.__type_rule = None
        self.__location_rule = None
        self.__protocol_rule = None

        self.__headers = None
        self.__cookies = None
        self.__proxies = None
        self.__data = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, headers):
        self.__headers = headers

    @property
    def cookies(self):
        return self.__cookies

    @cookies.setter
    def cookies(self, cookies):
        self.__cookies = cookies

    @property
    def proxies(self):
        return self.__proxies

    @proxies.setter
    def proxies(self, proxies):
        self.__proxies = proxies

    # 5个正则表达式作为参数，个人感觉不太友好
    def rules(self, ip_rule, port_rule, type_rule=None, location_rule=None, protocol_rule=None):
        self.__ip_rule = ip_rule
        self.__port_rule = port_rule
        self.__type_rule = type_rule
        self.__location_rule = location_rule
        self.__protocol_rule = protocol_rule

    # 收获raw_ip. 这些IP没经过验证。
    def harvest(self):
        try:
            r = requests.get(self.__url, timeout=10, headers=self.__headers, cookies=self.__cookies, proxies=self.__proxies, data=self.__data)
        except:
            return None

        # 用正则解析页面内容
        if self.__ip_rule is not None:
            r_ip = re.findall(self.__ip_rule, r.text)

        if self.__port_rule is not None:
            r_port = re.findall(self.__port_rule, r.text)
        else:
            r_port = None

        if self.__type_rule is not None:
            r_type = re.findall(self.__type_rule, r.text)
        else:
            r_type = None

        if self.__location_rule is not None:
            r_location = re.findall(self.__location_rule, r.text)
        else:
            r_location = None

        if self.__protocol_rule is not None:
            r_protocol = re.findall(self.__protocol_rule, r.text)
        else:
            r_protocol = None

        # 生成Proxy对象
        for i in range(0, len(r_ip)):
            p = Proxy()
            if r_ip is not None:
                p.ip = r_ip[i]
            if r_port is not None:
                p.port = r_port[i]
            if r_type is not None:
                p.type = r_type[i]
            if r_location is not None:
                p.location = r_location[i]
            if r_protocol is not None:
                p.protocol = r_protocol[i]
            yield p

    # 筛选raw_ip，挑出符合要求的
    # 为每个代理开一个线程, 然后测试可用性
    def shive(self):
        threads = []
        for proxy in self.harvest():
            t = threading.Thread(target=judger, args=(proxy,))
            threads.append(t)
            t.start()
        # TODO 阻塞了, 要所有线程都完成才能进行下一步
        for t in threads:
            t.join()
        while not que.empty():
            _proxy = que.get()
            yield _proxy

    # 将数据持久化, 通过回调函数save, 可以自定义持久化方式。需要实现save接口
    def hibernate(self):
        gen = self.shive()
        for proxy in gen:
            try:
                save2mysql(proxy)
            except Exception as e:
                print(e)


# pymysql的connection是非线程安全的
def save2mysql(proxy):
    conn = pymysql.connect(host='localhost', user='root', passwd='qwqwqw', db='Eroxy', port=3306, charset='utf8')
    cur = conn.cursor()
    ssql = 'select ip, port from proxy where ip = %s'
    cur.execute(ssql, (proxy.ip, ))
    ret = cur.fetchall()
    # 如果该IP已经存在, 更新延迟。否则插入数据库
    if ret is not ():
        usql = 'update proxy set delay=%s, alive=1 where ip=%s'
        cur.execute(usql, (proxy.delay, proxy.ip))
        print(usql % (proxy.delay, proxy.ip))
    else:
        isql = 'insert into proxy (ip,port,delay,inTime,location,protocal,alive) VALUES (%s,%s,%s,%s,%s,%s,1)'
        cur.execute(isql, (proxy.ip, proxy.port, proxy.delay, proxy.inTime, proxy.location, proxy.protocol))
        print(isql % (proxy.ip, proxy.port, proxy.delay, proxy.inTime, proxy.location, proxy.protocol))
    conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源


# 生成可用IP, judger接受一个回调函数。可以自定义proxy可用性的判定规则。
# anyJudger参数需要实现类似于HTTPJudger的接口
def judger(proxy, anyJudger=HTTPJudger, timeout=10, https=False, verify=None):
    t = anyJudger(proxy.ip + ':' + proxy.port, timeout, https, verify)
    if t is not None:
        proxy.inTime = getTime()
        proxy.delay = t[1]
        que.put(proxy)


if __name__ == '__main__':
    my_headers = \
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        }

    p2 = ProxyFarmer('http://www.xicidaili.com/')
    p2.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=<td>)\d{2,5}(?=</td>)')
    p2.headers = my_headers

    p2.hibernate()

