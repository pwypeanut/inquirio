import random

def generate_salt(length):
  salt_seq = "0123456789abcdef"
  salt = ""
  for i in range(0, 32):
    salt += salt_seq[random.randint(0, 15)]
  return salt