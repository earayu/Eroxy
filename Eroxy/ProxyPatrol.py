import requests
import pymysql
from Eroxy.ProxyFarmer import getTime
import threading
import Eroxy.IPJudger
from Eroxy.IPJudger import HTTPJudger


def patrol(ip, port):
    _proxy = ip + ':' + port
    ret = HTTPJudger(_proxy)
    if ret is not None:
        conn = pymysql.connect(host='localhost', user='earayu', passwd='qwqwqw', db='Eroxy', port=3306,
                               charset='utf8')
        cur = conn.cursor()  # 获取一个游标
        sql = 'update proxy2 set delay=%s where ip=%s'
        print(ret)
        print(sql % (ret[1], ret[0][:ret[0].index(':')]))
        cur.execute(sql, (ret[1], ret[0][:ret[0].index(':')]))
        conn.commit()
        cur.close()  # 关闭游标
        conn.close()  # 释放数据库资源
    else:
        conn = pymysql.connect(host='localhost', user='earayu', passwd='qwqwqw', db='Eroxy', port=3306,
                               charset='utf8')
        cur = conn.cursor()  # 获取一个游标
        sql = 'delete from proxy2 where ip=%s'
        print(sql % ip)
        cur.execute(sql, (ip, ))
        conn.commit()
        cur.close()  # 关闭游标
        conn.close()  # 释放数据库资源






if __name__ == '__main__':
    # threads = []
    conn = pymysql.connect(host='localhost', user='earayu', passwd='qwqwqw', db='Eroxy', port=3306,
                           charset='utf8')
    cur = conn.cursor()  # 获取一个游标
    sql = 'select ip,port from proxy2 where inTime < %s'
    print(sql)
    t = getTime()
    cur.execute(sql, (t, ))
    data = cur.fetchall()
    if data is not ():
        for i in data:
            t = threading.Thread(target=patrol, args=(i[0], i[1]))
            # threads.append(t)
            t.start()
    # conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源
