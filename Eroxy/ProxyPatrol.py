import pymysql
from Eroxy.ProxyFarmer import getTime
import threading
from Eroxy.IPJudger import HTTPJudger
from Eroxy.utils import execute
from Eroxy.utils import select


# TODO 不要直接删除，最好放在另一个表中。给第二次机会
def patrol(ip, port):
    _proxy = ip + ':' + port
    ret = HTTPJudger(_proxy)
    if ret is not None:
        usql = 'update proxy2 set delay=%s where ip=%s'
        execute(usql, (ret[1], ret[0][:ret[0].index(':')]))
    else:
        dsql = 'delete from proxy2 where ip=%s'
        execute(dsql, (ip, ))





if __name__ == '__main__':
    # # threads = []
    # conn = pymysql.connect(host='localhost', user='earayu', passwd='qwqwqw', db='Eroxy', port=3306,
    #                        charset='utf8')
    # cur = conn.cursor()  # 获取一个游标
    # sql = 'select ip,port from proxy2 where inTime < %s'
    # print(sql)
    # t = getTime()
    # cur.execute(sql, (t, ))
    # data = cur.fetchall()
    sql = 'select ip,port from proxy2 where inTime < %s'
    data = select(sql, getTime())
    if data is not ():
        for i in data:
            t = threading.Thread(target=patrol, args=(i[0], i[1]))
            # threads.append(t)
            t.start()
    # conn.commit()
    # cur.close()  # 关闭游标
    # conn.close()  # 释放数据库资源
