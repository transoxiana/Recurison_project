import sys
import os
import socket

#unix
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# server address
server_address = os.path.expanduser('~/local_chat_file')

#sock connect
try:
    sock.connect(server_address)
except socket.error as err:
    print(err)
    sys.exit(1)

# message
if len(sys.argv) != 2:
    print("make send message!")
    raise SyntaxError

text = sys.argv[1]
sock.sendall(text.encode())

try:
    while True:
        data = sock.recv(4098)
        data_str = data.decode('utf-8')

        if data:
            print("server responce: " + data_str)
            break
        else:
            break
        
finally:
    print('closing socket')
    sock.close()
