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
        self.__headers = None
        self.__cookies = None
        self.__proxies = None

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

    # IP必须设定规则，因为需要提供一个页面抓取的Proxy计数。
    # TODO 这儿rule要提供6个正则表达式太麻烦了，也许可以建立一个rules对象来管理。
    # TODO 而且ProxyFarmer对正则表达式的准确度要求较高。不准确的正则表达式会引发不确定的错误。
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
            r = requests.get(self.__url, timeout=(10, 30), headers=self.__headers, cookies=self.__cookies, proxies=self.__proxies)
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

    # 筛选raw_ip，挑出符合要求的
    # TODO 这里开线程，阻塞至最慢的线程返回
    def shive(self):
        threads = []
        for proxy in self.harvest():
            t = threading.Thread(target=judger, args=(proxy,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        while not que.empty():
            _proxy = que.get()
            yield _proxy

    def hibernate(self):
        gen = self.shive()
        for proxy in gen:
            try:
                save(proxy)
            # TODO 这里应该处理主键重复错误，更新记录。或者写个saveOrUpdate函数
            except Exception as e:
                print(e)


# pymysql的connection是非线程安全的
def save(proxy):
    conn = pymysql.connect(host='localhost', user='earayu', passwd='qwqwqw', db='Eroxy', port=3306, charset='utf8')
    cur = conn.cursor()
    ssql = 'select ip, port from proxy2 where ip = %s'
    cur.execute(ssql, (proxy.ip, ))
    ret = cur.fetchall()
    # update the delay if the proxy exists, or do a insertation
    if ret is not ():
        usql = 'update proxy2 set delay=%s where ip=%s'
        cur.execute(usql, (proxy.delay, proxy.ip))
        print(usql % (proxy.delay, proxy.ip))
    else:
        # TODO 这里和rules严重耦合了，需要修改
        isql = 'insert into proxy2 (ip,port,delay,inTime,location,protocal) VALUES (%s,%s,%s,%s,%s,%s)'
        cur.execute(isql, (proxy.ip, proxy.port, proxy.delay, proxy.inTime, proxy.location, proxy.protocol))
        print(isql % (proxy.ip, proxy.port, proxy.delay, proxy.inTime, proxy.location, proxy.protocol))
    conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源


# 获取形如 2016-05-23 13:01:21 的时间字符串
def getTime(format="%Y-%m-%d %H:%M:%S", offset=0):
    timeArray = time.localtime(int(time.time() + offset))
    formatTime = time.strftime(format, timeArray)
    return formatTime


# 送出可用IP
# TODO judger应该可以自定义过滤规则。待实现
def judger(proxy, timeout=10, https=False, verify=None):
    t = HTTPJudger(proxy.ip + ':' + proxy.port, timeout, https, verify)
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

    # p = ProxyFarmer('http://www.youdaili.net/Daili/http/4435.html')
    # p.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=\d:)\d{2,5}(?=@)', protocol_rule='(?<=@).*?(?=#)',
    #         location_rule='(?<=P#).*?(?=\W)')
    # p.headers = my_headers
    # p.proxies = {'http': '117.21.182.110:80'}
    # p.hibernate()

    p2 = ProxyFarmer('http://www.idcloak.com/proxylist/free-proxy-ip-list.html')
    p2.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=<td>)\d{2,5}(?=</td>)', protocol_rule='(?<=<td>)https?(?=</td>)',
             location_rule='(?<=">)[A-Za-z]*?(?=&nbsp;)')

    while True:
        p2.hibernate()
        time.sleep(300)

