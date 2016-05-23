import requests
import re
from Eroxy.Proxy import Proxy
from Eroxy.IPJudger import HTTPJudger
import threading
import queue
import time
import pymysql


# 各个线程过滤完IP后都存在这里，按照delay排序
que = queue.PriorityQueue()

my_headers = \
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Cookie": "bdshare_ty=0x18; Hm_lvt_f8bdd88d72441a9ad0f8c82db3113a84=1463983094,1463985523; Hm_lpvt_f8bdd88d72441a9ad0f8c82db3113a84=1463985523",
        "Connection": "keep-alive",
        "Host": "www.youdaili.net",
        "Referer": "http://www.youdaili.net/Daili/http/4456.html",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }

# TODO 需要加入header, proxies, data, cookies 甚至auth 等字段。
# TODO Proxy类可以不填完整，只要有IP和PORT就行了。有了这些可以去IP库查询归属地，运营商等信息
class ProxyFarmer:
    def __init__(self, url):
        self.__url = url
        self.__ip_rule = None
        self.__port_rule = None
        self.__delay_rule = None
        self.__type_rule = None
        self.__location_rule = None
        self.__inTime_rule = None
        self.__protocol_rule = None
        self.__life_rule = None

    #IP必须设定规则，因为需要提供一个页面抓取的Proxy计数。
    #TODO 这儿rule要提供6个正则表达式太麻烦了，也许可以建立一个rules对象来管理。
    #TODO 而且ProxyFarmer对正则表达式的准确度要求较高。不准确的正则表达式会引发不确定的错误。
    def rules(self, ip_rule, port_rule=None, type_rule=None, location_rule=None, protocol_rule=None, life_rule=None):
        self.__ip_rule = ip_rule
        self.__port_rule = port_rule
        self.__type_rule = type_rule
        self.__location_rule = location_rule
        self.__protocol_rule = protocol_rule
        self.__life_rule = life_rule

    # 收获raw_ip. 这些IP没经过验证，很可能不能使用。
    def harvest(self):
        try:
            r = requests.get(self.__url, timeout=(10, 30), headers=my_headers)
            print(r.status_code)
        except:
            return None

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

        if self.__life_rule is not None:
            r_life = re.findall(self.__life_rule, r.text)
        else:
            r_life = None

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
            if r_life is not None:
                p.life = r_life[i]
            yield p

    # 加工收获的raw_ip
    def process(self):
        threads = []
        for proxy in self.harvest():
            t = threading.Thread(target=judger, args=(proxy,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        while not que.empty():
            _proxy = que.get()
            print(type(_proxy))
            yield _proxy

    def hibernate(self):
        gen = self.process()
        for proxy in gen:
            print(proxy)
            try:
                save(proxy)
            except  Exception:
                print("发生异常")


def save(proxy):
    conn = pymysql.connect(host='localhost', user='earayu', passwd='qwqwqw', db='Eroxy', port=3306,
                           charset='utf8')
    cur = conn.cursor()  # 获取一个游标
    sql = 'insert into proxy (ip,port,delay,location,inTime,protocal)' \
          + ' VALUES (\'' + proxy.ip + '\',\'' + str(proxy.port) + '\',\'' + str(proxy.delay) + '\',\'' + \
          proxy.location + '\',\'' + proxy.inTime + '\',\'' + proxy.protocol + '\')'
    print(sql)
    cur.execute(sql)
    conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源




# 获取形如 2016-05-23 13:01:21 的时间字符串
def getTime(format="%Y-%m-%d %H:%M:%S"):
    timeArray = time.localtime(int(time.time()))
    formatTime = time.strftime(format, timeArray)
    return formatTime


# 送出可用IP
# TODO judger应该可以自定义过滤规则。待实现
def judger(proxy , timeout=10, https=False, verify=None):
    t = HTTPJudger(proxy.ip + ':' + proxy.port, timeout, https, verify)
    if t is not None:
        proxy.inTime = getTime()
        proxy.delay = t[1]
        que.put(proxy)


if __name__ == '__main__':
    p = ProxyFarmer('http://www.youdaili.net/Daili/http/4456.html')
    p.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=\d:)\d{2,5}(?=@)', protocol_rule='(?<=@).*?(?=#)', \
            location_rule='(?<=P#).*?(?=\W)')

    p.hibernate()

