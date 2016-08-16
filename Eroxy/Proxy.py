import time


class Proxy:
    """
    代理类, 描述了代理对象。
    """
    def __init__(self):
        self.__ip = ''
        self.__port = ''
        # __delay应该是一个整数,但传入字符串也可以。比较的时候转int,虽然可能会稍微影响效率
        # __delay作为优先队列排序的依据
        self.__delay = 0
        self.__type = ''
        self.__location = ''
        self.__inTime = ''
        self.__protocol = ''
        self.__life = ''

    def __lt__(self, other):
        return int(self.delay) < int(other.delay)

    def __gt__(self, other):
        return int(self.delay) > int(other.delay)

    def __eq__(self, other):
        return int(self.delay) == int(other.delay)

    def __str__(self):
        s = 'ip = ' + self.__ip, 'port = ' + self.__port, 'delay = ' + str(self.__delay), 'type = ' + self.__type, 'location = ' + self.__location, 'inTime = ' + self.__inTime, 'protocol = ' + self.__protocol, 'life = ' + self.__life
        return str(s)

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        self.__ip = ip

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = port

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, delay):
        self.__delay = delay

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type):
        self.__type = type

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, location):
        self.__location = location

    @property
    def inTime(self):
        return self.__inTime

    @inTime.setter
    def inTime(self, inTime):
        self.__inTime = inTime

    @property
    def protocol(self):
        return self.__protocol

    @protocol.setter
    def protocol(self, protocol):
        self.__protocol = protocol

    @property
    def life(self):
        return self.__life

    @life.setter
    def life(self, life):
        self.__life = life


if __name__ == '__main__':
    p1 = Proxy()
    p2 = Proxy()
    p1.delay = '200'
    p2.delay = 200
    print(type(p1.__str__()))



