from multiprocessing.connection import Client
import sys

print(sys.argv)
f = open(sys.argv[1],'r')
ecn = f.readline().strip()
print(ecn)

address = ('localhost', 6000)
conn = Client(address, authkey=b'secret password')
conn.send(ecn)
conn.send('close')
# can also send arbitrary objects:
# conn.send(['a', 2.5, None, int, sum])
conn.close()