from Eroxy import ProxyFarmer
from Eroxy import ProxyPatrol


if __name__ == '__main__':
    famer = ProxyFarmer('http://www.xicidaili.com/')
    famer.rules("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '(?<=<td>)\d{2,5}(?=</td>)')

    famer2 = ProxyFarmer('another url')
    famer2.rules("ip regex", 'port regex')

    famer.hibernate()
    famer2.hibernate()

    # 检验IP可用性和延迟
    ProxyPatrol.loop()
