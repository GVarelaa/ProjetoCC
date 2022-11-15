import time

time1 = time.localtime()
time.sleep(1)
time2 = time.localtime()
print(time.mktime(time2)-time.mktime(time1))
