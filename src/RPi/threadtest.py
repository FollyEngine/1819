#!//usr/bin/python3

import threading

def stopthathorribleflashing():
  print("stop")

print("main")
#threading.Timer(4, stopthathorribleflashing)
threading.Timer(4, stopthathorribleflashing).start()
#t = threading.Timer(4, stopthathorribleflashing).start()
