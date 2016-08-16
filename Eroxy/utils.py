import pymysql
import time


# 获取形如 2016-05-23 13:01:21 的时间字符串
def getTime(format="%Y-%m-%d %H:%M:%S", offset=0):
    timeArray = time.localtime(int(time.time() + offset))
    formatTime = time.strftime(format, timeArray)
    return formatTime

def execute(sql, args, host='localhost', user='root', passwd='qwqwqw', db='Eroxy', port=3306, charset='utf8'):
    conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset)
    cur = conn.cursor()  # 获取一个游标
    print(sql % args)
    cur.execute(sql, args)
    conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源


def select(sql, args=None, host='localhost', user='root', passwd='qwqwqw', db='Eroxy', port=3306, charset='utf8'):
    conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset)
    cur = conn.cursor()  # 获取一个游标
    print(sql)
    cur.execute(sql, args)
    data = cur.fetchall()
    # conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源
    return data



if __name__ =='__main__':
    sql = 'select * from proxy2 where ip=%s'
    data = select(sql, '124.244.77.129')
    for i in data:
        print(i)
