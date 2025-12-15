import random

def gen_vcode(length=6):
  return ''.join(random.choices('0123456789', k=length))