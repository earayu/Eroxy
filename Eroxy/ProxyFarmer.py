import requests
import re
from Eroxy.Proxy import Proxy
from Eroxy.ProxyIP import IPJudger
import threading
import queue
import time


# 各个线程过滤完IP后都存在这里，按照delay排序
que = queue.PriorityQueue()


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
            r = requests.get(self.__url, timeout=(10, 30))
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

# 获取形如 2016-05-23 13:01:21 的时间字符串
def getTime(format="%Y-%m-%d %H:%M:%S"):
    timeArray = time.localtime(int(time.time()))
    formatTime = time.strftime(format, timeArray)
    return formatTime


# 送出可用IP
# TODO judger应该可以自定义过滤规则。待实现
def judger(proxy , timeout=10, https=False, verify=None):
    t = IPJudger(proxy.ip+':'+proxy.port, timeout, https, verify)
    if t is not None:
        proxy.inTime = getTime()
        proxy.delay = t[1]
        que.put(proxy)


if __name__ == '__main__':
    p = ProxyFarmer('http://www.ip-adress.com/proxy_list/')
    p.rules("(?<=<td>)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=:)\d{2,5}(?=</td>)')

    gen = p.process()
    for proxy in gen:
        print(proxy)

    # threads = []
    #
    # for proxy in p.harvest():
    #     t = threading.Thread(target=judger, args=(proxy,))
    #     threads.append(t)
    #     t.start()
    #
    # for t in threads:
    #     t.join()
    #
    # print('que:', que.queue)
    # while not que.empty():
    #     _proxy = que.get()
    #     print(_proxy)


