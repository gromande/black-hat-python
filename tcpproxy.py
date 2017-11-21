import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as ex:
        print("[!] Failed to listen on %s:%d. Error: %s" %
              (local_host, local_port, str(ex)))
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, client_addr = server.accept()
        print("[=>] Received incomming connection from %s:%d" %
              (remote_host, remote_port))

        proxy_thread = threading.Thread(target=proxy_handler,
            args=(client_socket,remote_host, remote_port, receive_first))

        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./tcpproxy.py [localhost] [localport] [remotehost] \
              [remoteport] [receive_first]")
        print("Example: ./tcpproxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if "True" = receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    #Connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    #Receive data from the remote end if neccesary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        #Send it to our response handler
        remote_buffer = response_handler(remote_buffer)

        #Send data to local client if required
        if len(remote_buffer):
            print("[<=] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    #Now lets loop and read from local, send to remote, read from remote,
    #send to local, and repeat
    while True:

        #Read from localhost
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[=>] Received %d bytes from localhost" % len(local_buffer))
            hexdump(local_buffer)

            #Send it to our request handler
            local_buffer = request_handler(local_buffer)

            #send off the data to the remote host
            remote_socket.send(local_buffer)
            print("[=>] Sent to remote")

        #receive back the response
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<=] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            #send to our response handler
            remote_buffer = response_handler(remote_buffer)

            #send response to local socket
            client_socket.send(remote_buffer)

            print("[<=] Sent to localhost")

        #If no more data in either side, close connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections")
            break



main()

