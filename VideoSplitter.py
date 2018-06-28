import socket

NUM = 4

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 1000))
s.sendto(b'', ('192.168.4.1', 1000))
s.sendto(b'', ('192.168.1.102', 1000))
while True:
    try:
        data, addr = s.recvfrom(4096*100)
        #print('Recebi')
        for i in range(0, NUM):
            try:
                s.sendto(data, ('127.0.0.1', 1001 +i))
            except:
                continue
    except:
        continue
