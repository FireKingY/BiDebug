#!python3
import os
import random

e = int(os.getenv("TEST_ENV"))
print(e)
if e  <= 33:
    if random.randint(1,10) > 5:
        print("fail")
        exit(1)
print("pass")
exit(0)
