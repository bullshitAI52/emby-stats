import datetime
import os
import time

# Simulate TZ env var
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

now = datetime.datetime.now()
offset = now.astimezone().utcoffset().total_seconds() / 3600
print(f"Current TZ: {os.environ.get('TZ')}")
print(f"Detected Offset: {offset}")
