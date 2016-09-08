from Eroxy.ProxyFarmer import getTime
import threading
from Eroxy.IPJudger import HTTPJudger
from Eroxy.utils import execute
import time
from Eroxy.utils import select


# TODO 2次验证都失败的ip是删掉还是转移另一个表中？
def patrol(ip, port, alive):
    _proxy = ip + ':' + port
    ret = HTTPJudger(_proxy)
    if ret is not None:
        usql = 'update proxy set delay=%s, alive=1 where ip=%s'
        execute(usql, (ret[1], ret[0][:ret[0].index(':')]))
    elif alive == 0:
        dsql = 'delete from proxy where ip=%s'
        execute(dsql, (ip, ))
    elif alive == 1:
        usql = 'update proxy set alive=0 where ip = %s'
        print(usql % ip)
        execute(usql, (ip,))


def loop(offset=-1200):
    threading.Thread(target=_loop, args=(offset, )).start()


def _loop(offset=-1200):
    while True:
        sql = 'select ip,port,alive from proxy where inTime < %s'
        data = select(sql, getTime(offset=offset))
        if data is not ():
            for i in data:
                t = threading.Thread(target=patrol, args=(i[0], i[1], i[2]))
                t.start()
        time.sleep(abs(offset))




if __name__ == '__main__':
    loop(-60)
