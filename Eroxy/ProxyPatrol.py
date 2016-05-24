from Eroxy.ProxyFarmer import getTime
import threading
from Eroxy.IPJudger import HTTPJudger
from Eroxy.utils import execute
import time
from Eroxy.utils import select


# TODO 不要直接删除，最好放在另一个表中。给第二次机会
def patrol(ip, port, alive):
    _proxy = ip + ':' + port
    ret = HTTPJudger(_proxy)
    if ret is not None:
        usql = 'update proxy2 set delay=%s, alive=1 where ip=%s'
        execute(usql, (ret[1], ret[0][:ret[0].index(':')]))
    elif alive == 0:
        dsql = 'delete from proxy2 where ip=%s'
        execute(dsql, (ip, ))
    elif alive == 1:
        usql = 'update proxy2 set alive=0 where ip = %s'
        print(usql % ip)
        execute(usql, (ip,))


def loop(offset=-3600):
    while True:
        sql = 'select ip,port,alive from proxy2 where inTime < %s'
        data = select(sql, getTime(offset=offset))
        if data is not ():
            for i in data:
                t = threading.Thread(target=patrol, args=(i[0], i[1], i[2]))
                t.start()
        time.sleep(abs(offset))



if __name__ == '__main__':
    loop(-1200)
