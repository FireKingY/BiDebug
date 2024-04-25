#!python3
import os
import random

e = int(os.getenv("TEST_ENV"))
if e  <= 33:
    if random.randint(1,10) > 5:
        exit(1)
exit(0)
