import socket
import os
from faker import Faker

# new socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# server path
server_address = os.path.expanduser('~/local_chat_file')

try:
    # when socketfile is, remove
    os.unlink(server_address)
except FileNotFoundError:
    pass

print('starting up on {}'.format(server_address))

#sock connect
sock.bind(server_address)

sock.listen(1)
while True:
    conection, client_address = sock.accept()
    try:
         print('conection from', client_address)
         
         while True:

            print("\nwaiting to receive message")

            data = conection.recv(4096)

            data_str = data.decode('utf-8')

            print('receive: ' + data_str)

            if data:
                # text
                fake = Faker('ja-JP')
                message = fake.text()

                conection.sendall(message.encode())

            else:
                break
            
    finally:
        print('clossing current conection')
        conection.close()
