import re
import time

ip = '222.33.192.238 222.33.192.232'

r = re.compile(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)')
m = r.match(ip)

print(m.group())
print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))

