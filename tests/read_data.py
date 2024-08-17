import time
import json
while True:
    with open('data.json', 'r') as file:
        data = json.load(file)
        print(data)
    # time.sleep(5)
