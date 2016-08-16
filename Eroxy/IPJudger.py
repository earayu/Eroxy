import requests
import time


# proxy: 传入代理IP和端口, 如 62.219.95.13:8080
# timeout:超时时间   https:默认False时使用http协议,否则使用https协议
# verify:verify为空时,默认检测IP的网站为httpbin.org/ip. verify可以接受一个网址来覆盖IPJudger的默认行为
# 需要注意的是，网址前不要带协议(直接使用如'www.google.com'形式。)
def HTTPJudger(proxy, timeout=10, https=False, verify=None):
    protocal = 'http'
    if https:
        protocal = 'https'
    _proxy = {protocal: proxy}
    try:
        if verify is None:
            start_time_stamp = time.time()
            o = requests.get(protocal + '://httpbin.org/ip', proxies=_proxy, timeout=timeout)
            end_time_stamp = time.time()
            _delay = int((end_time_stamp - start_time_stamp) * 1000)
            if o.text.startswith('{\n  "origin":'):
                return proxy, _delay
        else:
            start_time_stamp = time.time()
            o = requests.get(protocal + '://' + verify, proxies=_proxy, timeout=timeout)
            end_time_stamp = time.time()
            _delay = int((end_time_stamp - start_time_stamp) * 1000)
            # TODO 这里需要思考一下判断IP可用性的方法
            # if o.status_code < 350:
            return proxy, _delay
        return None
    except:
        return None


# 通用的IP验证函数，能验证各种协议   HTTP,HTTPS,SOCK5
def ProxyJudger(proxy, timeout=10, protocal='HTTP', verify=None):
    _proxy = {protocal: proxy}





