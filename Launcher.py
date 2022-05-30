from multiprocessing.connection import Client
import sys, os
import time
import subprocess

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#program_location = r"C:\Users\ljiang\Documents\Programming Projects\ECN-Manager\build\exe.win-amd64-3.9"
    
#check for lock file
lock_loc = r"C:\ProgramData\ECN-Manager"

#print(sys.argv)
f = open(sys.argv[1],'r')
ecn = f.readline().strip()
#print(ecn)

lockfile = os.path.join(lock_loc,"ecn.lock")
program = os.path.join(program_location,"Manager.exe")
if not os.path.exists(lockfile):
    #print(f"launching: {program}")
    subprocess.Popen([program,ecn])
else:
    address = ('localhost', 6000)
    conn = Client(address, authkey=b'secret password')
    conn.send(ecn)
    conn.send('close')
    conn.close()