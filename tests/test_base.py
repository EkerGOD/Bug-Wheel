import json
import time

def test_range():
    for i in range(5):
        print(i)

now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))

now_new = time.mktime(time.strptime(now, "%Y-%m-%d-%H_%M_%S"))

print(now)
print(now_new)

time.sleep(10)

print(time.time())

# ten_time = time.mktime()


print(json.dumps(now))