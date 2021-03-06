import socket, threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

#this is our client handling thread
def handle_client(client_socket):
    #print what the client sends
    request = client_socket.recv(1024)
    print("[*] Received: %s" % (request))

    #Send back a packet
    client_socket.send("ACK!".encode())

    client_socket.close()

while True:
    (client_socket,address) = server.accept()
    print("[*] Accepted connection from %s:%d" % (address[0], address[1]))

    #sping up client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
